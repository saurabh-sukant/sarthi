import openai
from typing import List
from app.config import settings

class EmbeddingService:
    """Service for generating embeddings using OpenAI."""

    def __init__(self):
        openai.api_key = settings.openai_api_key

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = await openai.Embedding.acreate(
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * 1536  # Fallback for ada-002

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            response = await openai.Embedding.acreate(
                input=texts,
                model="text-embedding-ada-002"
            )
            return [data['embedding'] for data in response['data']]
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [[0.0] * 1536 for _ in texts]

# Global instance
embedding_service = EmbeddingService()

async def get_embedding(text: str) -> List[float]:
    """Convenience function for single embedding."""
    return await embedding_service.generate_embedding(text)

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Convenience function for batch embeddings."""
    return await embedding_service.generate_embeddings(texts)