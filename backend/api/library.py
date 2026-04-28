import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_user
from db.base import get_db
from db.models import AudioUpload, ProcessedResult, RoomSave, User
from schemas.room import RoomConfig

router = APIRouter(prefix="/library", tags=["library"])


class RoomSaveCreate(BaseModel):
    name: str
    config: RoomConfig


class RoomSaveRead(BaseModel):
    id: str
    name: str
    config: dict
    rt60_preview: float | None = None
    created_at: str
    updated_at: str


class AudioUploadRead(BaseModel):
    id: str
    filename: str
    duration_s: float
    sample_rate: int
    created_at: str


class ProcessedResultRead(BaseModel):
    id: str
    upload_id: str
    room_save_id: str | None
    duration_s: float
    download_url: str
    created_at: str


# ── Room Saves ────────────────────────────────────────────────────────────────

@router.get("/rooms", response_model=list[RoomSaveRead])
async def list_room_saves(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RoomSave).where(RoomSave.user_id == current_user.id).order_by(RoomSave.updated_at.desc())
    )
    rooms = result.scalars().all()
    return [
        RoomSaveRead(
            id=r.id,
            name=r.name,
            config=json.loads(r.config_json),
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in rooms
    ]


@router.post("/rooms", response_model=RoomSaveRead, status_code=201)
async def save_room(
    body: RoomSaveCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    room_save = RoomSave(
        user_id=current_user.id,
        name=body.name,
        config_json=body.config.model_dump_json(),
    )
    db.add(room_save)
    await db.commit()
    await db.refresh(room_save)
    return RoomSaveRead(
        id=room_save.id,
        name=room_save.name,
        config=json.loads(room_save.config_json),
        created_at=room_save.created_at.isoformat(),
        updated_at=room_save.updated_at.isoformat(),
    )


@router.get("/rooms/{room_id}", response_model=RoomSaveRead)
async def get_room_save(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    room_save = await db.get(RoomSave, room_id)
    if not room_save or room_save.user_id != current_user.id:
        raise HTTPException(404, "Room save not found")
    return RoomSaveRead(
        id=room_save.id,
        name=room_save.name,
        config=json.loads(room_save.config_json),
        created_at=room_save.created_at.isoformat(),
        updated_at=room_save.updated_at.isoformat(),
    )


@router.delete("/rooms/{room_id}", status_code=200)
async def delete_room_save(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    room_save = await db.get(RoomSave, room_id)
    if not room_save or room_save.user_id != current_user.id:
        raise HTTPException(404, "Room save not found")
    await db.delete(room_save)
    await db.commit()
    return {"ok": True}


# ── Audio Uploads ─────────────────────────────────────────────────────────────

@router.get("/audio", response_model=list[AudioUploadRead])
async def list_audio_uploads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AudioUpload)
        .where(AudioUpload.user_id == current_user.id)
        .order_by(AudioUpload.created_at.desc())
    )
    uploads = result.scalars().all()
    return [
        AudioUploadRead(
            id=u.id,
            filename=u.filename,
            duration_s=u.duration_s,
            sample_rate=u.sample_rate,
            created_at=u.created_at.isoformat(),
        )
        for u in uploads
    ]


@router.delete("/audio/{upload_id}", status_code=200)
async def delete_audio_upload(
    upload_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    upload = await db.get(AudioUpload, upload_id)
    if not upload or upload.user_id != current_user.id:
        raise HTTPException(404, "Upload not found")
    # Delete physical file
    src = Path(upload.storage_path)
    if src.exists():
        src.unlink()
    await db.delete(upload)
    await db.commit()
    return {"ok": True}


# ── Processed Results ─────────────────────────────────────────────────────────

@router.get("/results", response_model=list[ProcessedResultRead])
async def list_results(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProcessedResult)
        .where(ProcessedResult.user_id == current_user.id)
        .order_by(ProcessedResult.created_at.desc())
    )
    results = result.scalars().all()
    return [
        ProcessedResultRead(
            id=r.id,
            upload_id=r.upload_id,
            room_save_id=r.room_save_id,
            duration_s=r.duration_s,
            download_url=f"/api/library/results/{r.id}/download",
            created_at=r.created_at.isoformat(),
        )
        for r in results
    ]


@router.get("/results/{result_id}/download")
async def download_result(
    result_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(ProcessedResult, result_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(404, "Result not found")
    path = Path(row.result_path)
    if not path.exists():
        raise HTTPException(404, "File not found on disk")
    return FileResponse(str(path), media_type="audio/wav", filename=f"binaural_{result_id[:8]}.wav")


@router.delete("/results/{result_id}", status_code=200)
async def delete_result(
    result_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.get(ProcessedResult, result_id)
    if not row or row.user_id != current_user.id:
        raise HTTPException(404, "Result not found")
    path = Path(row.result_path)
    if path.exists():
        path.unlink()
    await db.delete(row)
    await db.commit()
    return {"ok": True}
