# Sarthi - Collaborative Incident Co-Pilot

## Overview

Sarthi is an intelligent co-worker and AI-powered enterprise support system designed to function as a virtual support organization. It coordinates multiple specialized AI agents to understand incoming tickets, chats, and alerts; retrieve relevant organizational knowledge; reason across historical incidents; and generate accurate, explainable responses while continuously learning from resolved incidents.

## Features

- **Multi-Modal Ingestion**: Accepts and normalizes inputs from support tickets, chat conversations, alerting systems in various formats (text, PDF, Word).
- **Orchestration & Planning**: Dynamic execution strategy with serial/parallel/asynchronous execution, retries, and graceful degradation using graph-based orchestration.
- **Advanced RAG**: Mandatory separation of Retrieval → Reasoning → Generation with semantic search, metadata filtering, root cause analysis, and citation tracking.
- **Hierarchical Memory System**: Working, episodic, and semantic memory with view/edit/delete capabilities.
- **Guardrails & Safety**: Input/output guardrails including jailbreak detection, hate speech filtering, PII masking, and policy enforcement.
- **Observability (Glass Box AI)**: Real-time execution visibility with planner decisions, agent handoffs, tool calls, and structured reasoning summaries.
- **Feedback Loop**: Asynchronous learning from resolved incidents to update memory and improve future responses.

## Architecture

The system follows a modular agent-based architecture with the following components:

- **Ingestion Agent**: Normalizes input, anonymization.
- **Self-Service Agent**: Handles user queries autonomously.
- **Retrieval Agent**: Performs semantic search with citations.
- **Memory Agent**: Manages episodic and semantic memory.
- **Reasoning Agent**: Handles correlation and root cause analysis.
- **Generator Agent**: Drafts responses.
- **Guardrail Agent**: Ensures safety validation.

### Architecture Flow
```
User Input → Input Guardrail → Query Intelligence → Retrieval → Re-ranking → Generation → Output Guardrail → Final Response
```

## Tech Stack

- **Backend**: Python 3.10, FastAPI, LangGraph, ChromaDB, SQLite, OpenAI API
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Orchestration**: LangGraph (for graph-based agent workflows)
- **AI/ML**: LangChain, OpenAI GPT models
- **Vector Database**: ChromaDB
- **Storage**: SQLite
- **Real-time**: Server-Sent Events (SSE)
- **Deployment**: Docker, Docker Compose

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn
- OpenAI API key

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sarthi
   ```

2. **Set up the complete system**:
   ```bash
   python deploy.py setup
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

