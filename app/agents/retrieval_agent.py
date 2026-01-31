from typing import List, Dict, Any
from datetime import datetime
from app.utils.embeddings import get_embedding
from app.db.chroma_client import search_documents, search_memory
from app.db.sqlite_client import log_observability_event

class RetrievalAgent:
    def __init__(self, execution_id: str = None):
        self.execution_id = execution_id

    def retrieve(self, query: str, top_k: int = 5, include_memory: bool = True) -> Dict[str, Any]:
        """
        Retrieve relevant documents and memory for a query.
        """
        # Generate query embedding
        query_embedding = get_embedding(query)

        # Search documents
        doc_results = search_documents(query_embedding, n_results=top_k)

        # Search memory if requested
        memory_results = {}
        if include_memory:
            memory_results = search_memory(query_embedding, n_results=top_k//2)

        # Log retrieval event
        if self.execution_id:
            log_observability_event(
                datetime.utcnow(),
                "tool_call",
                "RetrievalAgent",
                f"Query: {query}, Docs found: {len(doc_results.get('documents', []))}",
                execution_id=self.execution_id
            )

        return {
            "documents": doc_results,
            "memory": memory_results,
            "query": query
        }

    def retrieve_with_filter(self, query: str, filters: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve with metadata filters.
        """
        # For now, simple implementation - can be enhanced with ChromaDB filtering
        results = self.retrieve(query, top_k)
        # Apply post-filtering if needed
        return results