"""
Acoustic absorption coefficients per material, migrated from the original simulator.py.
Values are dimensionless absorption coefficients (0=fully reflective, 1=fully absorptive).
"""

ABSORPTION_COEFFICIENTS: dict[str, dict[str, float]] = {
    "drywall":  {"low": 0.10,  "mid": 0.05,  "high": 0.04},
    "hardwood": {"low": 0.15,  "mid": 0.11,  "high": 0.10},
    "carpet":   {"low": 0.20,  "mid": 0.50,  "high": 0.60},
    "curtain":  {"low": 0.30,  "mid": 0.50,  "high": 0.70},
    "concrete": {"low": 0.01,  "mid": 0.015, "high": 0.02},
    "glass":    {"low": 0.05,  "mid": 0.03,  "high": 0.02},
}

# Map our three bands to octave-band center frequencies for pyroomacoustics
# low → 125 Hz, 250 Hz
# mid → 500 Hz, 1000 Hz, 2000 Hz
# high → 4000 Hz, 8000 Hz
PRA_CENTER_FREQS = [125, 250, 500, 1000, 2000, 4000, 8000]


def get_pra_coefficients(material: str) -> list[float]:
    """Return absorption coefficients at the 7 pyroomacoustics octave-band centres."""
    c = ABSORPTION_COEFFICIENTS[material]
    return [c["low"], c["low"], c["mid"], c["mid"], c["mid"], c["high"], c["high"]]


def sabine_rt60(volume: float, surfaces: list[tuple[float, str]]) -> float:
    """
    Sabine reverberation time estimate.
    surfaces: list of (area_m2, material_name) for each surface.
    Returns RT60 in seconds.
    """
    total_absorption = sum(
        area * ABSORPTION_COEFFICIENTS[mat]["mid"]
        for area, mat in surfaces
    )
    if total_absorption <= 0:
        return 0.0
    return 0.161 * volume / total_absorption
