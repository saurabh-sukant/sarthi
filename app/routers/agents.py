from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.ingestion_service import IngestionService
from app.agents.self_service_agent import SelfServiceAgent

router = APIRouter()
ingestion_service = IngestionService()

class AgentInfo(BaseModel):
    name: str

class IngestionRequest(BaseModel):
    source_type: str
    value: str
    metadata: Dict[str, Any] = None

class SelfServiceRequest(BaseModel):
    query: str

@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    return [
        {"name": "SelfServiceAgent"},
        {"name": "IngestionAgent"},
        # Add other agents as implemented
    ]

@router.post("/self-service/run")
async def run_self_service_agent(request: SelfServiceRequest):
    try:
        agent = SelfServiceAgent()
        execution_id = await agent.run(request.query)
        return {"execution_id": execution_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingestion")
async def run_ingestion_agent(request: IngestionRequest):
    try:
        result = await ingestion_service.ingest(request.source_type, request.value, request.metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))