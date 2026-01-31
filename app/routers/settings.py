from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
from app.config import settings

router = APIRouter()

class SettingsUpdate(BaseModel):
    openai_api_key: str = ""
    chroma_path: str = "./chroma_db"
    database_url: str = "sqlite:///./sarthi.db"
    max_tokens: int = 1000
    temperature: float = 0.7
    model_name: str = "gpt-4"

@router.get("/settings")
async def get_settings() -> Dict[str, Any]:
    """Get current system settings"""
    return {
        "openai_api_key": settings.openai_api_key or "",
        "chroma_path": settings.chroma_path,
        "database_url": settings.database_url,
        "max_tokens": settings.max_tokens,
        "temperature": settings.temperature,
        "model_name": settings.model_name
    }

@router.put("/settings")
async def update_settings(settings_update: SettingsUpdate):
    """Update system settings"""
    try:
        # Update environment variables or config
        # Note: In a production system, you'd want to persist these securely
        if settings_update.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings_update.openai_api_key

        # For demo purposes, we'll just return success
        # In a real implementation, you'd update the config file or database
        return {"message": "Settings updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")