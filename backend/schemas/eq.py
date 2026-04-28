from pydantic import BaseModel


class EQProfile(BaseModel):
    profile_id: str
    name: str
    frequencies: list[float]
    db_values: list[float]


class EQApplyRequest(BaseModel):
    source_job_id: str
    profile_id: str
