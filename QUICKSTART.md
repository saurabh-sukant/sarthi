# SARTHI Quick Reference

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
docker-compose up -d
open http://localhost:5173
```

### Option 2: Local Dev
```bash
# Terminal 1: Backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

### Option 3: Setup Script
```bash
chmod +x setup.sh
./setup.sh docker    # or ./setup.sh local
```

---

## 📋 Services

| Service | Local | Docker | Docs |
|---------|-------|--------|------|
| Frontend | http://localhost:5173 | http://localhost:5173 | [frontend/README.md](frontend/README.md) |
| API | http://localhost:8000 | http://localhost:8000 | http://localhost:8000/docs |
| Vector DB | - | http://localhost:8001 | - |

---

## 🔌 API Endpoints

### Chat
```javascript
import { submitChatQuery, createEventSource } from './services/api'

// Send query
const res = await submitChatQuery('How do I handle outages?')

// Stream events
const es = createEventSource(res.execution_id)
es.onmessage = (ev) => console.log(JSON.parse(ev.data))
```

### Agents
```javascript
import { listAgents, runIngestion } from './services/api'

// List
const agents = await listAgents()

// Ingest
await runIngestion('text', 'incident guide...', { category: 'incident' })
```

### Memory
```javascript
import { listMemory, updateMemory, deleteMemory } from './services/api'

const items = await listMemory()
await updateMemory(id, 'updated content')
await deleteMemory(id)
```

### Feedback
```javascript
import { submitFeedback } from './services/api'

await submitFeedback('exec_123', 'up', 'Great response!')
```

### Guardrails
```javascript
import { validateInput, validateOutput } from './services/api'

await validateInput('user message')
await validateOutput('assistant response')
```

### Observability
```javascript
import { getDashboard } from './services/api'

const summary = await getDashboard('exec_123')
```

---

## 📁 Frontend Structure

```
src/
├── main.jsx              # Entry point
├── App.jsx               # Root router
├── index.css             # Styles
├── components/
│   ├── Chat.jsx
│   ├── Agents.jsx
│   └── Feedback.jsx
└── services/
    └── api.js            # All endpoints + axios config
```

---

## 🐳 Docker Commands

```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# Clean slate
docker-compose down -v
```

---

## 🔧 Environment Variables

### Backend
- `OPENAI_API_KEY` - OpenAI API key
- `SECRET_KEY` - Secret for signing tokens
- `DATABASE_URL` - SQLite path (default: `sqlite:///./sarthi.db`)
- `CHROMA_PATH` - Vector DB path (default: `./chroma_db`)

### Frontend
- `VITE_API_BASE_URL` - Backend URL (default: `http://localhost:8000`)

---

## 🛠️ Development

### Add a New API Endpoint

1. **Backend** (`app/routers/*.py`):
```python
@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    return {"result": "..."}
```

2. **Frontend** (`src/services/api.js`):
```javascript
export async function myEndpoint(param1, param2) {
  const res = await client.post('/my-endpoint', { param1, param2 })
  return res.data
}
```

3. **Component** (`src/components/*.jsx`):
```javascript
import { myEndpoint } from '../services/api'

const result = await myEndpoint(val1, val2)
```

### Test Frontend Locally
```bash
cd frontend
npm run dev
# http://localhost:5173
```

### Test Build
```bash
cd frontend
npm run build
npm run preview
# http://localhost:4173
```

---

## 📚 Documentation

- [Backend Architecture](prd.md)
- [Frontend Guide](frontend/README.md)
- [Docker Setup](DOCKER.md)
- [API Routes](app/routers/)
- [Integration Summary](INTEGRATION_SUMMARY.md)

---

## 🐛 Troubleshooting

### Frontend can't connect to API
- Check `VITE_API_BASE_URL` environment variable
- Verify backend is running on port 8000
- Check CORS settings in backend

### Docker containers won't start
```bash
# Clean and rebuild
docker-compose down -v
docker-compose up --build
```

### Frontend build fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### API responding with 500
```bash
# Check backend logs
docker-compose logs sarthi-api
# Or locally
python -m uvicorn app.main:app --reload
```

---

## 📞 Support

See [README.md](README.md) for full documentation.
