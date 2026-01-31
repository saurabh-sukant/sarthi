# Sarthi Implementation To-Do List

## Overview
This document outlines the step-by-step implementation strategy for the Sarthi (Collaborative Incident Co-Pilot) project. As a senior developer, I've analyzed the PRDs (prd.md and web.md) and created a phased approach focusing on MVP delivery for the hackathon.

## Overall Strategy
- **Phased Development**: Break down into manageable phases with clear deliverables.
- **MVP Focus**: Prioritize core chat functionality, basic agents, and observability.
- **Incremental Testing**: Test each component as it's built.
- **Tech Stack**: Python 3.10, FastAPI, LangGraph, ChromaDB, SQLite, SSE.
- **Architecture**: Modular agents, service layer, REST APIs with SSE streaming.
- **Timeline**: Aim for functional MVP in 2-3 weeks of development.

## Phase 1: Core Setup and Infrastructure (1-2 days)
### 1.1 Environment Setup
- [ ] Install Python 3.10 and create virtual environment
- [ ] Install dependencies from requirements.txt
- [ ] Set up .env file with API keys and configurations
- [ ] Initialize ChromaDB and SQLite databases
- [ ] Test basic FastAPI app startup

### 1.2 Database Schema Setup
- [ ] Define SQLAlchemy models for Memory, History, Feedback tables
- [ ] Create database migration scripts
- [ ] Implement ChromaDB collection setup for embeddings
- [ ] Add initial seed data (sample memories/documents)

### 1.3 Core Utilities

- [ ] Add PII masking functions
- [ ] Create embedding generation (OpenAI or local)
- [ ] Set up logging and error handling

## Phase 2: Basic Agents Implementation (3-4 days)
### 2.1 Ingestion Agent
- [ ] Implement document fetching (URL, file upload)
- [ ] Add text chunking and preprocessing
- [ ] Integrate embedding generation
- [ ] Store chunks in ChromaDB with metadata

### 2.2 Retrieval Agent
- [ ] Implement semantic search in ChromaDB
- [ ] Add metadata filtering
- [ ] Implement re-ranking logic
- [ ] Return citations with results

### 2.3 Memory Agent
- [ ] CRUD operations for episodic memory
- [ ] Semantic memory management
- [ ] Working memory for execution state
- [ ] Integration with SQLite

### 2.4 Guardrail Agent
- [ ] Input validation (jailbreak, hate speech, PII)
- [ ] Output safety checks
- [ ] Escalation triggers
- [ ] Integration with LLM calls

## Phase 3: LangGraph Orchestrator (2-3 days)
### 3.1 Basic Graph Setup
- [ ] Define state schema for LangGraph
- [ ] Create nodes for each agent
- [ ] Implement conditional routing
- [ ] Add error handling and retries

### 3.2 Workflow Implementation
- [ ] Implement RAG flow: Retrieval → Reasoning → Generation
- [ ] Add planner for dynamic execution
- [ ] Integrate guardrails at input/output
- [ ] Add parallel execution where possible

### 3.3 Execution Management
- [ ] Track execution state and progress
- [ ] Implement graceful degradation
- [ ] Add timeout handling
- [ ] Support for background/async execution

## Phase 4: API Implementation (3-4 days)
### 4.1 Chat APIs
- [ ] POST /api/chat/query - Submit queries
- [ ] GET /api/chat/stream/{execution_id} - SSE streaming
- [ ] Implement conversation management
- [ ] Add attachment handling

### 4.2 Memory APIs
- [ ] GET /api/memory - List memories
- [ ] PUT /api/memory/{id} - Update memory
- [ ] DELETE /api/memory/{id} - Soft delete
- [ ] Add filtering and pagination

### 4.3 Agent APIs
- [ ] GET /api/agents - List available agents
- [ ] POST /api/agents/self-service/run - Run self-service
- [ ] POST /api/agents/ingestion - Document ingestion
- [ ] Add execution tracking

### 4.4 Observability APIs
- [ ] GET /api/observability/dashboard/{execution_id} - Summary
- [ ] GET /api/observability/live/{execution_id} - Live stream
- [ ] Implement event streaming
- [ ] Add structured reasoning summaries

### 4.5 Feedback and Guardrail APIs
- [ ] POST /api/feedback - Submit feedback
- [ ] POST /api/guardrail/input - Input validation
- [ ] POST /api/guardrail/output - Output validation
- [ ] Integrate with learning loop

## Phase 5: Advanced Features (2-3 days)
### 5.1 Reasoning and Generation
- [ ] Implement Reasoning Agent with RCA
- [ ] Add conflict resolution logic
- [ ] Integrate Generator Agent with citations
- [ ] Add natural language synthesis

### 5.2 Intent Classification
- [ ] Implement Intent Agent
- [ ] Add urgency and risk assessment
- [ ] Integrate with planner decisions

### 5.3 Feedback Loop
- [ ] Asynchronous learning worker
- [ ] Update episodic memory from feedback
- [ ] Improve future responses
- [ ] Add metrics tracking

## Phase 6: Testing and Refinement (2-3 days)
### 6.1 Unit Testing
- [ ] Test each agent individually
- [ ] Test service layer functions
- [ ] Add mock data for testing
- [ ] Achieve 80%+ code coverage

### 6.2 Integration Testing
- [ ] Test full RAG pipeline
- [ ] Test API endpoints
- [ ] Test SSE streaming
- [ ] Performance testing (TTFT < 2s)

### 6.3 End-to-End Testing
- [ ] Complete chat workflows
- [ ] Memory management flows
- [ ] Observability features
- [ ] Error handling scenarios

## Phase 7: Deployment and Documentation (1-2 days)
### 7.1 Containerization
- [ ] Finalize Dockerfile
- [ ] Create docker-compose.yml for full stack
- [ ] Add environment-specific configs

### 7.2 Documentation
- [ ] Update README.md with setup instructions
- [ ] Add API documentation (Swagger)
- [ ] Create deployment guide
- [ ] Add troubleshooting section

### 7.3 Final Polish
- [ ] Code cleanup and optimization
- [ ] Security review
- [ ] Performance optimization
- [ ] Final testing

## Risk Mitigation
- **Technical Risks**:
  - LangGraph complexity: Start with simple linear flow, expand gradually
  - Embedding performance: Use batch processing and caching
  - Database scaling: Start with SQLite, plan for PostgreSQL migration

- **Timeline Risks**:
  - Parallel development: Work on independent components simultaneously
  - MVP scope: Focus on core chat + 2-3 agents for demo
  - Buffer time: Include 20% buffer for unexpected issues

- **Quality Risks**:
  - Testing strategy: Automated tests for all critical paths
  - Code reviews: Self-review with checklists
  - Documentation: Update docs as you build

## Success Criteria
- [ ] Functional chat interface with basic Q&A
- [ ] At least 3 working agents (Ingestion, Retrieval, Memory)
- [ ] Real-time observability dashboard
- [ ] Memory management UI
- [ ] TTFT < 2 seconds for simple queries
- [ ] 80%+ test coverage
- [ ] Docker containerized deployment
- [ ] Complete API documentation

## Next Steps
1. Start with Phase 1: Set up development environment
2. Implement Ingestion Agent as first working component
3. Build basic orchestrator for linear agent flow
4. Add chat API and test end-to-end
5. Iterate based on testing and feedback

This plan provides a structured path to MVP while allowing flexibility for discoveries during implementation.