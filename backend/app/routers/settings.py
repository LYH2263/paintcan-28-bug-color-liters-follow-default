from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.paint_service import ColorBatchRejected, PaintService
router = APIRouter()


class ColorBatchBody(BaseModel):
    default_color_batch: str


@router.get("/settings")
def get_settings():
    with PaintService() as s: return s.settings()


@router.post("/settings/default-color-batch")
def set_default_color_batch(body: ColorBatchBody):
    with PaintService() as s:
        try:
            code = s.update_default_color_batch(body.default_color_batch)
        except ColorBatchRejected:
            raise HTTPException(400, "默认色号不能为空")
        return {"default_color_batch": code}
