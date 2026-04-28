"""
Full audio processing pipeline:
dry audio → RIR convolution → HRTF binauralization → optional EQ → stereo WAV
"""
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve

from config import settings
from services.eq_service import apply_fft_eq, load_profile


TARGET_SR = settings.sample_rate


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    """Load audio file, convert to mono float32, resample to TARGET_SR."""
    import librosa
    audio, sr = librosa.load(str(path), sr=TARGET_SR, mono=True)
    return audio.astype(np.float32), sr


def load_rir(rir_path: Path) -> tuple[np.ndarray, np.ndarray, int]:
    data = np.load(str(rir_path))
    return data["left"].astype(np.float32), data["right"].astype(np.float32), int(data["fs"])


def _peak_normalize(arr: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(arr))
    if peak < 1e-9:
        return arr
    return arr / peak * 0.95


def process_audio(
    dry_path: Path,
    rir_path: Path,
    output_path: Path,
    speaker_pos: tuple[float, float, float] | None = None,
    listener_pos: tuple[float, float, float] | None = None,
    eq_profile_path: Path | None = None,
    use_hrtf: bool = True,
) -> float:
    """
    Convolve dry audio with binaural RIR, optionally apply HRTF and EQ.
    Writes a 32-bit float stereo WAV to output_path.
    Returns duration in seconds.
    """
    dry, sr = load_audio(dry_path)
    rir_l, rir_r, rir_sr = load_rir(rir_path)

    if use_hrtf and speaker_pos and listener_pos:
        try:
            from services.hrtf_processor import HRTFProcessor
            hrtf = HRTFProcessor.get()
            rir_l, rir_r = hrtf.binauralize_rir(rir_l, rir_r, speaker_pos, listener_pos)
        except Exception:
            # HRTF not available (e.g. SOFA file missing) — continue without it
            pass

    wet_l = fftconvolve(dry, rir_l, mode="full").astype(np.float32)
    wet_r = fftconvolve(dry, rir_r, mode="full").astype(np.float32)

    if eq_profile_path and eq_profile_path.exists():
        import json
        profile = json.loads(eq_profile_path.read_text())
        eq_freqs = np.array(profile["frequencies"], dtype=np.float32)
        eq_db = np.array(profile["db_values"], dtype=np.float32)
        wet_l = apply_fft_eq(wet_l, eq_freqs, eq_db, sr)
        wet_r = apply_fft_eq(wet_r, eq_freqs, eq_db, sr)

    # Align lengths
    length = max(len(wet_l), len(wet_r))
    if len(wet_l) < length:
        wet_l = np.pad(wet_l, (0, length - len(wet_l)))
    if len(wet_r) < length:
        wet_r = np.pad(wet_r, (0, length - len(wet_r)))

    stereo = np.stack([_peak_normalize(wet_l), _peak_normalize(wet_r)], axis=1)
    sf.write(str(output_path), stereo, sr, subtype="FLOAT")
    return length / sr