4. **Start the full system**:
   ```bash
   python deploy.py full
   ```

   This will start both backend (http://localhost:8000) and frontend (http://localhost:3000).

### Alternative: Manual Setup

1. **Backend Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Start Backend**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Start Frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

## Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - **API**: http://localhost:8000
   - **Frontend**: http://localhost:3000
   - **API Docs**: http://localhost:8000/docs

## Testing

### Run comprehensive system tests:
```bash
python deploy.py test
```

### Run individual API tests:
```bash
python test_system.py
```

## API Endpoints

### Chat & Core Functionality
- `POST /api/chat` - Submit a chat query and get response
- `GET /api/chat/stream/{execution_id}` - Stream execution events (SSE)

### Memory Management
- `GET /api/memory` - List memory items
- `GET /api/memory/executions/{execution_id}` - Get execution details
- `PUT /api/memory/{id}` - Update memory item
- `DELETE /api/memory/{id}` - Delete memory item

### Agent Management
- `GET /api/agents` - List available agents
- `POST /api/agents/ingestion` - Ingest documents for knowledge base
- `POST /api/agents/self-service/run` - Run self-service agent

### Observability
- `GET /api/observability/events` - Get observability events
- `GET /api/observability/dashboard/{execution_id}` - Get execution dashboard

### Feedback & Learning
- `POST /api/feedback` - Submit user feedback
- `GET /api/feedback` - Get feedback statistics

### Settings
- `GET /api/settings` - Get system settings
- `PUT /api/settings` - Update system settings

### Guardrails
- `POST /api/guardrail/check` - Check content against guardrails

## Frontend Features

The React-based frontend provides:

- **Chat Interface**: Interactive chat with real-time streaming
- **Memory Dashboard**: View and manage conversation history
- **Agent Management**: Upload documents and run agents
- **Observability Panel**: Monitor system events and executions
- **Settings Panel**: Configure API keys and system parameters

## Usage Examples

### Submit a Chat Query
```python
import requests

response = requests.post("http://localhost:8000/api/chat", json={
    "message": "How do I handle a server downtime incident?",
    "session_id": "user_session_123"
})
print(response.json())
```

### Upload a Document
```python
files = {"file": open("incident_guide.pdf", "rb")}
response = requests.post("http://localhost:8000/api/agents/ingestion", files=files)
print(response.json())
```

### Stream Execution Events
```javascript
const eventSource = new EventSource('/api/chat/stream/execution_123');
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Event:', data);
};
```

## Configuration

### Environment Variables (.env)
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./sarthi.db
CHROMA_PATH=./chroma_db
MAX_TOKENS=1000
TEMPERATURE=0.7
MODEL_NAME=gpt-4
```

### System Settings (via API)
- OpenAI model configuration
- Database and vector store paths
- Token limits and temperature settings
- Agent behavior parameters

## Project Structure

```
sarthi/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── db/
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── sqlite_client.py   # Database operations
│   │   └── chroma_client.py   # Vector database client
│   ├── agents/
│   │   ├── ingestion_agent.py # Document ingestion
│   │   └── self_service_agent.py # Query handling
│   ├── core/
│   │   └── orchestrator.py    # LangGraph workflow
│   ├── routers/
│   │   ├── chat.py           # Chat endpoints
│   │   ├── memory.py         # Memory management
│   │   ├── agents.py         # Agent operations
│   │   └── observability.py  # Monitoring
│   └── utils/
│       ├── pii_masking.py    # PII detection/masking
│       └── embeddings.py     # Text embeddings
├── frontend/
│   ├── app/
│   │   ├── layout.tsx        # Main layout
│   │   ├── page.tsx          # Home page
│   │   ├── chat/
│   │   ├── memory/
│   │   ├── agents/
│   │   ├── observability/
│   │   └── settings/
│   └── components/
│       ├── ChatInterface.tsx
│       ├── Sidebar.tsx
│       └── ObservabilityPanel.tsx
├── requirements.txt           # Python dependencies
├── package.json              # Node.js dependencies
├── docker-compose.yml        # Docker orchestration
├── test_system.py           # Comprehensive tests
├── deploy.py                # Deployment script
└── README.md
```

## Success Metrics

- **MTTR reduction**: ≥ 30%
- **First-response accuracy**: ≥ 80%
- **Hallucination rate**: < 5%
- **User satisfaction**: ≥ 4/5
- **Incident reuse**: ≥ 40%

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Make your changes and add tests.
4. Commit your changes (`git commit -m 'Add amazing feature'`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request.

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   - Ensure your API key is set in `.env`
   - Check API key validity and quota

2. **Database Connection Error**:
   - Verify SQLite file permissions
   - Check database path in configuration

3. **Frontend Build Errors**:
   - Clear node_modules: `rm -rf frontend/node_modules && npm install`
   - Check Node.js version compatibility

4. **Agent Execution Failures**:
   - Check observability logs for detailed error messages
   - Verify all dependencies are installed

### Logs and Debugging

- **Backend Logs**: Check console output when running the server
- **Frontend Logs**: Open browser developer tools
- **API Logs**: Use `/api/observability/events` endpoint
- **Database Logs**: Check SQLite file and ChromaDB directory

## License

This project is licensed under the MIT License.

## Roadmap

- **Phase 2**: Knowledge graph integration, ownership reasoning, service dependency analysis.
- **Phase 3**: Proactive incident detection, predictive incident clustering, approval-based automation.
- **Future**: Multi-tenant support, advanced analytics, integration with ITSM tools.