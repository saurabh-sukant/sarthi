from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.config import settings
from typing import List, Optional
from datetime import datetime
import uuid

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memories"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String)
    content = Column(Text)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

class Execution(Base):
    __tablename__ = "executions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="running")
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String)
    rating = Column(Integer)
    comments = Column(Text)
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ObservabilityEvent(Base):
    __tablename__ = "observability_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)
    agent_name = Column(String)
    message = Column(Text)
    level = Column(String, default="info")
    execution_id = Column(String, nullable=True)

engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def create_execution() -> str:
    execution_id = str(uuid.uuid4())
    with SessionLocal() as session:
        execution = Execution(id=execution_id, status="running")
        session.add(execution)
        session.commit()
    return execution_id

def update_execution_status(execution_id: str, status: str, result: str = None):
    with SessionLocal() as session:
        execution = session.query(Execution).filter(Execution.id == execution_id).first()
        if execution:
            execution.status = status
            execution.updated_at = datetime.utcnow()
            if result:
                execution.result = result
            session.commit()

def log_observability_event(timestamp: datetime, event_type: str, agent_name: str,
                          message: str, level: str = "info", execution_id: str = None):
    with SessionLocal() as session:
        event = ObservabilityEvent(
            timestamp=timestamp,
            event_type=event_type,
            agent_name=agent_name,
            message=message,
            level=level,
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
                "status": execution.status,
                "result": execution.result,
                "created_at": execution.created_at.isoformat() if execution.created_at else None,
                "updated_at": execution.updated_at.isoformat() if execution.updated_at else None
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
                "message": event.message,
                "level": event.level,
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

async def create_execution(execution_id: str, conversation_id: str, query: str) -> Execution:
    async with async_session() as session:
        execution = Execution(id=execution_id, conversation_id=conversation_id, query=query)
        session.add(execution)
        await session.commit()
        await session.refresh(execution)
        return execution

async def update_execution_status(execution_id: str, status: str, result: str = None):
    async with async_session() as session:
        await session.execute(
            "UPDATE executions SET status = ?, completed_at = datetime('now'), result = ? WHERE id = ?",
            (status, result, execution_id)
        )
        await session.commit()

async def log_observability_event(execution_id: str, event_type: str, agent_name: str = None, tool_name: str = None, data: str = None):
    async with async_session() as session:
        event = ObservabilityEvent(
            execution_id=execution_id,
            event_type=event_type,
            agent_name=agent_name,
            tool_name=tool_name,
            data=data
        )
        session.add(event)
        await session.commit()