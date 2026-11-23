
import logging
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document


logger = logging.getLogger(__name__)

# Resolve the NEXORA project root
PROJECT_ROOT = Path(__file__).resolve().parents[4]

KNOWLEDGE_BASE_PATH = (
    PROJECT_ROOT / "knowledge_base" / "raw"
)


def discover_pdf_files() -> list[Path]:
    """
    Discover all PDF files recursively inside the raw knowledge base.
    """

    if not KNOWLEDGE_BASE_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {KNOWLEDGE_BASE_PATH}"
        )

    return sorted(
        path
        for path in KNOWLEDGE_BASE_PATH.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )


def load_pdf_documents() -> list[Document]:
    """
    Load PDFs and extract their text page by page.
    """

    pdf_files = discover_pdf_files()

    documents = []

    logger.info("Discovered %d PDF files", len(pdf_files))

    for pdf_path in pdf_files:

        try:
            loader = PyMuPDFLoader(str(pdf_path))
            pages = loader.load()

            relative_path = pdf_path.relative_to(
                KNOWLEDGE_BASE_PATH
            )

            category = (
                relative_path.parts[1]
                if len(relative_path.parts) > 2
                else "general"
            )

            for page in pages:

                # PyMuPDFLoader uses zero-based page numbers
                page_number = page.metadata.get("page", 0) + 1

                page.metadata.update({
                    "document_name": pdf_path.name,
                    "category": category,
                    "source_path": relative_path.as_posix(),
                    "file_type": "pdf",
                    "page_number": page_number
                })

                documents.append(page)

            logger.info(
                "Loaded %s (%d pages)",
                pdf_path.name,
                len(pages)
            )

        except Exception:
            logger.exception(
                "Failed to load PDF: %s",
                pdf_path
            )

    logger.info(
        "Total extracted pages: %d",
        len(documents)
    )

    return documents