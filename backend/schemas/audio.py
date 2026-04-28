from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    upload_id: str
    filename: str
    duration_s: float
    sample_rate: int


class ProcessRequest(BaseModel):
    upload_id: str
    rir_id: str
    eq_profile_id: str | None = None


class AudioResultResponse(BaseModel):
    job_id: str
    status: str
    result_url: str | None = None
    duration_s: float | None = None
