from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sessions_dir: Path = Path("/data/sessions")
    hrtf_path: Path = Path("/app/data/hrtf/MIT_KEMAR.sofa")
    session_ttl: int = 3600          # seconds
    max_upload_mb: int = 200
    cleanup_interval: int = 900      # 15 min
    sample_rate: int = 48000
    rir_max_order: int = 3
    rir_duration: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
