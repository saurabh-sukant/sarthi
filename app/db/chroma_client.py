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

async def search_documents(query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
    """Search documents by embedding."""
    collection = client.get_or_create_collection("documents")
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    return results

async def store_memory_embeddings(memories: List[str], embeddings: List[List[float]], memory_types: List[str]):
    """Store memory items with embeddings."""
    collection = client.get_or_create_collection("memory")
    ids = [f"mem_{uuid.uuid4()}" for _ in range(len(memories))]
    metadata = [{"type": memory_type} for memory_type in memory_types]
    collection.add(ids=ids, embeddings=embeddings, documents=memories, metadatas=metadata)

async def search_memory(query_embedding: List[float], memory_type: str = None, n_results: int = 5) -> Dict[str, Any]:
    """Search memory by embedding and optional type."""
    collection = client.get_or_create_collection("memory")
    if memory_type:
        where = {"type": memory_type}
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results, where=where)
    else:
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    return results