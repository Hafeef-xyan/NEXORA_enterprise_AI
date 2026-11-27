
from langchain_core.documents import Document

from app.rag.vector_store import get_vector_store
from app.rag.retrieval.reranker import DocumentReranker


class DocumentRetriever:
    def __init__(
        self,
        top_k: int = 5,
        candidate_k: int = 15,
    ):
        self.vector_store = get_vector_store()

        self.top_k = top_k
        self.candidate_k = max(candidate_k, top_k)

        self.reranker = DocumentReranker(
            top_k=self.top_k,
            score_threshold=0.50,
        )

    def retrieve(
        self,
        query: str,
        filters: dict | None = None,
    ) -> list[Document]:

        if not query.strip():
            raise ValueError("Query cannot be empty")

        # Stage 1: Hybrid retrieval
        candidates = self.vector_store.similarity_search(
            query=query,
            k=self.candidate_k,
            filter=filters,
        )

        # Stage 2: Cross-encoder reranking
        documents = self.reranker.rerank(
            query=query,
            documents=candidates,
        )

        return documents
