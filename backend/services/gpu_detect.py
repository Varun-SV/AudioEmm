from config import settings


def has_cuda() -> bool:
    """Return True if CuPy + a CUDA device are available and USE_GPU != 'no'."""
    if settings.use_gpu == "no":
        return False
    try:
        import cupy as cp
        cp.zeros(1)   # force device initialisation
        return True
    except Exception:
        return False


_GPU_AVAILABLE: bool | None = None


def gpu_available() -> bool:
    global _GPU_AVAILABLE
    if _GPU_AVAILABLE is None:
        _GPU_AVAILABLE = has_cuda()
        if _GPU_AVAILABLE:
            print("[gpu] CUDA detected — FFT convolution will run on GPU.")
        else:
            print("[gpu] No CUDA device — using CPU FFT convolution.")
    return _GPU_AVAILABLE
