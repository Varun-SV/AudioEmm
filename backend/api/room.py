import json

from fastapi import APIRouter, HTTPException

from schemas.room import RoomConfig, ROOM_PRESETS
from services.session_manager import session_manager
from lib.materials import sabine_rt60

router = APIRouter(prefix="/sessions/{session_id}/room", tags=["room"])


def _rt60_preview(config: RoomConfig) -> float:
    mat_map = {s.surface: s.material for s in config.surfaces}
    default_mat = "drywall"
    L, W, H = config.length, config.width, config.height
    surfaces = [
        (L * W, mat_map.get("floor", default_mat)),
        (L * W, mat_map.get("ceiling", default_mat)),
        (L * H, mat_map.get("wall_front", default_mat)),
        (L * H, mat_map.get("wall_back", default_mat)),
        (W * H, mat_map.get("wall_left", default_mat)),
        (W * H, mat_map.get("wall_right", default_mat)),
    ]
    return sabine_rt60(L * W * H, surfaces)


@router.get("")
def get_room(session_id: str):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    if session.room_config_path.exists():
        data = json.loads(session.room_config_path.read_text())
        config = RoomConfig.model_validate(data)
    else:
        config = RoomConfig()

    config.rt60_preview = _rt60_preview(config)
    return config


@router.put("")
def put_room(session_id: str, config: RoomConfig):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    # Clamp speaker/listener positions to room bounds
    for sp in config.speakers:
        sp.x = max(0.0, min(sp.x, config.length))
        sp.y = max(0.0, min(sp.y, config.width))
        sp.z = max(0.0, min(sp.z, config.height))
    config.listener.x = max(0.0, min(config.listener.x, config.length))
    config.listener.y = max(0.0, min(config.listener.y, config.width))
    config.listener.z = max(0.0, min(config.listener.z, config.height))

    config.rt60_preview = _rt60_preview(config)
    session.room_config_path.write_text(config.model_dump_json())
    return config


@router.get("/presets")
def list_presets():
    return list(ROOM_PRESETS.keys())


@router.get("/presets/{name}")
def get_preset(session_id: str, name: str):
    if name not in ROOM_PRESETS:
        raise HTTPException(404, f"Preset '{name}' not found")
    config = RoomConfig.model_validate(ROOM_PRESETS[name])
    config.rt60_preview = _rt60_preview(config)
    return config
