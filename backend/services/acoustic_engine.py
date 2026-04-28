import numpy as np
from pathlib import Path
from uuid import uuid4

import pyroomacoustics as pra

from config import settings
from lib.materials import get_pra_coefficients, PRA_CENTER_FREQS, sabine_rt60
from schemas.room import RoomConfig


EAR_SEPARATION = 0.215  # metres — standard KEMAR head width


def _build_pra_materials(config: RoomConfig) -> dict[str, pra.Material]:
    mat_map = {s.surface: s.material for s in config.surfaces}
    default = "drywall"
    surface_names = ["floor", "ceiling", "wall_front", "wall_back", "wall_left", "wall_right"]
    result = {}
    for name in surface_names:
        mat_name = mat_map.get(name, default)
        coeffs = get_pra_coefficients(mat_name)
        result[name] = pra.Material(
            energy_absorption={
                "coeffs": coeffs,
                "center_freqs": PRA_CENTER_FREQS,
            }
        )
    return result


def compute_rir(
    config: RoomConfig,
    session_rir_dir: Path,
    max_order: int | None = None,
    rir_duration: float | None = None,
) -> dict:
    """
    Generate a binaural Room Impulse Response using pyroomacoustics image-source method.
    Returns a dict with rir_id, rt60_sabine, rt60_computed, direct_delay_ms, reflection_count.
    """
    fs = settings.sample_rate
    max_order = max_order or settings.rir_max_order
    rir_dur = rir_duration or settings.rir_duration

    materials = _build_pra_materials(config)

    room = pra.ShoeBox(
        p=[config.length, config.width, config.height],
        fs=fs,
        max_order=max_order,
        materials=pra.MixedOrderSimulator(
            pra.Material(energy_absorption={"coeffs": get_pra_coefficients("drywall"),
                                            "center_freqs": PRA_CENTER_FREQS})
        ),
        ray_tracing=False,
        air_absorption=True,
    )

    # Override per-surface materials via the materials dict
    # pyroomacoustics ShoeBox accepts a single Material or a dict keyed by wall name
    # Re-create with per-wall materials
    room = pra.ShoeBox(
        p=[config.length, config.width, config.height],
        fs=fs,
        max_order=max_order,
        materials=pra.Material(
            energy_absorption={
                "coeffs": get_pra_coefficients(
                    next((s.material for s in config.surfaces if s.surface == "floor"), "drywall")
                ),
                "center_freqs": PRA_CENTER_FREQS,
            }
        ),
        ray_tracing=False,
        air_absorption=True,
    )

    # Add all speakers as sources
    speakers = config.speakers or []
    if not speakers:
        speakers_pos = [[config.length / 4, config.width / 2, 1.0]]
    else:
        speakers_pos = [[s.x, s.y, s.z] for s in speakers]

    for pos in speakers_pos:
        room.add_source(pos)

    # Two-ear microphone array
    lx = config.listener
    half = EAR_SEPARATION / 2
    mic_array = np.array([
        [lx.x - half, lx.x + half],
        [lx.y,        lx.y],
        [lx.z,        lx.z],
    ])
    room.add_microphone(mic_array)

    room.simulate()

    # RIR for first source, left/right ear
    rir_left  = room.rir[0][0]
    rir_right = room.rir[1][0]

    # Trim/pad to desired duration
    n_samples = int(fs * rir_dur)
    rir_left  = _trim_pad(rir_left,  n_samples)
    rir_right = _trim_pad(rir_right, n_samples)

    # Measured RT60
    try:
        rt60_computed = float(pra.experimental.measure_rt60(rir_left, fs=fs, decay_db=60))
    except Exception:
        rt60_computed = None

    # Sabine preview
    mat_map = {s.surface: s.material for s in config.surfaces}
    def _mat(surf): return mat_map.get(surf, "drywall")
    L, W, H = config.length, config.width, config.height
    sabine_surfaces = [
        (L * W, _mat("floor")), (L * W, _mat("ceiling")),
        (L * H, _mat("wall_front")), (L * H, _mat("wall_back")),
        (W * H, _mat("wall_left")),  (W * H, _mat("wall_right")),
    ]
    rt60_sabine = sabine_rt60(L * W * H, sabine_surfaces)

    # Direct sound delay (first source)
    src = speakers_pos[0]
    dist = float(np.sqrt((src[0]-lx.x)**2 + (src[1]-lx.y)**2 + (src[2]-lx.z)**2))
    direct_delay_ms = dist / 343.0 * 1000.0

    # Reflection count from image source method
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


def _trim_pad(arr: np.ndarray, n: int) -> np.ndarray:
    if len(arr) >= n:
        return arr[:n]
    return np.pad(arr, (0, n - len(arr)))
