from pydantic import BaseModel
from typing import List, Optional

class ObservabilityEvent(BaseModel):
    event_type: str
    agent_name: Optional[str] = None
    tool_name: Optional[str] = None
    data: Optional[str] = None
    timestamp: str

class ObservabilitySummary(BaseModel):
    priority: str
    agents_ran: List[str]
    data_used: List[str]
    decision_summary: str
    mitigation: str