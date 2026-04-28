import json
import shutil
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from config import settings


class Session:
    def __init__(self, session_id: str, base_dir: Path):
        self.session_id = session_id
        self.path = base_dir / session_id
        self.uploads = self.path / "uploads"
        self.rir = self.path / "rir"
        self.results = self.path / "results"
        self.eq_profiles = self.path / "eq_profiles"
        self.models = self.path / "models"

    @property
    def metadata_path(self) -> Path:
        return self.path / "metadata.json"

    @property
    def room_config_path(self) -> Path:
        return self.path / "room_config.json"

    def touch(self):
        meta = self._read_meta()
        meta["last_accessed"] = datetime.now(timezone.utc).isoformat()
        self.metadata_path.write_text(json.dumps(meta))

    def _read_meta(self) -> dict:
        if self.metadata_path.exists():
            return json.loads(self.metadata_path.read_text())
        return {}

    def to_dict(self) -> dict:
        meta = self._read_meta()
        return {
            "session_id": self.session_id,
            "created_at": meta.get("created_at"),
            "expires_at": meta.get("expires_at"),
            "has_audio": any(self.uploads.glob("*.wav")) if self.uploads.exists() else False,
            "has_result": any(self.results.glob("*.wav")) if self.results.exists() else False,
        }


class SessionManager:
    def __init__(self):
        self.base_dir = settings.sessions_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, dict] = {}  # job_id → {status, result, error}

    def create_session(self) -> Session:
        session_id = uuid4().hex
        session = Session(session_id, self.base_dir)
        for d in (session.path, session.uploads, session.rir, session.results,
                  session.eq_profiles, session.models):
            d.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        meta = {
            "session_id": session_id,
            "created_at": now.isoformat(),
            "last_accessed": now.isoformat(),
            "expires_at": (now + timedelta(seconds=settings.session_ttl)).isoformat(),
        }
        session.metadata_path.write_text(json.dumps(meta))
        return session

    def get_session(self, session_id: str) -> Session:
        session = Session(session_id, self.base_dir)
        if not session.path.exists():
            raise KeyError(session_id)
        session.touch()
        return session

    def delete_session(self, session_id: str):
        session = Session(session_id, self.base_dir)
        if session.path.exists():
            shutil.rmtree(session.path)

    def set_job(self, job_id: str, status: str, result: dict | None = None, error: str | None = None):
        self._jobs[job_id] = {"status": status, "result": result, "error": error}

    def get_job(self, job_id: str) -> dict:
        return self._jobs.get(job_id, {"status": "not_found", "result": None, "error": None})

    async def cleanup_expired(self) -> int:
        removed = 0
        now = datetime.now(timezone.utc)
        for session_dir in self.base_dir.iterdir():
            if not session_dir.is_dir():
                continue
            meta_file = session_dir / "metadata.json"
            if not meta_file.exists():
                shutil.rmtree(session_dir)
                removed += 1
                continue
            try:
                meta = json.loads(meta_file.read_text())
                last = datetime.fromisoformat(meta.get("last_accessed", ""))
                if (now - last).total_seconds() > settings.session_ttl:
                    shutil.rmtree(session_dir)
                    removed += 1
            except Exception:
                pass
        return removed

    async def run_cleanup_loop(self):
        while True:
            await asyncio.sleep(settings.cleanup_interval)
            await self.cleanup_expired()


session_manager = SessionManager()
