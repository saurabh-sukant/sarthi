from pydantic import BaseModel
from typing import Optional

class MemoryItem(BaseModel):
    id: str
    type: str  # EPISODIC, SEMANTIC
    content: str
    source: Optional[str] = None
    created_at: str

class MemoryUpdate(BaseModel):
    content: str