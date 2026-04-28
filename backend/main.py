import asyncio
import ssl
import urllib.request
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text

from api.router import api_router
from config import settings
from db.base import engine
from db.models import Base
from services.session_manager import session_manager


def _download_hrtf():
    """Download MIT KEMAR SOFA file if not already present."""
    hrtf_path = settings.hrtf_path
    if hrtf_path.exists():
        return
    hrtf_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[startup] Downloading HRTF dataset to {hrtf_path} …")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        urllib.request.urlretrieve(settings.hrtf_url, str(hrtf_path))
        print("[startup] HRTF download complete.")
    except Exception as exc:
        print(f"[startup] HRTF download failed ({exc}). Binaural rendering will be skipped.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist. Use a PG advisory lock so that when uvicorn starts
    # multiple workers they don't race on CREATE TABLE and hit a duplicate-key
    # error on pg_type_typname_nsp_index.
    async with engine.begin() as conn:
        await conn.execute(text("SELECT pg_advisory_lock(8675309)"))
        try:
            await conn.run_sync(Base.metadata.create_all)
        finally:
            await conn.execute(text("SELECT pg_advisory_unlock(8675309)"))

    # Download HRTF dataset on first startup (run in thread so it doesn't block)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _download_hrtf)

    # Ensure library dir exists
    settings.library_dir.mkdir(parents=True, exist_ok=True)

    # Start background session cleanup loop
    task = asyncio.create_task(session_manager.run_cleanup_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AudioEmm API", version="2.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = (
    ["*"]
    if settings.allowed_origins == "*"
    else [o.strip() for o in settings.allowed_origins.split(",")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
