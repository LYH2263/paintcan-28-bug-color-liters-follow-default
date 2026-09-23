from pydantic import BaseModel


class EstimateRequest(BaseModel):
    room_id: int
    coats: int | None = None
    coverage: float | None = None
    color_batch: str | None = None
    persist: bool = True
