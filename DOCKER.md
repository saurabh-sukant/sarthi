# SARTHI Docker Setup

## Prerequisites
- Docker and Docker Compose installed
- `.env` file with `OPENAI_API_KEY` and `SECRET_KEY`

## Quick Start

```bash
# Copy .env.example to .env and fill in your keys
cp .env.example .env

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| **sarthi-frontend** | http://localhost:5173 | React UI |
| **sarthi-api** | http://localhost:8000 | FastAPI backend |
| **chroma-db** | http://localhost:8001 | Vector DB |

## Endpoints

- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Chroma UI: http://localhost:8001

## Stop Services

```bash
docker-compose down
```

## Rebuild

```bash
docker-compose up -d --build
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: Secret key for the backend
- `VITE_API_BASE_URL`: Frontend API endpoint (set to `http://sarthi-api:8000` inside Docker)
