import chromadb
import uuid
from typing import List, Dict, Any
from app.config import settings

client = chromadb.PersistentClient(path=settings.chroma_path)

async def init_chroma_collections():
    """Initialize ChromaDB collections."""
    # Documents collection for RAG
    client.get_or_create_collection("documents")
    # Memory collection for episodic/semantic memory
    client.get_or_create_collection("memory")

async def store_document_embeddings(chunks: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None):
    """Store document chunks with embeddings."""
    collection = client.get_or_create_collection("documents")
    ids = [f"doc_{uuid.uuid4()}" for _ in range(len(chunks))]
    if metadata is None:
        metadata = [{}] * len(chunks)
    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadata)

async def search_documents(query_embedding: List[float], n_results: int = 5, query_text: str = None) -> Dict[str, Any]:
    """Search documents by embedding with keyword fallback."""
    collection = client.get_or_create_collection("documents")
    
    # Try semantic search first
    try:
        if query_embedding and any(query_embedding):  # Check if embedding is valid
            results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
            if results.get("documents") and any(results.get("documents", [[]])[0]):
                return results
    except Exception as e:
        print(f"Semantic search failed: {e}")
    
    # Fallback to keyword search if embedding search fails or returns empty
    if query_text:
        print(f"Falling back to keyword search for: {query_text}")
        all_docs = collection.get()
        if not all_docs.get("documents"):
            return {"documents": [[]], "metadatas": [[]], "ids": [[]]}
        
        # Extract keywords from query
        keywords = set(query_text.lower().split())
        keywords.discard("and")
        keywords.discard("or")
        keywords.discard("the")
        keywords.discard("a")
        keywords.discard("is")
        
        # Score documents by keyword matches
        scored_docs = []
        for i, doc in enumerate(all_docs.get("documents", [])):
            doc_lower = doc.lower() if doc else ""
            score = sum(1 for kw in keywords if kw in doc_lower)
            if score > 0:
                scored_docs.append((score, i, doc))
        
        # Sort by score (descending) and get top n
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = scored_docs[:n_results]
        
        # Format as Chroma results
        doc_ids = all_docs.get("ids", [])
        doc_metadatas = all_docs.get("metadatas", [])
        
        return {
            "documents": [[doc[2] for doc in top_docs]] if top_docs else [[]],
            "metadatas": [[doc_metadatas[doc[1]] for doc in top_docs]] if top_docs else [[]],
            "ids": [[doc_ids[doc[1]] for doc in top_docs]] if top_docs else [[]]
        }
    
    return {"documents": [[]], "metadatas": [[]], "ids": [[]]}

async def store_memory_embeddings(memories: List[str], embeddings: List[List[float]], memory_types: List[str]):
    """Store memory items with embeddings."""
    collection = client.get_or_create_collection("memory")
    ids = [f"mem_{uuid.uuid4()}" for _ in range(len(memories))]
    metadata = [{"type": memory_type} for memory_type in memory_types]
    collection.add(ids=ids, embeddings=embeddings, documents=memories, metadatas=metadata)

async def search_memory(query_embedding: List[float], memory_type: str = None, n_results: int = 5, query_text: str = None) -> Dict[str, Any]:
    """Search memory by embedding and optional type, with keyword fallback."""
    collection = client.get_or_create_collection("memory")
    
    # Try semantic search first
    try:
        if query_embedding and any(query_embedding):  # Check if embedding is valid
            if memory_type:
                where = {"type": memory_type}
                results = collection.query(query_embeddings=[query_embedding], n_results=n_results, where=where)
            else:
                results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
            
            if results.get("documents") and any(results.get("documents", [[]])[0]):
                return results
    except Exception as e:
        print(f"Semantic memory search failed: {e}")
    
    # Fallback to keyword search if embedding search fails or returns empty
    if query_text:
        print(f"Falling back to keyword memory search for: {query_text}")
        all_memories = collection.get()
        if not all_memories.get("documents"):
            return {"documents": [[]], "metadatas": [[]], "ids": [[]]}
        
        # Extract keywords from query
        keywords = set(query_text.lower().split())
        keywords.discard("and")
        keywords.discard("or")
        keywords.discard("the")
        keywords.discard("a")
        keywords.discard("is")
        
        # Score memories by keyword matches
        scored_memories = []
        for i, memory in enumerate(all_memories.get("documents", [])):
            memory_lower = memory.lower() if memory else ""
            score = sum(1 for kw in keywords if kw in memory_lower)
            if score > 0:
                # Filter by memory_type if specified
                if memory_type:
                    mem_metadata = all_memories.get("metadatas", [{}])[i] if i < len(all_memories.get("metadatas", [])) else {}
                    if mem_metadata.get("type") != memory_type:
                        continue
                scored_memories.append((score, i, memory))
        
        # Sort by score (descending) and get top n
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = scored_memories[:n_results]
        
        # Format as Chroma results
        mem_ids = all_memories.get("ids", [])
        mem_metadatas = all_memories.get("metadatas", [])
        
        return {
            "documents": [[mem[2] for mem in top_memories]] if top_memories else [[]],
            "metadatas": [[mem_metadatas[mem[1]] for mem in top_memories]] if top_memories else [[]],
            "ids": [[mem_ids[mem[1]] for mem in top_memories]] if top_memories else [[]]
        }
    
    return {"documents": [[]], "metadatas": [[]], "ids": [[]]}