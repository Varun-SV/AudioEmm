from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from schemas.eq import EQProfile, EQApplyRequest
from services.session_manager import session_manager
from services.eq_service import parse_fr_file, save_profile, load_profile, list_profiles

router = APIRouter(prefix="/sessions/{session_id}/eq", tags=["eq"])

MAX_EQ_BYTES = 1 * 1024 * 1024  # 1 MB


@router.post("/upload", response_model=EQProfile)
async def upload_fr(
    session_id: str,
    file: UploadFile = File(...),
    name: str = Form(...),
):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    content = await file.read()
    if len(content) > MAX_EQ_BYTES:
        raise HTTPException(413, "FR file exceeds 1 MB limit")

    try:
        freqs, dbs = parse_fr_file(content, file.filename or "")
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    profile_id = save_profile(session.eq_profiles, name, freqs, dbs)
    return EQProfile(
        profile_id=profile_id,
        name=name,
        frequencies=freqs.tolist(),
        db_values=dbs.tolist(),
    )


@router.get("")
def list_eq_profiles(session_id: str):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")
    return list_profiles(session.eq_profiles)


@router.get("/{profile_id}", response_model=EQProfile)
def get_eq_profile(session_id: str, profile_id: str):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")
    try:
        data = load_profile(session.eq_profiles, profile_id)
    except KeyError:
        raise HTTPException(404, "Profile not found")
    return EQProfile(**data)


@router.delete("/{profile_id}")
def delete_eq_profile(session_id: str, profile_id: str):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")
    path = session.eq_profiles / f"{profile_id}.json"
    if not path.exists():
        raise HTTPException(404, "Profile not found")
    path.unlink()
    return {"ok": True}
