# sarthi PRD
intelligent co-worker

Product	Collaborative Incident sarthi
Version	1.0
Status	Approved for Hackathon Execution
Owner	Platform Architecture Team
Last Updated	{{today}}
1. Executive Summary

The Collaborative Incident Co-Pilot(sarthi) is an agentic AI-powered enterprise support system designed to function as an intelligent virtual support organization.

The platform coordinates multiple specialized AI agents to:

Understand incoming tickets, chats, and alerts

Retrieve relevant organizational knowledge

Reason across historical incidents

Generate accurate, explainable responses

Continuously learn from resolved incidents

Unlike traditional chatbots, this system enforces:

Clear separation of Retrieval → Reasoning → Generation

Persistent organizational memory

Real-time observability (“Glass Box AI”)

Strong guardrails and safety controls

2. Goals & Objectives
Goals

Reduce Mean Time to Resolution (MTTR)

Improve Tier-1 support efficiency

Preserve institutional knowledge

Increase response accuracy and trust

Non-Goals (v1)

Autonomous remediation

Infrastructure mutation

User personalization beyond session context

3. User Personas
Tier-1 Support Engineer

Drafts responses instantly

Reviews similar past incidents

Diagnoses issues faster

End Customer

Receives faster self-service support

Gets consistent, explainable responses

Operations Manager

Reviews AI learning

Edits or deletes stored memory

Ensures governance and trust

4. Functional Requirements
FR-01: Multi-Modal Ingestion

Description
The system must accept and normalize inputs from multiple enterprise sources and formats.

Sources

Support tickets

Chat conversations

Alerting systems

Formats

Text

PDF

Word

Images (screenshots, error dialogs)

Capabilities

OCR for images inside documents

Metadata extraction

Normalization into a standard internal schema

FR-02: Orchestration & Planning

Description
A planner must dynamically determine the execution strategy.

Capabilities

Serial execution

Parallel execution

Asynchronous background execution

Retry on failure

Graceful degradation

Technology

Graph-based orchestration (LangGraph)

FR-03: Advanced RAG

Mandatory separation

Retrieval → Reasoning → Generation


Retrieval

Semantic search via vector database

Metadata-aware filtering

Source citation tracking

Reasoning

Correlation across retrieved documents and memory

Root Cause Analysis (RCA)

Conflict resolution

Generation

Natural language synthesis

Explicit citation inclusion

FR-04: Hierarchical Memory System
Memory Types
Type	Purpose
Working Memory	Short-term graph execution state
Episodic Memory	Past incidents and ticket history
Semantic Memory	Knowledge base and documentation
Memory Management

View / Edit / Delete via UI

Soft-delete support

User-correctable learning

FR-05: Guardrails & Safety
Input Guardrails

Jailbreak detection (e.g. “Ignore instructions”)

Hate speech detection

Self-harm filtering

PII masking

Output Guardrails

Safety moderation

Policy enforcement

Escalation triggers

FR-06: Observability (Glass Box AI)

The system must expose real-time execution visibility.

Observable Events

Planner decisions

Agent handoffs

Tool calls

Retrieval queries

Memory writes

⚠ Raw chain-of-thought is never exposed.
Only structured reasoning summaries are shown.

FR-07: Feedback Loop

Asynchronous learning worker

Summarizes resolved incidents

Updates episodic memory

Improves future reasoning

5. Non-Functional Requirements
ID	Requirement
NFR-01	Explainability via citations and reasoning summary
NFR-02	Modular agents (Single Responsibility Principle)
NFR-03	Parallel execution to reduce TTFT
NFR-04	Planner-driven retries and graceful degradation
NFR-05	PII masking before LLM calls
6. Agent Responsibilities
Agent	Responsibility
Ingestion Agent	Normalize input, OCR, anonymization
Planner Agent	Select execution workflow
Intent Agent	Classify intent, urgency, risk
Retrieval Agent	Semantic search + citations
Memory Agent	Read/write episodic & semantic memory
Reasoning Agent	Correlation and RCA
Generator Agent	Draft response
Guardrail Agent	Safety validation
7. Required Architecture (MVP)
7.1 Architecture Overview

This architecture represents the MVP Enterprise RAG flow with safety, observability, and feedback built in.

7.2 Architecture Flow (Logical)
User Input
   ↓
Input Guardrail
   ↓
Expected Input Decision
   ├── Yes → Query Rewriting → HyDE → Encoding
   └── No  → Unexpected Input Handler
   ↓
Retrieval
   ↓
Re-ranking
   ↓
Generation
   ↓
Output Guardrail
   ↓
Final Response (with citations)
   ↓
Feedback + History update

7.3 Architecture Components
Input Layer

User Input

Input Guardrails

Query Intelligence

Query Rewriter

HyDE (Hypothetical Document Embedding)

Encoder

Retrieval Pipeline

Semantic retrieval

Ranking improvement

Knowledge Storage

Embedding Storage

Document Storage

History Storage

Feedback Storage

Generation

Generator

Output Guardrail

Final Response Generator

Observability

Central event stream

Agent and tool telemetry

Feedback Loop

Stores user feedback

Updates historical context

7.4 Architecture Diagram (Mermaid — for documentation)
flowchart TD
UI[User Input] --> IG[Input Guardrail]
IG --> DEC{Expected Input?}

DEC -- Yes --> QR[Query Rewriter]
DEC -- No --> UNEXP[Unexpected Input Handler]

QR --> HYDE[HyDE]
HYDE --> ENC[Encoder]
QR --> ENC

ENC --> RET[Retrieval]
RET --> RERANK[Improve Ranking]

RET --> DI[Document Ingestion]

subgraph STORAGE[Storage]
ES[Embedding Storage]
DS[Document Storage]
HS[History Storage]
FS[Feedback Storage]
end

DI --> ES
DI --> DS

HS -.-> QR
FS -.-> STORAGE

RERANK --> GEN[Generator]
GEN --> OG[Output Guardrail]
OG --> FRG[Final Response Generator]
FRG --> RESP[Final Response]

IG -.-> OBS[Observability]
RET -.-> OBS
GEN -.-> OBS
OG -.-> OBS
FRG -.-> OBS

RESP --> FS
RESP -.-> HS

8. Success Metrics
Metric	Target
MTTR reduction	≥ 30%
First-response accuracy	≥ 80%
Hallucination rate	< 5%
User satisfaction	≥ 4/5
Incident reuse	≥ 40%
9. Risks & Mitigations
Risk	Mitigation
Hallucination	Strict RAG + citations
Privacy leakage	Input PII masking
Incorrect learning	Editable memory
Latency	Parallel retrieval
Agent failure	Planner retries
10. Future Roadmap


Phase 2

Knowledge graph integration

Ownership reasoning

Service dependency analysis

Phase 3

Proactive incident detection

Predictive incident clustering

Approval-based automation


