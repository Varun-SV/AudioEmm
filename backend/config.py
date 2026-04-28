from pathlib import Path
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Storage
    sessions_dir: Path = Path("/data/sessions")
    library_dir: Path = Path("/data/library")
    hrtf_path: Path = Path("/app/data/hrtf/MIT_KEMAR.sofa")
    hrtf_url: str = "https://sofacoustics.org/data/database/mit/MIT_KEMAR_large_pinna.sofa"

    # Session
    session_ttl: int = 3600
    max_upload_mb: int = 200
    cleanup_interval: int = 900

    # Audio / simulation
    sample_rate: int = 48000
    rir_max_order: int = 6
    rir_max_order_preview: int = 1
    rir_duration: float = 1.0
    use_gpu: str = "auto"

    # Database
    database_url: str = "postgresql+asyncpg://audioemm:changeme@postgres:5432/audioemm"

    # Auth
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    oauth_redirect_base: str = "http://localhost"

    # CORS
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
