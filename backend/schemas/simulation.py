from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    max_order: int = Field(default=3, ge=1, le=8)
    rir_duration: float = Field(default=1.0, ge=0.2, le=5.0)


class SimulationResult(BaseModel):
    rir_id: str
    rt60_sabine: float
    rt60_computed: float | None
    direct_delay_ms: float
    reflection_count: int
    job_id: str


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending | running | done | error
    progress: float = 0.0
    result: dict | None = None
    error: str | None = None
