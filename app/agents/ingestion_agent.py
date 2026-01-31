import requests
from typing import List, Dict, Any
from app.utils.embeddings import get_embeddings
from app.db.chroma_client import store_document_embeddings
from app.utils.pii_masking import mask_pii

class IngestionAgent:
    async def ingest(self, source_type: str, value: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ingest content from various sources and store in vector database.
        """
        text = await self._extract_text(source_type, value)

        if not text:
            return {"status": "error", "message": "No text extracted"}

        # Mask PII
        text = mask_pii(text)

        # Chunk text
        chunks = self._chunk_text(text)

        # Generate embeddings
        embeddings = await get_embeddings(chunks)

        # Prepare metadata
        if metadata is None:
            metadata = {}
        metadata_list = [metadata.copy() for _ in chunks]

        # Store in ChromaDB
        await store_document_embeddings(chunks, embeddings, metadata_list)

        return {
            "status": "completed",
            "chunks_indexed": len(chunks),
            "source_type": source_type
        }

    async def _extract_text(self, source_type: str, value: str) -> str:
        """Extract text based on source type."""
        if source_type == "url":
            # Assume it's a text URL, fetch content
            try:
                response = requests.get(value)
                return response.text
            except:
                return ""
        elif source_type == "text":
            return value
        elif source_type == "file":
            # For now, assume text file
            try:
                with open(value, 'r') as f:
                    return f.read()
            except:
                return ""
        else:
            return value

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Chunk text into smaller pieces with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            if start >= len(text):
                break
        return chunks