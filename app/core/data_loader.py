import asyncio
from pathlib import Path
from typing import List
from app.db.chroma_client import store_document_embeddings
from app.utils.embeddings import get_embeddings
from app.db.sqlite_client import log_observability_event
from datetime import datetime


CHUNK_SIZE = 800


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    # Simple fixed-size chunking preserving word boundaries when possible
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        # try to break at newline or space
        if end < length:
            sep = text.rfind('\n', start, end)
            if sep <= start:
                sep = text.rfind(' ', start, end)
            if sep > start:
                end = sep
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks


async def hotload_data(path: Path = None):
    """Hotload static files from the `data/` folder into the documents collection.

    This function reads text-like files under the `data` directory, splits them
    into chunks, computes embeddings, and stores them in Chroma's `documents`
    collection so the RetrievalAgent can find them via semantic search.
    """
    # Resolve default data directory (repository root /data)
    if path is None:
        repo_root = Path(__file__).resolve().parents[2]
        data_dir = repo_root / "data"
    else:
        data_dir = Path(path)

    if not data_dir.exists() or not data_dir.is_dir():
        # Nothing to load
        log_observability_event(datetime.utcnow(), "data_loader", "DataLoader", f"Data directory not found: {data_dir}")
        return

    # Collect files
    text_files = [p for p in data_dir.rglob("*") if p.suffix.lower() in {".txt", ".md", ".json", ".csv"}]
    if not text_files:
        log_observability_event(datetime.utcnow(), "data_loader", "DataLoader", f"No data files found in {data_dir}")
        return

    for file in text_files:
        try:
            content = file.read_text(encoding='utf-8')
        except Exception as e:
            log_observability_event(datetime.utcnow(), "data_loader", "DataLoader", f"Failed to read {file}: {e}")
            continue

        # For JSON files, try to compact to string
        if file.suffix.lower() == ".json":
            try:
                import json
                parsed = json.loads(content)
                # if dict/list, stringify; else keep raw
                if isinstance(parsed, (dict, list)):
                    content = json.dumps(parsed)
            except Exception:
                pass

        chunks = _chunk_text(content)
        if not chunks:
            continue

        # Compute embeddings in batches
        try:
            embeddings = await get_embeddings(chunks)
        except Exception as e:
            log_observability_event(datetime.utcnow(), "data_loader", "DataLoader", f"Embedding failed for {file}: {e}")
            continue

        # Build metadata per chunk
        metadata = [{"source": str(file.relative_to(data_dir)), "filename": file.name} for _ in chunks]

        try:
            await store_document_embeddings(chunks, embeddings, metadata)
            log_observability_event(datetime.utcnow(), "data_loader", "DataLoader", f"Loaded {len(chunks)} chunks from {file.name}")
        except Exception as e:
            log_observability_event(datetime.utcnow(), "data_loader", "DataLoader", f"Failed to store embeddings for {file}: {e}")


def load_data_sync(path: str = None):
    """Convenience wrapper to run hotload_data from sync context."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If running inside an async loop (e.g., Uvicorn), create a task
        asyncio.create_task(hotload_data(Path(path) if path else None))
    else:
        loop.run_until_complete(hotload_data(Path(path) if path else None))
