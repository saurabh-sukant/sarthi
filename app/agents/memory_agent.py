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
        Falls back to keyword search if embeddings fail (e.g., API key issues).
        """
        if query:
            # Try semantic search first
            try:
                query_embedding = await get_embeddings([query])
                # Check if we got valid embeddings (not all zeros indicating failure)
                if query_embedding[0] and any(query_embedding[0]):
                    results = await search_memory(query_embedding[0], memory_type, top_k, query_text=query)
                    # Convert to memory item format
                    # Results structure: {"documents": [[...]], "ids": [[...]], "metadatas": [[...]]}
                    memories = []
                    docs_list = results.get('documents', [[]])[0] if results.get('documents') else []
                    ids_list = results.get('ids', [[]])[0] if results.get('ids') else []
                    metas_list = results.get('metadatas', [[]])[0] if results.get('metadatas') else []
                    
                    for i, doc in enumerate(docs_list):
                        memories.append({
                            "id": ids_list[i] if i < len(ids_list) else f"mem_{i}",
                            "type": memory_type or (metas_list[i].get('type', 'UNKNOWN') if i < len(metas_list) else 'UNKNOWN'),
                            "content": doc,
                            "source": "vector_search",
                            "created_at": datetime.utcnow().isoformat()
                        })
                    if memories:
                        return memories
            except Exception as e:
                print(f"Semantic search failed, falling back to keyword search: {e}")
            
            # Fallback: keyword-based search from SQLite
            db_memories = get_memory_items()
            if memory_type:
                db_memories = [m for m in db_memories if m.get("type") == memory_type]
            
            # Simple keyword matching: prioritize memories that contain query words
            query_words = set(query.lower().split())
            scored_memories = []
            for mem in db_memories:
                content = mem.get("content", "").lower()
                # Count matching words
                matches = sum(1 for word in query_words if word in content)
                if matches > 0:
                    scored_memories.append((matches, mem))
            
            # Sort by match count (descending) and return top_k
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            return [mem for _, mem in scored_memories[:top_k]]
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

        # Try to store embeddings in ChromaDB for semantic search
        # If embeddings fail (e.g., API key issue), it still gets stored in SQLite
        try:
            embeddings = await get_embeddings([content])
            # Only store if we got valid embeddings
            if embeddings[0] and any(embeddings[0]):
                await store_memory_embeddings([content], embeddings, [memory_type])
        except Exception as e:
            print(f"Warning: Failed to store embeddings (will use keyword search): {e}")

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