from app.core.orchestrator import Orchestrator
from app.models.chat_models import ChatQuery, ChatResponse
from app.agents.memory_agent import MemoryAgent

class ChatService:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.memory_agent = MemoryAgent()

    async def process_query(self, query: str, attachments: list, mode: str) -> ChatResponse:
        result = await self.orchestrator.run_query(query, attachments, mode)
        orchestrator_result = result.get("result", {})
        response_text = orchestrator_result.get("final_response", "")
        
        # **IMPORTANT**: Immediately store this conversation turn as episodic memory
        # so that future queries can retrieve context about what the user told us
        if query and response_text:
            try:
                # Store the complete conversation turn for future recall
                conversation_memory = f"User: {query}\nAssistant: {response_text}"
                await self.memory_agent.write_memory(
                    content=conversation_memory,
                    memory_type="conversation",
                    source="chat_interaction"
                )
            except Exception as e:
                # Log but don't fail the response if memory write fails
                print(f"Warning: Failed to store conversation memory: {e}")
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            execution_id=result["execution_id"],
            response=response_text,
            status="completed"
        )