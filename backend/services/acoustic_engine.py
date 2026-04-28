import numpy as np
from pathlib import Path
from uuid import uuid4

import pyroomacoustics as pra

from config import settings
from lib.materials import get_pra_coefficients, PRA_CENTER_FREQS, sabine_rt60
from schemas.room import RoomConfig


EAR_SEPARATION = 0.215  # metres — standard KEMAR head width

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


def _build_materials_dict(config: RoomConfig) -> dict[str, pra.Material]:
    """Build per-wall pyroomacoustics Material objects from surface config."""
    mat_map = {s.surface: s.material for s in config.surfaces}
    default = "drywall"
    result = {}
    for our_name, pra_name in _SURFACE_TO_PRA.items():
        mat_name = mat_map.get(our_name, default)
        result[pra_name] = pra.Material(
            energy_absorption={
                "coeffs": get_pra_coefficients(mat_name),
                "center_freqs": PRA_CENTER_FREQS,
            }
        )
    return result


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

    materials = _build_materials_dict(config)

    room = pra.ShoeBox(
        p=[config.length, config.width, config.height],
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

    # Add all speakers as sources
    speakers = config.speakers or []
    if not speakers:
        speakers_pos = [[config.length / 4, config.width / 2, 1.0]]
    else:
        speakers_pos = [[s.x, s.y, s.z] for s in speakers]

    for pos in speakers_pos:
        room.add_source(pos)

    # Binaural two-ear microphone array at listener position
    lx = config.listener
    half = EAR_SEPARATION / 2
    mic_array = np.array([
        [lx.x - half, lx.x + half],
        [lx.y,        lx.y],
        [lx.z,        lx.z],
    ])
    room.add_microphone(mic_array)

    room.simulate()

    # RIR: mic 0 = left ear, mic 1 = right ear, source 0
    rir_left  = room.rir[0][0]
    rir_right = room.rir[1][0]

    # Trim/pad to desired duration
    n_samples = int(fs * rir_dur)
    rir_left  = _trim_pad(rir_left,  n_samples)
    rir_right = _trim_pad(rir_right, n_samples)

    # Measure RT60 from computed RIR
    try:
        rt60_computed = float(pra.experimental.measure_rt60(rir_left, fs=fs, decay_db=60))
    except Exception:
        rt60_computed = None

    # Sabine estimate for comparison
    mat_map = {s.surface: s.material for s in config.surfaces}
    def _mat(surf): return mat_map.get(surf, "drywall")
    L, W, H = config.length, config.width, config.height
    sabine_surfaces = [
        (L * W, _mat("floor")), (L * W, _mat("ceiling")),
        (L * H, _mat("wall_front")), (L * H, _mat("wall_back")),
        (W * H, _mat("wall_left")),  (W * H, _mat("wall_right")),
    ]
    rt60_sabine = sabine_rt60(L * W * H, sabine_surfaces)

    # Direct sound delay
    src = speakers_pos[0]
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

    materials = _build_materials_dict(config)
    room = pra.ShoeBox(
        p=[config.length, config.width, config.height],
        fs=fs,
        max_order=settings.rir_max_order_preview,
        materials=materials,
        ray_tracing=False,
        air_absorption=False,
    )

    speakers = config.speakers or []
    speakers_pos = [[s.x, s.y, s.z] for s in speakers] if speakers else [[config.length / 4, config.width / 2, 1.0]]
    for pos in speakers_pos:
        room.add_source(pos)

    lx = config.listener
    half = EAR_SEPARATION / 2
    room.add_microphone(np.array([
        [lx.x - half, lx.x + half],
        [lx.y,        lx.y],
        [lx.z,        lx.z],
    ]))
    room.simulate()

    rir_left = _trim_pad(room.rir[0][0], int(fs * rir_dur))

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
    dist = float(np.sqrt((src[0]-lx.x)**2 + (src[1]-lx.y)**2 + (src[2]-lx.z)**2))

    return {
        "rt60_sabine": round(rt60_sabine, 3),
        "rt60_computed": round(rt60_computed, 3) if rt60_computed else None,
        "direct_delay_ms": round(dist / 343.0 * 1000.0, 2),
        "reflection_count": len(room.sources[0].images.T) - 1,
    }


def _trim_pad(arr: np.ndarray, n: int) -> np.ndarray:
    if len(arr) >= n:
        return arr[:n]
    return np.pad(arr, (0, n - len(arr)))
