
import logging

from fastapi import APIRouter, HTTPException

from app.api.schemas.rag import (
    RAGQueryRequest,
    RAGQueryResponse,
)
from app.services.rag_service import RAGService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)

rag_service = RAGService()


@router.post("/query", response_model=RAGQueryResponse)
def query_rag(request: RAGQueryRequest):
    try:
        result = rag_service.query(request.query)
        return result
    except Exception:
        logger.exception("RAG query failed")

        raise HTTPException(
            status_code=500,
            detail="RAG query failed",
        )
