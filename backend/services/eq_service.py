"""
EQ / Frequency-Response service.
Migrated and improved from code/lib/equalizer/device_equalizer.py.

Phase-preserving FFT EQ: multiply magnitude, preserve phase angle.
"""
import csv
import io
import json
from pathlib import Path
from uuid import uuid4

import numpy as np
from scipy.interpolate import interp1d


def parse_fr_file(content: bytes, filename: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Parse a headphone/speaker FR measurement file (CSV or space-separated TXT).
    Expected columns: frequency_hz, db_value  (with or without header)
    Returns (frequencies, db_values) as float32 arrays sorted by frequency.
    """
    text = content.decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text))
    freqs, dbs = [], []
    for row in reader:
        row = [c.strip() for c in row if c.strip()]
        if len(row) < 2:
            # Try space-split
            parts = row[0].split() if row else []
            if len(parts) >= 2:
                row = parts
            else:
                continue
        try:
            f = float(row[0])
            d = float(row[1])
            freqs.append(f)
            dbs.append(d)
        except ValueError:
            continue  # skip header rows

    if not freqs:
        raise ValueError("No frequency/dB pairs found in FR file")

    freqs = np.array(freqs, dtype=np.float32)
    dbs = np.array(dbs, dtype=np.float32)
    order = np.argsort(freqs)
    return freqs[order], dbs[order]


def apply_fft_eq(
    audio: np.ndarray,
    eq_freqs: np.ndarray,
    eq_db: np.ndarray,
    sample_rate: int,
) -> np.ndarray:
    """
    Apply a frequency-response curve to an audio signal using FFT.
    Phase-preserving: only the magnitude is scaled, phase angles are unchanged.
    """
    n = len(audio)
    spectrum = np.fft.rfft(audio)
    fft_freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)

    # Interpolate EQ curve onto FFT bins (linear interp, clamp extrapolation)
    interp = interp1d(
        eq_freqs, eq_db,
        kind="linear",
        bounds_error=False,
        fill_value=(eq_db[0], eq_db[-1]),
    )
    eq_at_bins = interp(fft_freqs).astype(np.float32)
    gain_linear = 10.0 ** (eq_at_bins / 20.0)

    # Scale magnitude, preserve phase
    mag = np.abs(spectrum)
    phase = np.angle(spectrum)
    spectrum_eq = (mag * gain_linear) * np.exp(1j * phase)
    return np.fft.irfft(spectrum_eq, n=n).astype(np.float32)


def save_profile(session_eq_dir: Path, name: str, freqs: np.ndarray, dbs: np.ndarray) -> str:
    profile_id = uuid4().hex
    data = {
        "profile_id": profile_id,
        "name": name,
        "frequencies": freqs.tolist(),
        "db_values": dbs.tolist(),
    }
    (session_eq_dir / f"{profile_id}.json").write_text(json.dumps(data))
    return profile_id


def load_profile(session_eq_dir: Path, profile_id: str) -> dict:
    path = session_eq_dir / f"{profile_id}.json"
    if not path.exists():
        raise KeyError(profile_id)
    return json.loads(path.read_text())


def list_profiles(session_eq_dir: Path) -> list[dict]:
    profiles = []
    for f in session_eq_dir.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            profiles.append({"profile_id": d["profile_id"], "name": d["name"]})
        except Exception:
            pass
    return sorted(profiles, key=lambda x: x["name"])
