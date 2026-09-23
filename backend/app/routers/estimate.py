from fastapi import APIRouter, HTTPException
from app.schemas.estimate import EstimateRequest
from app.services.paint_service import ColorBatchRejected, PaintService
router = APIRouter()
@router.post("/estimate")
def post_estimate(body: EstimateRequest):
    with PaintService() as s:
        try:
            r = s.estimate(body.room_id, body.persist, body.coats, body.coverage, body.color_batch)
        except ColorBatchRejected:
            raise HTTPException(400, "色号不能为空，整单已拒绝")
        if not r: raise HTTPException(404)
        return r
