import json
from pathlib import Path
from uuid import uuid4

import soundfile as sf
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from config import settings
from schemas.audio import AudioUploadResponse, ProcessRequest, AudioResultResponse
from services.session_manager import session_manager
from services.audio_pipeline import process_audio

router = APIRouter(prefix="/sessions/{session_id}/audio", tags=["audio"])

ALLOWED_MIME = {
    "audio/wav", "audio/x-wav", "audio/wave",
    "audio/mpeg", "audio/mp3",
    "audio/flac", "audio/ogg",
    "audio/aiff", "audio/x-aiff",
    "application/octet-stream",  # browsers sometimes use this for audio
}
MAX_BYTES = settings.max_upload_mb * 1024 * 1024


@router.post("/upload", response_model=AudioUploadResponse)
async def upload_audio(session_id: str, file: UploadFile = File(...)):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit")

    upload_id = uuid4().hex
    ext = Path(file.filename or "audio.wav").suffix or ".wav"
    dest = session.uploads / f"{upload_id}{ext}"
    dest.write_bytes(content)

    # Read metadata
    try:
        info = sf.info(str(dest))
        duration_s = info.duration
        sample_rate = info.samplerate
    except Exception:
        dest.unlink(missing_ok=True)
        raise HTTPException(422, "Could not read audio file. Ensure it is a valid audio format.")

    # Store metadata alongside the file
    meta = {"upload_id": upload_id, "filename": file.filename, "ext": ext,
            "duration_s": duration_s, "sample_rate": sample_rate}
    (session.uploads / f"{upload_id}.json").write_text(json.dumps(meta))

    return AudioUploadResponse(
        upload_id=upload_id,
        filename=file.filename or "",
        duration_s=duration_s,
        sample_rate=sample_rate,
    )


def _run_process(job_id: str, session_id: str, req: ProcessRequest):
    session_manager.set_job(job_id, "running")
    try:
        session = session_manager.get_session(session_id)

        # Find upload file
        upload_meta_path = session.uploads / f"{req.upload_id}.json"
        if not upload_meta_path.exists():
            raise FileNotFoundError(f"Upload {req.upload_id} not found")
        meta = json.loads(upload_meta_path.read_text())
        dry_path = session.uploads / f"{req.upload_id}{meta['ext']}"

        rir_path = session.rir / f"{req.rir_id}.npz"
        if not rir_path.exists():
            raise FileNotFoundError(f"RIR {req.rir_id} not found")

        # Load room config for speaker/listener positions
        speaker_pos = None
        listener_pos = None
        if (session.room_config_path).exists():
            from schemas.room import RoomConfig
            config = RoomConfig.model_validate(json.loads(session.room_config_path.read_text()))
            if config.speakers:
                sp = config.speakers[0]
                speaker_pos = (sp.x, sp.y, sp.z)
            lx = config.listener
            listener_pos = (lx.x, lx.y, lx.z)

        eq_profile_path = None
        if req.eq_profile_id:
            eq_profile_path = session.eq_profiles / f"{req.eq_profile_id}.json"

        output_path = session.results / f"{job_id}.wav"
        duration = process_audio(
            dry_path=dry_path,
            rir_path=rir_path,
            output_path=output_path,
            speaker_pos=speaker_pos,
            listener_pos=listener_pos,
            eq_profile_path=eq_profile_path,
            use_hrtf=True,
        )
        session_manager.set_job(job_id, "done", result={
            "result_url": f"/api/sessions/{session_id}/audio/download/{job_id}",
            "duration_s": round(duration, 2),
        })
    except Exception as exc:
        session_manager.set_job(job_id, "error", error=str(exc))


@router.post("/process")
def process_audio_endpoint(
    session_id: str,
    req: ProcessRequest,
    background_tasks: BackgroundTasks,
):
    try:
        session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")
    job_id = uuid4().hex
    session_manager.set_job(job_id, "pending")
    background_tasks.add_task(_run_process, job_id, session_id, req)
    return {"job_id": job_id, "status": "pending"}


@router.get("/result/{job_id}", response_model=AudioResultResponse)
def get_audio_result(session_id: str, job_id: str):
    try:
        session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")
    job = session_manager.get_job(job_id)
    result = job.get("result") or {}
    return AudioResultResponse(
        job_id=job_id,
        status=job["status"],
        result_url=result.get("result_url"),
        duration_s=result.get("duration_s"),
    )


@router.get("/download/{job_id}")
def download_audio(session_id: str, job_id: str):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")
    result_path = session.results / f"{job_id}.wav"
    if not result_path.exists():
        raise HTTPException(404, "Result not ready or not found")
    return FileResponse(
        str(result_path),
        media_type="audio/wav",
        filename=f"binaural_{job_id[:8]}.wav",
    )
