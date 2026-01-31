from typing import List
from app.agents.memory_agent import MemoryAgent
from app.models.memory_models import MemoryItem

class MemoryService:
    def __init__(self):
        self.agent = MemoryAgent()

    async def list_memory(self) -> List[MemoryItem]:
        memories = await self.agent.read_memory()
        return [MemoryItem(**mem) for mem in memories]

    async def update_memory(self, memory_id: str, content: str):
        await self.agent.update_memory(memory_id, content)

    async def delete_memory(self, memory_id: str):
        await self.agent.delete_memory(memory_id)

    async def search_memory(self, query: str, memory_type: str = None) -> List[MemoryItem]:
        memories = await self.agent.read_memory(query=query, memory_type=memory_type)
        return [MemoryItem(**mem) for mem in memories]