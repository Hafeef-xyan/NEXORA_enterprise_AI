
import hashlib
import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


logger = logging.getLogger(__name__)


CHUNK_SIZE = 1500
CHUNK_OVERLAP = 250


def generate_chunk_id(
    source_path: str,
    page_number: int,
    chunk_index: int
) -> str:
    """
    Generate a deterministic ID for each chunk.
    """

    unique_value = (
        f"{source_path}:{page_number}:{chunk_index}"
    )

    return hashlib.sha256(
        unique_value.encode("utf-8")
    ).hexdigest()


def chunk_documents(
    documents: list[Document]
) -> list[Document]:
    """
    Split loaded documents into smaller chunks
    while preserving their metadata.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ],
        add_start_index=True
    )

    chunks = []

    for document in documents:

        if not document.page_content.strip():
            continue

        page_chunks = splitter.split_documents(
            [document]
        )

        for chunk_index, chunk in enumerate(page_chunks):

            page_number = chunk.metadata.get(
                "page_number", 1
            )

            source_path = chunk.metadata.get(
                "source_path", "unknown"
            )

            chunk.metadata.update({
                "chunk_index": chunk_index,
                "chunk_id": generate_chunk_id(
                    source_path,
                    page_number,
                    chunk_index
                ),
                "chunk_size": len(chunk.page_content)
            })

            chunks.append(chunk)

    logger.info(
        "Created %d chunks from %d pages",
        len(chunks),
        len(documents)
    )

    return chunks
