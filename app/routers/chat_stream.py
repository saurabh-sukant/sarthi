from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.db.sqlite_client import log_observability_event
import asyncio
import json

router = APIRouter()

# In-memory storage for demo - in production, use Redis or similar
active_streams = {}

@router.get("/stream/{execution_id}")
async def stream_chat_execution(execution_id: str):
    """Stream real-time execution events via SSE."""

    async def event_generator():
        """Generate SSE events for the execution."""
        # Send initial connection event
        yield f"data: {json.dumps({'event': 'connected', 'execution_id': execution_id})}\n\n"

        # Listen for events (in a real implementation, this would poll a queue or use websockets)
        # For demo, we'll simulate some events
        events = [
            {"event": "agent_started", "agent": "GuardrailAgent", "timestamp": "2026-01-31T10:00:00Z"},
            {"event": "agent_completed", "agent": "GuardrailAgent", "timestamp": "2026-01-31T10:00:01Z"},
            {"event": "agent_started", "agent": "RetrievalAgent", "timestamp": "2026-01-31T10:00:02Z"},
            {"event": "tool_call", "tool": "vector_search", "input": "gateway timeout", "timestamp": "2026-01-31T10:00:03Z"},
            {"event": "agent_completed", "agent": "RetrievalAgent", "timestamp": "2026-01-31T10:00:04Z"},
            {"event": "agent_started", "agent": "ReasoningAgent", "timestamp": "2026-01-31T10:00:05Z"},
            {"event": "agent_completed", "agent": "ReasoningAgent", "timestamp": "2026-01-31T10:00:06Z"},
            {"event": "agent_started", "agent": "GeneratorAgent", "timestamp": "2026-01-31T10:00:07Z"},
            {"event": "final_response", "answer": "Based on incident INC-1023, gateway timeouts are typically resolved by restarting the gateway service.", "citations": ["INC-1023"], "timestamp": "2026-01-31T10:00:08Z"}
        ]

        for event in events:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.5)  # Simulate timing

        # Send completion event
        yield f"data: {json.dumps({'event': 'execution_completed', 'execution_id': execution_id})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )