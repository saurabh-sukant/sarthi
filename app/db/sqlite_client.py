from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from typing import List, Optional
from datetime import datetime
import uuid

# Use canonical models defined in app/db/models.py to avoid schema drift
from app.db.models import Base, Memory, Execution, Feedback, ObservabilityEvent

engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Prepare async engine/session for async helpers (e.g. memory agent)
_db_url = settings.database_url
if _db_url.startswith("sqlite:///"):
    async_db_url = _db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
elif _db_url.startswith("sqlite://"):
    async_db_url = _db_url.replace("sqlite://", "sqlite+aiosqlite://")
else:
    async_db_url = _db_url

async_engine = create_async_engine(async_db_url, echo=True)
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def create_execution(execution_id: str, conversation_id: str, query: str) -> str:
    """Create an execution record."""
    with SessionLocal() as session:
        execution = Execution(id=execution_id, conversation_id=conversation_id, query=query, status="running")
        session.add(execution)
        session.commit()
    return execution_id

def update_execution_status(execution_id: str, status: str, result: str = None):
    with SessionLocal() as session:
        execution = session.query(Execution).filter(Execution.id == execution_id).first()
        if execution:
            execution.status = status
            if status in ("completed", "failed"):
                try:
                    execution.completed_at = datetime.utcnow()
                except Exception:
                    pass
            if result is not None:
                execution.result = result
            session.commit()

def log_observability_event(timestamp: datetime, event_type: str, agent_name: str = None, message: str = None, level: str = "info", execution_id: str = None):
    """Log an observability event.

    Signature: (timestamp, event_type, agent_name, message, level="info", execution_id=None)
    """
    print(f"Logging event: {event_type} at {timestamp.isoformat()} message: {message} agent: {agent_name} level: {level} execution_id: {execution_id}")
    with SessionLocal() as session:
        event = ObservabilityEvent(
            timestamp=timestamp,
            event_type=event_type,
            agent_name=agent_name,
            tool_name=None,
            data=message,
            execution_id=execution_id
        )
        session.add(event)
        session.commit()

def get_memory_items() -> List[dict]:
    with SessionLocal() as session:
        memories = session.query(Memory).filter(Memory.is_deleted == False).all()
        return [
            {
                "id": memory.id,
                "type": memory.type,
                "content": memory.content,
                "source": memory.source,
                "created_at": memory.created_at.isoformat() if memory.created_at else None
            } for memory in memories
        ]

def get_execution(execution_id: str) -> Optional[dict]:
    with SessionLocal() as session:
        execution = session.query(Execution).filter(Execution.id == execution_id).first()
        if execution:
            return {
                "id": execution.id,
                "conversation_id": getattr(execution, "conversation_id", None),
                "query": getattr(execution, "query", None),
                "status": execution.status,
                "started_at": getattr(execution, "started_at", None).isoformat() if getattr(execution, "started_at", None) else None,
                "completed_at": getattr(execution, "completed_at", None).isoformat() if getattr(execution, "completed_at", None) else None,
                "result": execution.result
            }
        return None

def get_observability_events(limit: int = 100) -> List[dict]:
    with SessionLocal() as session:
        events = session.query(ObservabilityEvent).order_by(ObservabilityEvent.timestamp.desc()).limit(limit).all()
        return [
            {
                "id": event.id,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                "event_type": event.event_type,
                "agent_name": event.agent_name,
                "message": event.data,
                "level": None,
                "execution_id": event.execution_id
            } for event in events
        ]

async def update_memory_item(memory_id: str, content: str):
    async with async_session() as session:
        await session.execute(
            "UPDATE memories SET content = ?, updated_at = datetime('now') WHERE id = ?",
            (content, memory_id)
        )
        await session.commit()

async def delete_memory_item(memory_id: str):
    async with async_session() as session:
        await session.execute(
            "UPDATE memories SET is_deleted = 1, updated_at = datetime('now') WHERE id = ?",
            (memory_id,)
        )
        await session.commit()



