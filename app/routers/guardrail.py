from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.guardrail_service import GuardrailService

router = APIRouter()
guardrail_service = GuardrailService()

class ValidationRequest(BaseModel):
    content: str

@router.post("/input")
async def validate_input(request: ValidationRequest):
    try:
        result = await guardrail_service.validate_input(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/output")
async def validate_output(request: ValidationRequest):
    try:
        result = await guardrail_service.validate_output(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))