from fastapi import APIRouter

from api.sessions import router as sessions_router
from api.room import router as room_router
from api.simulation import router as simulation_router
from api.audio import router as audio_router
from api.eq import router as eq_router
from api.auth import router as auth_router
from api.library import router as library_router
from api.models import router as models_router

api_router = APIRouter(prefix="/api")
api_router.include_router(sessions_router)
api_router.include_router(room_router)
api_router.include_router(simulation_router)
api_router.include_router(audio_router)
api_router.include_router(eq_router)
api_router.include_router(auth_router)
api_router.include_router(library_router)
api_router.include_router(models_router)
