from app.agents.ingestion_agent import IngestionAgent
from typing import Dict, Any

class IngestionService:
    def __init__(self):
        self.agent = IngestionAgent()

    async def ingest(self, source_type: str, value: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self.agent.ingest(source_type, value, metadata)