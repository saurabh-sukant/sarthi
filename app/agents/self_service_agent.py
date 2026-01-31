import uuid
from app.core.orchestrator import Orchestrator

class SelfServiceAgent:
    def __init__(self):
        self.orchestrator = Orchestrator()

    async def run(self, query: str):
        execution_id = str(uuid.uuid4())
        # Run query through orchestrator
        await self.orchestrator.run_query(query, [], "self-service")
        return execution_id