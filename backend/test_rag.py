import asyncio
import sys

from functools import lru_cache

from langchain_postgres import PGEngine, PGVectorStore

from app.core.config import settings
from app.rag.embeddings import get_embedding_model


if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.rag.retrieval.pipeline import RetrievalPipeline

from app.rag.retrieval.pipeline import RetrievalPipeline


TABLE_NAME = "nexora_document_chunks"
VECTOR_SIZE = 1024


@lru_cache(maxsize=1)
def get_pg_engine() -> PGEngine:
    """
    Create and reuse the PostgreSQL vector engine.
    """

    return PGEngine.from_connection_string(
        url=settings.DATABASE_URL
    )


@lru_cache(maxsize=1)
def get_vector_store() -> PGVectorStore:
    """
    Initialize and return the NEXORA vector store.
    """

    engine = get_pg_engine()

    embedding_model = get_embedding_model()

    return PGVectorStore.create_sync(
        engine=engine,
        embedding_service=embedding_model,
        table_name=TABLE_NAME
    )


def initialize_vector_store():
    """
    Create the vector storage table if it doesn't exist.
    """

    engine = get_pg_engine()

    engine.init_vectorstore_table(
        table_name=TABLE_NAME,
        vector_size=VECTOR_SIZE
    )

    return get_vector_store()

def test_rag_retrieval():
    pipeline = RetrievalPipeline(top_k=5)

    query = "What is NEXORA's employee leave policy?"

    result = pipeline.run(query)

    print("\n" + "=" * 60)
    print("QUERY:", result["query"])
    print("=" * 60)

    print("\nRETRIEVED CONTEXT:\n")
    print(result["context"])

    print("\nSOURCES:\n")
    for source in result["sources"]:
        print(source)

    assert result["documents"], "No documents were retrieved"
    assert result["context"].strip(), "Retrieved context is empty"

    print("\nRAG RETRIEVAL TEST PASSED")


if __name__ == "__main__":
    test_rag_retrieval()