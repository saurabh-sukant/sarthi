from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, memory, agents, observability, feedback, guardrail, settings as settings_router
from app.routers.chat_stream import router as chat_stream_router
from app.config import settings
from app.db.sqlite_client import init_db
from app.db.chroma_client import init_chroma_collections
from app.core.data_loader import hotload_data
import asyncio

app = FastAPI(title="Sarthi - Collaborative Incident Co-Pilot", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(chat_stream_router, prefix="/api/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(observability.router, prefix="/api/observability", tags=["observability"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(guardrail.router, prefix="/api/guardrail", tags=["guardrail"])
app.include_router(settings_router.router, prefix="/api", tags=["settings"])

@app.on_event("startup")
async def startup_event():
    init_db()
    await init_chroma_collections()
    # Hotload any static data under /data into Chroma for retrieval
    await hotload_data()

@app.get("/")
async def root():
    return {"message": "Welcome to Sarthi API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)