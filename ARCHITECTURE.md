# SARTHI Architecture Overview

## System Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose Network                   │
│                      (sarthi-network bridge)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐         ┌──────────────────────┐      │
│  │   sarthi-frontend   │         │     sarthi-api       │      │
│  │  (React + Vite)     │◄───────►│    (FastAPI)         │      │
│  │   Port: 5173        │ Axios   │    Port: 8000        │      │
│  │                     │  HTTP   │                      │      │
│  ├─────────────────────┤         ├──────────────────────┤      │
│  │ npm run build       │         │ uvicorn 0.0.0.0:8000│      │
│  │ serve -s dist       │         │                      │      │
│  └─────────────────────┘         └──────────────────────┘      │
│          │                                    │                 │
│          │                                    ▼                 │
│          │                         ┌──────────────────────┐     │
│          │                         │    chroma-db         │     │
│          │                         │  (Vector Database)   │     │
│          │                         │    Port: 8001        │     │
│          │                         └──────────────────────┘     │
│          │                                                       │
│          ▼                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │          HOST MACHINE (Localhost)                    │      │
│  │                                                      │      │
│  │  Port 5173  ◄─── Browser visits http://localhost:  │      │
│  │  Port 8000  ◄─── API requests from frontend        │      │
│  │  Port 8001  ◄─── Vector DB (optional browser)      │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Input (Browser)
    │
    ▼
React Component (Chat.jsx, Agents.jsx, etc.)
    │
    ▼
Axios API Client (src/services/api.js)
    │
    ├─ submitChatQuery()
    ├─ listAgents()
    ├─ runIngestion()
    ├─ submitFeedback()
    └─ ... (10+ endpoint wrappers)
    │
    ▼
HTTP Request → sarthi-api:8000
    │
    ▼
FastAPI Routers (app/routers/*.py)
    │
    ├─ /chat        → ChatService → LangGraph Orchestration
    ├─ /agents      → Agent Management & Ingestion
    ├─ /memory      → Memory Management
    ├─ /guardrail   → Input/Output Validation
    ├─ /feedback    → Learning & Feedback Loop
    ├─ /observability → Execution Monitoring
    └─ /settings    → Configuration
    │
    ▼
Data Persistence
    │
    ├─ SQLite (sarthi.db)
    └─ ChromaDB (chroma_db/) → Vector embeddings
```

## Component Hierarchy

```
App (React Root)
│
├─ Header
│  └─ Navigation Menu
│
├─ Sidebar
│  ├─ "Chat with SARTHI"
│  ├─ "Memory Dashboard"
│  ├─ "Agent Management"
│  └─ "Observability"
│
└─ Page Router
   ├─ Chat
   │  ├─ Messages Container
   │  ├─ Message (User)
   │  ├─ Message (Assistant)
   │  └─ Input Bar + Send Button
   │
   ├─ Agents
   │  ├─ Available Agents List
   │  └─ Document Ingestion Form
   │
   ├─ Feedback
   │  ├─ Execution ID Input
   │  ├─ Rating Select
   │  ├─ Comment Textarea
   │  └─ Submit Button
   │
   └─ Memory (optional expansion)
      ├─ Memory Items List
      ├─ Update/Delete Controls
      └─ Statistics
```

## API Integration Layer

```
src/services/api.js
│
├─ HTTP Client Configuration
│  └─ axios.create({baseURL: '/api', timeout: 30s})
│
├─ Chat Endpoints
│  ├─ submitChatQuery(query, attachments, mode)
│  └─ createEventSource(execution_id) → SSE streaming
│
├─ Agent Endpoints
│  ├─ listAgents()
│  ├─ runSelfService(query)
│  └─ runIngestion(source_type, value, metadata)
│
├─ Guardrail Endpoints
│  ├─ validateInput(content)
│  └─ validateOutput(content)
│
├─ Memory Endpoints
│  ├─ listMemory()
│  ├─ updateMemory(id, content)
│  └─ deleteMemory(id)
│
├─ Feedback Endpoint
│  └─ submitFeedback(execution_id, rating, comment)
│
└─ Observability Endpoints
   ├─ getDashboard(execution_id)
   └─ createEventSource(execution_id)
```

## Deployment Architecture

### Docker Compose Stack

```yaml
version: 3.8

services:
  sarthi-frontend:
    build: ./frontend
    ports: [5173:5173]
    env: VITE_API_BASE_URL=http://sarthi-api:8000
    depends_on: [sarthi-api] ← health check
    networks: [sarthi-network]

  sarthi-api:
    build: .
    ports: [8000:8000]
    env:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes: [./data, ./chroma_db]
    healthcheck: curl -f http://localhost:8000/api/agents
    networks: [sarthi-network]

  chroma-db:
    image: chromadb/chroma:latest
    ports: [8001:8000]
    volumes: [chroma_data:/chroma/chroma]
    networks: [sarthi-network]

networks:
  sarthi-network: { driver: bridge }

volumes:
  chroma_data:
```

### Build Process

**Frontend (Multi-stage)**
```
Stage 1: Builder
  node:18-alpine
  → npm ci
  → npm run build (Vite)
  → Generates /dist

Stage 2: Production
  node:18-alpine
  → Copy /dist from builder
  → npm install -g serve
  → serve -s dist -l 5173
```

**Backend**
```
python:3.10-slim
  → pip install -r requirements.txt
  → Copy app/
  → uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Communication Patterns

### REST (Request-Response)
```
Frontend                Backend
   │                      │
   ├─ POST /chat/query ──►│
   │                      ├─ Process query
   │                      ├─ Generate response
   │                      │
   │◄─ 200 OK + JSON ─────┤
   │   {execution_id}     │
```

### Server-Sent Events (Streaming)
```
Frontend                Backend
   │                      │
   ├─ GET /stream/{id} ──►│
   │                      ├─ event: agent_started
   │◄─ data: {...} ───────┤
   │                      ├─ event: tool_call
   │◄─ data: {...} ───────┤
   │                      ├─ event: final_response
   │◄─ data: {...} ───────┤
   │                      ├─ Close connection
   │◄─ [Connection close]─┤
```

## Key Features Enabled by Architecture

✓ **Real-time Updates**: SSE streaming for live execution monitoring
✓ **Scalability**: Docker containers can be independently scaled
✓ **Isolation**: Separate frontend/backend containers with health checks
✓ **Development**: Local dev without Docker using Vite + Axios
✓ **Production**: Optimized multi-stage builds for small image sizes
✓ **Reliability**: Service dependencies and health checks ensure proper startup order
✓ **Persistence**: Docker volumes for data and vector DB across restarts
✓ **Networking**: Bridge network enables inter-container communication
