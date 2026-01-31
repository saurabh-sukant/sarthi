from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.feedback_service import FeedbackService

router = APIRouter()
feedback_service = FeedbackService()

class FeedbackRequest(BaseModel):
    execution_id: str
    rating: str  # e.g., "up", "down"
    comment: Optional[str] = None

@router.post("/")
async def submit_feedback(request: FeedbackRequest):
    try:
        await feedback_service.process_feedback(request.execution_id, request.rating, request.comment)
        return {"status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))