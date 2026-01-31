from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.chat_service import ChatService
from app.models.chat_models import ChatQuery, ChatResponse

router = APIRouter()
chat_service = ChatService()

class QueryRequest(BaseModel):
    query: str
    attachments: Optional[List[str]] = []
    mode: str = "chat"

@router.post("/query", response_model=ChatResponse)
async def submit_chat_query(request: QueryRequest):
    try:
        response = await chat_service.process_query(request.query, request.attachments, request.mode)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Note: Streaming endpoint would use SSE, implemented separately