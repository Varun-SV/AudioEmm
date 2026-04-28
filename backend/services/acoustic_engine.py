import numpy as np
from pathlib import Path
from uuid import uuid4

import pyroomacoustics as pra

from config import settings
from lib.materials import get_pra_coefficients, PRA_CENTER_FREQS, sabine_rt60
from schemas.room import RoomConfig


EAR_SEPARATION = 0.215  # metres — standard KEMAR head width
WALL_MARGIN = 0.1       # minimum distance from any wall for sources / mics

# pyroomacoustics wall name mapping for ShoeBox
# ShoeBox wall order: [west, east, south, north, floor, ceiling]
_SURFACE_TO_PRA = {
    "wall_left":  "west",
    "wall_right": "east",
    "wall_front": "south",
    "wall_back":  "north",
    "floor":      "floor",
    "ceiling":    "ceiling",
}

# Absorption coefficients for room objects (blended into wall material by coverage)
_OBJECT_ABSORPTION = {
    "curtain":   {"low": 0.35, "mid": 0.55, "high": 0.75},
    "window":    {"low": 0.05, "mid": 0.03, "high": 0.02},
    "door":      {"low": 0.14, "mid": 0.10, "high": 0.08},
    "sofa":      {"low": 0.35, "mid": 0.55, "high": 0.65},
    "bookshelf": {"low": 0.25, "mid": 0.40, "high": 0.50},
    "desk":      {"low": 0.10, "mid": 0.15, "high": 0.20},
}

# Wall area calculation helpers
def _wall_area(surface: str, L: float, W: float, H: float) -> float:
    if surface in ("floor", "ceiling"):
        return L * W
    if surface in ("wall_front", "wall_back"):
        return L * H
    return W * H  # wall_left, wall_right


def _clamp_pos(pos: list, L: float, W: float, H: float) -> list:
    return [
        max(WALL_MARGIN, min(pos[0], L - WALL_MARGIN)),
        max(WALL_MARGIN, min(pos[1], W - WALL_MARGIN)),
        max(WALL_MARGIN, min(pos[2], H - WALL_MARGIN)),
    ]


def _clamp_listener(lx, L: float, W: float, H: float):
    """Clamp listener so both ears stay inside walls."""
    half = EAR_SEPARATION / 2
    cx = max(WALL_MARGIN + half, min(lx.x, L - WALL_MARGIN - half))
    cy = max(WALL_MARGIN, min(lx.y, W - WALL_MARGIN))
    cz = max(WALL_MARGIN, min(lx.z, H - WALL_MARGIN))
    return cx, cy, cz


def _build_materials_dict(config: RoomConfig) -> dict[str, pra.Material]:
    """Build per-wall pyroomacoustics Material objects, blending in any room objects."""
    L, W, H = config.length, config.width, config.height
    mat_map = {s.surface: s.material for s in config.surfaces}
    default = "drywall"

    # Compute base 7-band coefficients per pra wall name
    base_coeffs: dict[str, list[float]] = {}
    for our_name, pra_name in _SURFACE_TO_PRA.items():
        mat_name = mat_map.get(our_name, default)
        base_coeffs[pra_name] = list(get_pra_coefficients(mat_name))

    # Blend room-object absorption into the wall it sits on
    room_objects = getattr(config, "room_objects", None) or []
    if room_objects:
        # Accumulate coverage fractions per our_name
        coverage: dict[str, float] = {}
        obj_blended: dict[str, list[float]] = {}

        for obj in room_objects:
            obj_type = obj.type
            if obj_type not in _OBJECT_ABSORPTION:
                continue
            our_name = obj.wall_surface
            pra_name = _SURFACE_TO_PRA.get(our_name)
            if pra_name is None:
                continue

            area = _wall_area(our_name, L, W, H)
            frac = min(0.95, (obj.width * obj.height) / area) if area > 0 else 0.0

            prev_frac = coverage.get(our_name, 0.0)
            new_frac = min(0.95, prev_frac + frac)
            coverage[our_name] = new_frac

            # Weighted blend of base + all objects; accumulate per band
            o_abs = _OBJECT_ABSORPTION[obj_type]
            o_coeffs = [o_abs["low"], o_abs["low"], o_abs["mid"], o_abs["mid"],
                        o_abs["mid"], o_abs["high"], o_abs["high"]]
            if our_name not in obj_blended:
                obj_blended[our_name] = list(base_coeffs[pra_name])

            # Incrementally blend: new = prev * (1-added_frac) + obj * added_frac
            added_frac = new_frac - prev_frac
            for i in range(7):
                obj_blended[our_name][i] = (
                    obj_blended[our_name][i] * (1 - added_frac) + o_coeffs[i] * added_frac
                )

        # Apply blended coefficients back
        for our_name, pra_name in _SURFACE_TO_PRA.items():
            if our_name in obj_blended:
                base_coeffs[pra_name] = obj_blended[our_name]

    result = {}
    for pra_name, coeffs in base_coeffs.items():
        result[pra_name] = pra.Material(
            energy_absorption={
                "coeffs": coeffs,
                "center_freqs": PRA_CENTER_FREQS,
            }
        )
    return result


