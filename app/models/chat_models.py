from pydantic import BaseModel

class ChatQuery(BaseModel):
    query: str
    attachments: list = []
    mode: str = "chat"

class ChatResponse(BaseModel):
    conversation_id: str
    execution_id: str