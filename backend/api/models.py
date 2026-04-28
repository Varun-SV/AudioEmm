from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from services.session_manager import session_manager

router = APIRouter(prefix="/sessions/{session_id}/models", tags=["models"])

ALLOWED_EXTENSIONS = {".glb", ".gltf", ".obj", ".fbx", ".stl"}
MAX_MODEL_MB = 50


@router.post("/upload")
async def upload_model(session_id: str, file: UploadFile = File(...)):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported format '{suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_MODEL_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_MODEL_MB} MB limit")

    session.models.mkdir(parents=True, exist_ok=True)

    model_id = uuid4().hex
    stored_name = f"{model_id}{suffix}"
    dest = session.models / stored_name
    dest.write_bytes(content)

    url = f"/api/sessions/{session_id}/models/{stored_name}"
    return {
        "model_id": model_id,
        "filename": file.filename,
        "url": url,
        "size_bytes": len(content),
    }


@router.get("/{stored_name}")
async def serve_model(session_id: str, stored_name: str):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    path = session.models / stored_name
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "Model file not found")

    suffix = path.suffix.lower()
    media_map = {
        ".glb":  "model/gltf-binary",
        ".gltf": "model/gltf+json",
        ".obj":  "text/plain",
        ".fbx":  "application/octet-stream",
        ".stl":  "model/stl",
    }
    media_type = media_map.get(suffix, "application/octet-stream")
    return FileResponse(str(path), media_type=media_type, filename=stored_name)
