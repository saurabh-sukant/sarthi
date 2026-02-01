from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.db.sqlite_client import log_observability_event, get_execution, get_observability_events
import asyncio
import json

router = APIRouter()

# Track which events have been sent per execution
sent_event_ids = {}

@router.get("/stream/{execution_id}")
async def stream_chat_execution(execution_id: str):
    """Stream real-time execution events and response via SSE."""

    async def event_generator():
        """Generate SSE events for the execution."""
        # Send initial connection event
        yield f"data: {json.dumps({'event': 'connected', 'execution_id': execution_id})}\n\n"

        sent_event_ids[execution_id] = set()
        max_wait = 120  # Maximum wait time in seconds
        poll_interval = 0.5  # Poll every 500ms
        elapsed = 0

        while elapsed < max_wait:
            try:
                # Get current execution state
                execution = get_execution(execution_id)
                
                if not execution:
                    yield f"data: {json.dumps({'error': 'Execution not found'})}\n\n"
                    break

                # Get all observability events for this execution
                all_events = get_observability_events(limit=100)
                execution_events = [e for e in all_events if e.get('execution_id') == execution_id]

                # Stream new events
                for event in execution_events:
                    event_key = f"{event.get('timestamp')}_{event.get('event_type')}_{event.get('agent_name')}"
                    
                    if event_key not in sent_event_ids[execution_id]:
                        sent_event_ids[execution_id].add(event_key)
                        
                        # Format event for frontend
                        event_data = {
                            "event": event.get('event_type', 'unknown'),
                            "agent": event.get('agent_name'),
                            "message": event.get('message'),
                            "timestamp": event.get('timestamp')
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"

                # Check if execution is complete
                if execution['status'] in ['completed', 'failed']:
                    # Stream final response
                    if execution.get('result'):
                        try:
                            result_data = json.loads(execution['result']) if isinstance(execution['result'], str) else execution['result']
                            if isinstance(result_data, dict):
                                final_response = result_data.get('final_response', '') or result_data.get('response', '')
                            else:
                                final_response = str(result_data)
                        except:
                            final_response = execution.get('result', '')
                        
                        # Stream the response content
                        if final_response:
                            yield f"data: {json.dumps({'type': 'response', 'final_response': final_response})}\n\n"

                    # Send completion event
                    yield f"data: {json.dumps({'status': 'completed', 'execution_id': execution_id})}\n\n"
                    break

                # Wait before polling again
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break

        # Cleanup
        if execution_id in sent_event_ids:
            del sent_event_ids[execution_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )