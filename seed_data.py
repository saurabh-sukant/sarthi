import asyncio
from app.db.sqlite_client import init_db
from app.db.chroma_client import init_chroma_collections, store_document_embeddings
from app.utils.embeddings import get_embeddings

async def seed_data():
    """Seed initial data for testing."""
    print("Initializing databases...")
    await init_db()
    await init_chroma_collections()

    print("Seeding sample documents...")

    # Sample documents
    sample_docs = [
        "Gateway timeout errors typically occur when the service is overloaded. Resolution: Restart the gateway service and monitor load.",
        "Database connection failures happen due to network issues or credential problems. Check network connectivity and verify credentials.",
        "Authentication failures occur when tokens expire or are invalid. Users should re-authenticate and check token validity.",
        "Memory leaks in application servers cause performance degradation. Monitor heap usage and restart services as needed.",
        "SSL certificate expiration causes connection errors. Renew certificates before expiration and update configurations."
    ]

    # Generate embeddings
    embeddings = await get_embeddings(sample_docs)

    # Store in ChromaDB
    await store_document_embeddings(sample_docs, embeddings)

    print(f"Seeded {len(sample_docs)} documents.")

if __name__ == "__main__":
    asyncio.run(seed_data())