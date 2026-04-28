from fastapi import APIRouter

from api.sessions import router as sessions_router
from api.room import router as room_router
from api.simulation import router as simulation_router
from api.audio import router as audio_router
from api.eq import router as eq_router

api_router = APIRouter(prefix="/api")
api_router.include_router(sessions_router)
api_router.include_router(room_router)
api_router.include_router(simulation_router)
api_router.include_router(audio_router)
api_router.include_router(eq_router)
