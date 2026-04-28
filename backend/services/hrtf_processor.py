import numpy as np
from scipy.signal import fftconvolve

from config import settings


class HRTFProcessor:
    _instance: "HRTFProcessor | None" = None

    def __init__(self, sofa_path: str | None = None):
        import sofar as sf
        path = sofa_path or str(settings.hrtf_path)
        self.sofa = sf.read_sofa(path)
        positions = self.sofa.SourcePosition  # (N, 3): [az_deg, el_deg, r_m]
        self._az = np.radians(positions[:, 0])
        self._el = np.radians(positions[:, 1])

    @classmethod
    def get(cls) -> "HRTFProcessor":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_hrir(self, azimuth_deg: float, elevation_deg: float) -> tuple[np.ndarray, np.ndarray]:
        """Return (hrir_left, hrir_right) for the nearest measured direction."""
        az = np.radians(azimuth_deg)
        el = np.radians(elevation_deg)
        # Great-circle angular distance
        dist = np.arccos(np.clip(
            np.sin(el) * np.sin(self._el) + np.cos(el) * np.cos(self._el) * np.cos(az - self._az),
            -1.0, 1.0,
        ))
        idx = int(np.argmin(dist))
        ir = self.sofa.Data.IR[idx]  # shape (2, samples)
        return ir[0].astype(np.float32), ir[1].astype(np.float32)

    @staticmethod
    def speaker_direction(
        speaker: tuple[float, float, float],
        listener: tuple[float, float, float],
    ) -> tuple[float, float]:
        """
        Compute azimuth and elevation of speaker as seen from listener.
        Returns (azimuth_deg, elevation_deg) in SOFA convention:
          azimuth:   0° = front, 90° = left, 180° = back, 270° = right
          elevation: 0° = horizontal, +90° = straight up
        """
        dx = speaker[0] - listener[0]
        dy = speaker[1] - listener[1]
        dz = speaker[2] - listener[2]
        dist_horiz = np.sqrt(dx ** 2 + dy ** 2)
        azimuth = float(np.degrees(np.arctan2(dy, dx)) % 360)
        elevation = float(np.degrees(np.arctan2(dz, dist_horiz + 1e-9)))
        return azimuth, elevation

    def binauralize_rir(
        self,
        rir_left: np.ndarray,
        rir_right: np.ndarray,
        speaker_pos: tuple[float, float, float],
        listener_pos: tuple[float, float, float],
    ) -> tuple[np.ndarray, np.ndarray]:
        az, el = self.speaker_direction(speaker_pos, listener_pos)
        hrir_l, hrir_r = self.get_hrir(az, el)
        out_l = fftconvolve(rir_left,  hrir_l, mode="full").astype(np.float32)
        out_r = fftconvolve(rir_right, hrir_r, mode="full").astype(np.float32)
        return out_l, out_r
