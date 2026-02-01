# SARTHI Frontend (React + Vite + Axios)

React-based frontend for the SARTHI incident co-pilot system with axios-based endpoint management.

## Local Development

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start dev server (default: http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

- `VITE_API_BASE_URL`: Backend API base URL (default: `http://localhost:8000`)

## API Services

All backend endpoints are wrapped in `src/services/api.js` using axios:

- **Chat**: `submitChatQuery()`, streaming via SSE
- **Agents**: `listAgents()`, `runSelfService()`, `runIngestion()`
- **Guardrail**: `validateInput()`, `validateOutput()`
- **Memory**: `listMemory()`, `updateMemory()`, `deleteMemory()`
- **Feedback**: `submitFeedback()`
- **Observability**: `getDashboard()`, `createEventSource()`

## Docker

Build and run within docker-compose (see `DOCKER.md` in project root):

```bash
docker-compose up -d
```

Frontend will be available at `http://localhost:5173`