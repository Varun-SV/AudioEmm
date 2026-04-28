import asyncio
import json
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from schemas.room import RoomConfig
from schemas.simulation import SimulationRequest, JobStatus
from services.session_manager import session_manager
from services.acoustic_engine import compute_rir, compute_rir_preview

router = APIRouter(prefix="/sessions/{session_id}", tags=["simulation"])


def _run_simulation(job_id: str, config: RoomConfig, session_id: str, req: SimulationRequest):
    session_manager.set_job(job_id, "running")
    try:
        session = session_manager.get_session(session_id)
        result = compute_rir(
            config=config,
            session_rir_dir=session.rir,
            max_order=req.max_order,
            rir_duration=req.rir_duration,
            ray_tracing=True,
        )
        session_manager.set_job(job_id, "done", result=result)
    except Exception as exc:
        session_manager.set_job(job_id, "error", error=str(exc))


@router.post("/simulate")
def start_simulation(
    session_id: str,
    req: SimulationRequest,
    background_tasks: BackgroundTasks,
):
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    if not session.room_config_path.exists():
        raise HTTPException(400, "No room config found. Save a room first.")

    config = RoomConfig.model_validate(json.loads(session.room_config_path.read_text()))
    job_id = uuid4().hex
    session_manager.set_job(job_id, "pending")
    background_tasks.add_task(_run_simulation, job_id, config, session_id, req)
    return {"job_id": job_id, "status": "pending"}


@router.post("/simulate/preview")
def simulate_preview(session_id: str):
    """
    Fast synchronous preview (ISM order 1, no ray tracing, no file I/O).
    Returns RT60 + reflection stats inline in < 300 ms.
    Triggered on every speaker/listener drag debounce.
    """
    try:
        session = session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    if not session.room_config_path.exists():
        raise HTTPException(400, "No room config found.")

    config = RoomConfig.model_validate(json.loads(session.room_config_path.read_text()))
    try:
        return compute_rir_preview(config)
    except Exception as exc:
        raise HTTPException(500, f"Preview failed: {exc}")


@router.get("/simulate/status/{job_id}")
def get_simulation_status(session_id: str, job_id: str):
    try:
        session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")
    job = session_manager.get_job(job_id)
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        result=job.get("result"),
        error=job.get("error"),
    )


@router.get("/simulate/progress/{job_id}")
async def stream_simulation_progress(session_id: str, job_id: str):
    """Server-Sent Events stream for live deep simulation progress."""
    try:
        session_manager.get_session(session_id)
    except KeyError:
        raise HTTPException(404, "Session not found")

    async def event_generator():
        while True:
            job = session_manager.get_job(job_id)
            yield f"data: {json.dumps({'job_id': job_id, 'status': job['status'], 'result': job.get('result'), 'error': job.get('error')})}\n\n"
            if job["status"] in ("done", "error", "not_found"):
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
