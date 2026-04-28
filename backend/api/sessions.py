from fastapi import APIRouter, HTTPException

from services.session_manager import session_manager

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", status_code=201)
def create_session():
    session = session_manager.create_session()
    return session.to_dict()


@router.get("/{session_id}")
def get_session(session_id: str):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.delete("/{session_id}", status_code=200)
def delete_session(session_id: str):
    try:
        session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    session_manager.delete_session(session_id)
    return {"ok": True}
