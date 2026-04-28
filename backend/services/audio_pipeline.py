"""
Full audio processing pipeline:
dry audio → RIR convolution → HRTF binauralization → optional EQ → stereo WAV
GPU-accelerated FFT convolution is used automatically when CUDA is available.
"""
from pathlib import Path

import numpy as np
import soundfile as sf

from config import settings
from services.eq_service import apply_fft_eq
from services.gpu_detect import gpu_available


TARGET_SR = settings.sample_rate


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    import librosa
    audio, sr = librosa.load(str(path), sr=TARGET_SR, mono=True)
    return audio.astype(np.float32), sr


def load_rir(rir_path: Path) -> tuple[np.ndarray, np.ndarray, int]:
    data = np.load(str(rir_path))
    return data["left"].astype(np.float32), data["right"].astype(np.float32), int(data["fs"])


def _fftconvolve(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FFT convolution, GPU-accelerated when CUDA is available."""
    if gpu_available():
        try:
            import cupy as cp
            n = len(a) + len(b) - 1
            fa = cp.fft.rfft(cp.asarray(a), n=n)
            fb = cp.fft.rfft(cp.asarray(b), n=n)
            result = cp.fft.irfft(fa * fb, n=n)
            return cp.asnumpy(result).astype(np.float32)
        except Exception:
            pass
    from scipy.signal import fftconvolve
    return fftconvolve(a, b, mode="full").astype(np.float32)


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
    rir_l, rir_r, _ = load_rir(rir_path)

    if use_hrtf and speaker_pos and listener_pos:
        try:
            from services.hrtf_processor import HRTFProcessor
            hrtf = HRTFProcessor.get()
            rir_l, rir_r = hrtf.binauralize_rir(rir_l, rir_r, speaker_pos, listener_pos)
        except Exception:
            pass  # HRTF file missing — continue with room-only RIR

    wet_l = _fftconvolve(dry, rir_l)
    wet_r = _fftconvolve(dry, rir_r)

    if eq_profile_path and eq_profile_path.exists():
        import json
        profile = json.loads(eq_profile_path.read_text())
        eq_freqs = np.array(profile["frequencies"], dtype=np.float32)
        eq_db    = np.array(profile["db_values"],   dtype=np.float32)
        wet_l = apply_fft_eq(wet_l, eq_freqs, eq_db, sr)
        wet_r = apply_fft_eq(wet_r, eq_freqs, eq_db, sr)

    length = max(len(wet_l), len(wet_r))
    wet_l = np.pad(wet_l, (0, length - len(wet_l)))
    wet_r = np.pad(wet_r, (0, length - len(wet_r)))

    stereo = np.stack([_peak_normalize(wet_l), _peak_normalize(wet_r)], axis=1)
    sf.write(str(output_path), stereo, sr, subtype="FLOAT")
    return length / sr
