# Sarthi Frontend

A simple HTML and vanilla JavaScript frontend for the Sarthi AI co-pilot application.

## Features

- Clean, responsive chat interface
- Sidebar navigation for different sections
- Real-time communication with FastAPI backend
- Memory dashboard
- Agent management
- Observability panel

## Usage

1. Start the FastAPI backend on port 8000
2. Start the frontend server: `python -m http.server 8080`
3. Open `http://localhost:8080/index.html` in your browser

## Files

- `index.html` - Main application interface
- All styling and JavaScript is embedded in the HTML file

## API Endpoints

The frontend communicates with these backend endpoints:
- `POST /api/chat` - Send chat messages
- `GET /api/memory/items` - Get memory items
- `GET /api/agents/` - List available agents
- `POST /api/agents/ingestion` - Ingest documents
- `GET /api/observability/events` - Get observability events