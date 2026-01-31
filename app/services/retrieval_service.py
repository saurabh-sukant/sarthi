from app.agents.retrieval_agent import RetrievalAgent
from typing import Dict, Any

class RetrievalService:
    async def retrieve(self, query: str, execution_id: str = None, top_k: int = 5, include_memory: bool = True) -> Dict[str, Any]:
        agent = RetrievalAgent(execution_id)
        return await agent.retrieve(query, top_k, include_memory)