from fastapi import APIRouter, HTTPException
from typing import List
from app.services.memory_service import MemoryService
from app.models.memory_models import MemoryItem, MemoryUpdate

router = APIRouter()
memory_service = MemoryService()

@router.get("/", response_model=List[MemoryItem])
async def list_memory():
    try:
        return await memory_service.list_memory()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{memory_id}")
async def update_memory(memory_id: str, update: MemoryUpdate):
    try:
        await memory_service.update_memory(memory_id, update.content)
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    try:
        await memory_service.delete_memory(memory_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))