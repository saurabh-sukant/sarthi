from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.ingestion_service import IngestionService
from app.agents.self_service_agent import SelfServiceAgent

router = APIRouter()
ingestion_service = IngestionService()

class AgentInfo(BaseModel):
    name: str
    description: str

class IngestionRequest(BaseModel):
    source_type: str
    value: str
    metadata: Dict[str, Any] = None

class SelfServiceRequest(BaseModel):
    query: str

@router.get("/", response_model=List[AgentInfo])
async def list_agents():
    return [
        {"name": "SelfServiceAgent", "description": "Handles user queries and provides self-service solutions"},
        {"name": "OrchestratorAgent", "description": "Coordinates multiple agents to fulfill complex tasks"},
        {"name": "IngestionAgent", "description": "Manages data ingestion from various sources"},
        {"name": "RetrievalAgent", "description": "Retrieves relevant documents and memory based on queries"},
        {"name": "MemoryAgent", "description": "Handles memory storage and retrieval for agents"},
        {"name": "ReasoningAgent", "description": "Performs reasoning over provided data to generate insights"},
        {"name":"ResponseSynthesisAgent", "description":"Synthesizes final responses from aggregated information"},
        {"name":"GuardrailAgent", "description":"Ensures outputs adhere to defined safety and quality guidelines"},
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