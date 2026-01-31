from app.core.orchestrator import Orchestrator
from app.models.chat_models import ChatQuery, ChatResponse

class ChatService:
    def __init__(self):
        self.orchestrator = Orchestrator()

    async def process_query(self, query: str, attachments: list, mode: str) -> ChatResponse:
        result = await self.orchestrator.run_query(query, attachments, mode)
        orchestrator_result = result.get("result", {})
        return ChatResponse(
            conversation_id=result["conversation_id"],
            execution_id=result["execution_id"],
            response=orchestrator_result.get("final_response", ""),
            status="completed"
        )