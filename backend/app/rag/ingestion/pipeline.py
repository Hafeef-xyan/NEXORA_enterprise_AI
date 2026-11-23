import logging
from dataclasses import dataclass
from app.rag.vector_store import get_vector_store
from langchain_core.documents import Document

from app.rag.ingestion.loader import (
    discover_pdf_files,
    load_pdf_documents,
)
from app.rag.ingestion.chunker import chunk_documents


logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    total_files: int
    total_pages: int
    total_chunks: int
    chunks: list[Document]


def run_ingestion_pipeline() -> IngestionResult:
    """
    Coordinate document loading and chunking.

    Embedding generation and vector storage
    will be integrated in later stages.
    """

    logger.info("Starting NEXORA ingestion pipeline")

    # Step 1: Discover source documents
    pdf_files = discover_pdf_files()

    if not pdf_files:
        raise ValueError(
            "No PDF documents found in the knowledge base"
        )

    # Step 2: Load and extract document text
    documents = load_pdf_documents()

    if not documents:
        raise ValueError(
            "No PDF pages were successfully extracted"
        )

    # Step 3: Split extracted pages into chunks
    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError(
            "No text chunks were generated"
        )
    
    # Step 4: Store chunks and embeddings in pgvector
    print(f"Preparing to store {len(chunks)} chunks...", flush=True)

    vector_store = get_vector_store()

    batch_size = 16

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        vector_store.add_documents(documents=batch)

        completed = min(start + batch_size, len(chunks))

        print(
            f"Stored {completed}/{len(chunks)} chunks",
            flush=True,
        )

    logger.info("Ingestion pipeline completed successfully")

    logger.info(
        "Ingestion completed: %d files, %d pages, %d chunks",
        len(pdf_files),
        len(documents),
        len(chunks),
    )

    return IngestionResult(
        total_files=len(pdf_files),
        total_pages=len(documents),
        total_chunks=len(chunks),
        chunks=chunks,
    )

if __name__ == "__main__":
    run_ingestion_pipeline()