import json
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException

from schemas.room import RoomConfig
from schemas.simulation import SimulationRequest, SimulationResult, JobStatus
from services.session_manager import session_manager
from services.acoustic_engine import compute_rir

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