def _trim_pad(arr, n: int) -> np.ndarray:
    if arr is None or len(arr) == 0:
        return np.zeros(n)
    if len(arr) >= n:
        return arr[:n]
    return np.pad(arr, (0, n - len(arr)))


def _build_room(config: RoomConfig, fs: int, max_order: int,
                ray_tracing: bool, rir_dur: float) -> tuple:
    """Build ShoeBox, add sources and mics. Returns (room, speakers_pos, mic_array)."""
    L, W, H = config.length, config.width, config.height
    materials = _build_materials_dict(config)

    room = pra.ShoeBox(
        p=[L, W, H],
        fs=fs,
        max_order=max_order,
        materials=materials,
        ray_tracing=ray_tracing,
        air_absorption=True,
    )
    if ray_tracing:
        room.set_ray_tracing(
            n_rays=10_000,
            energy_thres=1e-7,
            time_thres=rir_dur,
            hist_bin_size=0.004,
        )

    speakers = config.speakers or []
    if not speakers:
        speakers_pos = [_clamp_pos([L / 4, W / 2, 1.0], L, W, H)]
    else:
        speakers_pos = [_clamp_pos([s.x, s.y, s.z], L, W, H) for s in speakers]

    for pos in speakers_pos:
        room.add_source(pos)

    cx, cy, cz = _clamp_listener(config.listener, L, W, H)
    half = EAR_SEPARATION / 2
    mic_array = np.array([
        [cx - half, cx + half],
        [cy,        cy],
        [cz,        cz],
    ])
    room.add_microphone(mic_array)

    return room, speakers_pos, mic_array


