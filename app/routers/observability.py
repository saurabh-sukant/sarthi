from fastapi import APIRouter, HTTPException
from app.services.observability_service import ObservabilityService
from app.models.observability_models import ObservabilitySummary

router = APIRouter()
observability_service = ObservabilityService()

@router.get("/dashboard/{execution_id}", response_model=ObservabilitySummary)
async def get_dashboard_summary(execution_id: str):
    try:
        return await observability_service.get_summary(execution_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Note: Live stream would use SSE, implemented separately