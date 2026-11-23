import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
from functools import lru_cache

from langchain_postgres import PGEngine, PGVectorStore

from app.core.config import settings
from app.rag.embeddings import get_embedding_model


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


def store_documents(documents):
    """
    Generate embeddings and store LangChain documents.
    """

    vector_store = get_vector_store()

    return vector_store.add_documents(
        documents=documents
    )


def search_similar_documents(
    query: str,
    k: int = 5
):
    """
    Retrieve the most relevant documents for a query.
    """

    vector_store = get_vector_store()

    return vector_store.similarity_search(
        query=query,
        k=k
    )