def compute_rir(
    config: RoomConfig,
    session_rir_dir: Path,
    max_order: int | None = None,
    rir_duration: float | None = None,
    ray_tracing: bool = True,
) -> dict:
    """
    Generate a binaural Room Impulse Response using pyroomacoustics.
    Uses hybrid ISM + ray tracing for accurate early and late reflections.
    Returns dict with rir_id, rt60_sabine, rt60_computed, direct_delay_ms, reflection_count.
    """
    fs = settings.sample_rate
    max_order = max_order if max_order is not None else settings.rir_max_order
    rir_dur = rir_duration if rir_duration is not None else settings.rir_duration

    room, speakers_pos, mic_array = _build_room(config, fs, max_order, ray_tracing, rir_dur)
    room.simulate()

    rir_left  = room.rir[0][0]
    rir_right = room.rir[1][0]

    # Fallback to ISM-only if ray tracing produced None RIRs
    if (rir_left is None or rir_right is None) and ray_tracing:
        room2, speakers_pos, mic_array = _build_room(
            config, fs, max_order, False, rir_dur
        )
        room2.simulate()
        rir_left  = room2.rir[0][0]
        rir_right = room2.rir[1][0]
        room = room2  # use room2 for reflection_count

    n_samples = int(fs * rir_dur)
    rir_left  = _trim_pad(rir_left,  n_samples)
    rir_right = _trim_pad(rir_right, n_samples)

    try:
        rt60_computed = float(pra.experimental.measure_rt60(rir_left, fs=fs, decay_db=60))
    except Exception:
        rt60_computed = None

    mat_map = {s.surface: s.material for s in config.surfaces}
    def _mat(surf): return mat_map.get(surf, "drywall")
    L, W, H = config.length, config.width, config.height
    sabine_surfaces = [
        (L * W, _mat("floor")), (L * W, _mat("ceiling")),
        (L * H, _mat("wall_front")), (L * H, _mat("wall_back")),
        (W * H, _mat("wall_left")),  (W * H, _mat("wall_right")),
    ]
    rt60_sabine = sabine_rt60(L * W * H, sabine_surfaces)

    src = speakers_pos[0]
    lx = config.listener
    dist = float(np.sqrt((src[0]-lx.x)**2 + (src[1]-lx.y)**2 + (src[2]-lx.z)**2))
    direct_delay_ms = dist / 343.0 * 1000.0

    reflection_count = len(room.sources[0].images.T) - 1

    rir_id = uuid4().hex
    rir_path = session_rir_dir / f"{rir_id}.npz"
    np.savez(str(rir_path), left=rir_left, right=rir_right, fs=fs)

    return {
        "rir_id": rir_id,
        "rt60_sabine": round(rt60_sabine, 3),
        "rt60_computed": round(rt60_computed, 3) if rt60_computed else None,
        "direct_delay_ms": round(direct_delay_ms, 2),
        "reflection_count": reflection_count,
    }


def compute_rir_preview(config: RoomConfig) -> dict:
    """
    Fast synchronous preview: ISM order 1, no ray tracing, no file output.
    Returns RT60 estimate and basic reflection stats inline (~50-150 ms).
    """
    fs = settings.sample_rate
    rir_dur = 0.5
    L, W, H = config.length, config.width, config.height

    materials = _build_materials_dict(config)
    room = pra.ShoeBox(
        p=[L, W, H],
        fs=fs,
        max_order=settings.rir_max_order_preview,
        materials=materials,
        ray_tracing=False,
        air_absorption=False,
    )

    speakers = config.speakers or []
    speakers_pos = (
        [_clamp_pos([s.x, s.y, s.z], L, W, H) for s in speakers]
        if speakers
        else [_clamp_pos([L / 4, W / 2, 1.0], L, W, H)]
    )
    for pos in speakers_pos:
        room.add_source(pos)

    cx, cy, cz = _clamp_listener(config.listener, L, W, H)
    half = EAR_SEPARATION / 2
    room.add_microphone(np.array([
        [cx - half, cx + half],
        [cy,        cy],
        [cz,        cz],
    ]))
    room.simulate()

    rir_left = _trim_pad(room.rir[0][0], int(fs * rir_dur))

    try:
        rt60_computed = float(pra.experimental.measure_rt60(rir_left, fs=fs, decay_db=60))
    except Exception:
        rt60_computed = None

    mat_map = {s.surface: s.material for s in config.surfaces}
    def _mat(surf): return mat_map.get(surf, "drywall")
    sabine_surfaces = [
        (L * W, _mat("floor")), (L * W, _mat("ceiling")),
        (L * H, _mat("wall_front")), (L * H, _mat("wall_back")),
        (W * H, _mat("wall_left")),  (W * H, _mat("wall_right")),
    ]
    rt60_sabine = sabine_rt60(L * W * H, sabine_surfaces)

    src = speakers_pos[0]
    lx = config.listener
    dist = float(np.sqrt((src[0]-lx.x)**2 + (src[1]-lx.y)**2 + (src[2]-lx.z)**2))

    return {
        "rt60_sabine": round(rt60_sabine, 3),
        "rt60_computed": round(rt60_computed, 3) if rt60_computed else None,
        "direct_delay_ms": round(dist / 343.0 * 1000.0, 2),
        "reflection_count": len(room.sources[0].images.T) - 1,
    }
