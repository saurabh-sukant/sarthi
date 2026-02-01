from typing import List, Dict, Any
from app.db.sqlite_client import get_memory_items, update_memory_item, delete_memory_item, create_memory_item
from app.utils.embeddings import get_embeddings
from app.db.chroma_client import store_memory_embeddings, search_memory
import uuid
from datetime import datetime

class MemoryAgent:
    async def read_memory(self, query: str = None, memory_type: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Read memory items, optionally filtered by type or semantic search.
        """
        if query:
            # Semantic search
            query_embedding = await get_embeddings([query])
            results = await search_memory(query_embedding[0], memory_type, top_k)
            # Convert to memory item format
            memories = []
            for i, doc in enumerate(results.get('documents', [])):
                memories.append({
                    "id": results.get('ids', [])[i] if i < len(results.get('ids', [])) else f"mem_{i}",
                    "type": memory_type or "UNKNOWN",
                    "content": doc,
                    "source": "vector_search",
                    "created_at": datetime.utcnow().isoformat()
                })
            return memories
        else:
            # Get all memories from DB
            db_memories = get_memory_items()
            if memory_type:
                db_memories = [m for m in db_memories if m.get("type") == memory_type]
            return db_memories

    async def write_memory(self, content: str, memory_type: str, source: str = None) -> str:
        """
        Write a new memory item to both SQLite and ChromaDB.
        """
        memory_id = str(uuid.uuid4())

        # Store in SQLite for persistent data store
        create_memory_item(memory_id, content, memory_type, source)

        # Store embeddings in ChromaDB for semantic search
        embeddings = await get_embeddings([content])
        await store_memory_embeddings([content], embeddings, [memory_type])

        return memory_id

    async def update_memory(self, memory_id: str, content: str):
        """
        Update existing memory.
        """
        await update_memory_item(memory_id, content)

    async def delete_memory(self, memory_id: str):
        """
        Soft delete memory.
        """
        await delete_memory_item(memory_id)