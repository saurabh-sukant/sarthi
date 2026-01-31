# SARTHI — Web UI & Backend API PRD

## Version
1.0

## Status
Approved (MVP)

## Product
SARTHI — Intelligent Incident Co-Pilot

---

# 1. Overview

This document defines the **UI-driven product requirements and backend API contracts** for SARTHI.

The system provides a **Rovo-style AI workspace** consisting of:
- Conversational chat
- Self-service agents
- Transparent observability
- Memory management
- Live agent execution streaming

All backend services are implemented in **Python (FastAPI)** and communicate with the frontend via **REST + Server-Sent Events (SSE)**.

---

# 2. UI Architecture Summary

### Left Navigation
1. Chat with SARTHI  
2. Memory Dashboard  
3. Agents  
4. Observability & Explainability  

### Observability Modes
- **Live Mode** — real-time execution
- **Dashboard Mode** — post-execution summary

---

# 3. Backend Architecture Overview

Browser (React / Next.js)
↓
FastAPI Gateway
↓
Agent Orchestration Layer (LangGraph)
↓
RAG + Memory + Tools
↓
Observability Event Bus


Backend Responsibilities:
- Orchestrate agents
- Stream execution events
- Enforce guardrails
- Manage memory
- Provide explainability data

---

# 4. API Design Principles

- Python 3.10+
- FastAPI async endpoints
- REST for control
- SSE for live execution
- Stateless UI requests
- Structured JSON responses
- No raw chain-of-thought exposure

---

# 5. Chat APIs

---

## 5.1 Submit Chat Query

**Endpoint**
POST /api/chat/query


**Purpose**
Submit a user query to SARTHI.

**Request**
```json
{
  "query": "Have we seen this error code before?",
  "attachments": [],
  "mode": "chat"
}
Response

{
  "conversation_id": "uuid",
  "execution_id": "uuid"
}
5.2 Stream Chat Execution (Live Mode)
Endpoint

GET /api/chat/stream/{execution_id}
Protocol

Server-Sent Events (SSE)

Events

{
  "event": "agent_started",
  "agent": "RetrievalAgent"
}
{
  "event": "tool_call",
  "tool": "vector_search",
  "input": "503 gateway error"
}
{
  "event": "agent_completed",
  "agent": "ReasoningAgent"
}
{
  "event": "final_response",
  "answer": "This error occurred in past incidents...",
  "citations": []
}
6. Memory Dashboard APIs
6.1 List Memory
GET /api/memory
Response

[
  {
    "id": "mem-123",
    "type": "EPISODIC",
    "content": "Gateway timeout fixed via restart",
    "source": "INC-1023",
    "created_at": "2026-01-20"
  }
]
6.2 Update Memory
PUT /api/memory/{memory_id}
{
  "content": "Gateway timeout usually fixed via restart"
}
6.3 Delete Memory (Soft Delete)
DELETE /api/memory/{memory_id}
7. Agents APIs
7.1 List Available Agents
GET /api/agents
[
  { "name": "SelfServiceAgent" },
  { "name": "IngestionAgent" }
]
7.2 Run Self-Service Agent
POST /api/agents/self-service/run
{
  "query": "Why is my dashboard not loading?"
}
Response

{
  "execution_id": "uuid"
}
7.3 Ingestion Agent
POST /api/agents/ingestion
Request

{
  "source_type": "url",
  "value": "https://docs.company.com/runbook"
}
Processing

Fetch content

Chunk text

Generate embeddings

Store in ChromaDB

Response

{
  "status": "completed",
  "chunks_indexed": 42
}
8. Observability APIs
8.1 Live Observability Stream
GET /api/observability/live/{execution_id}
Streams:

Planner decisions

Agent transitions

Tool calls

Memory reads/writes

8.2 Dashboard Summary
GET /api/observability/dashboard/{execution_id}
{
  "priority": "HIGH",
  "agents_ran": [
    "PlannerAgent",
    "RetrievalAgent",
    "ReasoningAgent"
  ],
  "data_used": [
    "INC-1023",
    "Gateway_Runbook_v3"
  ],
  "decision_summary": "Correlated gateway failures across incidents",
  "mitigation": "Restart gateway service"
}
9. Feedback APIs
9.1 Submit Feedback
POST /api/feedback
{
  "execution_id": "uuid",
  "rating": "down",
  "comment": "Answer missed recent deployment."
}
Triggers asynchronous learning.

10. Guardrail APIs
10.1 Input Validation
POST /api/guardrail/input
Used internally by orchestrator.

10.2 Output Validation
POST /api/guardrail/output
Evaluates final response before delivery.

11. Backend Services Mapping
Service	Responsibility
Chat Service	Conversation handling
Orchestrator	LangGraph execution
Retrieval Service	Vector search
Memory Service	Episodic + semantic memory
Ingestion Service	Document ingestion
Observability Service	Event streaming
Feedback Worker	Async learning
Guardrail Service	Safety enforcement
12. Technology Stack
Layer	Technology
Language	Python 3.10
API	FastAPI
Orchestration	LangGraph
Vector DB	ChromaDB
Memory DB	PostgreSQL
Streaming	SSE
Frontend	React / Next.js
13. MVP Scope
Included
Chat

Agents

Live observability

Memory dashboard

Ingestion

Feedback loop

Excluded
Authentication

RBAC

Multi-tenant isolation

14. Success Metrics
Metric	Target
TTFT	< 2 seconds
Incident reuse	≥ 40%
Self-service resolution	≥ 60%
User trust	≥ 4/5
15. Final Principle
SARTHI is not a chatbot.

It is a transparent reasoning system.

Every API must support:

explainability

observability

correction

trust
