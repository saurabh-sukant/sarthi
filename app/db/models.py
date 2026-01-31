from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True)  # EPISODIC, SEMANTIC, WORKING
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

class Execution(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    query = Column(Text, nullable=False)
    status = Column(String, default="running")  # running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, ForeignKey("executions.id"), index=True)
    rating = Column(String, nullable=False)  # up, down
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    execution = relationship("Execution")

class ObservabilityEvent(Base):
    __tablename__ = "observability_events"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, ForeignKey("executions.id"), index=True)
    event_type = Column(String, nullable=False)  # agent_started, tool_call, etc.
    agent_name = Column(String, nullable=True)
    tool_name = Column(String, nullable=True)
    data = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

    execution = relationship("Execution")