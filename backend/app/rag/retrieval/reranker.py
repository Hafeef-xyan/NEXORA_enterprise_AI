
from functools import lru_cache

import torch
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document


MODEL_NAME = "BAAI/bge-reranker-base"


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    device = "cuda" if torch.cuda.is_available() else "cpu"

    return CrossEncoder(
        MODEL_NAME,
        device=device,
    )


class DocumentReranker:
    def __init__(
        self,
        top_k: int = 5,
        score_threshold: float = 0.75,
    ):
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.model = get_reranker()

    def rerank_with_scores(
        self,
        query: str,
        documents: list[Document],
    ) -> list[tuple[Document, float]]:

        if not documents:
            return []

        pairs = [
            (query, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked_documents = sorted(
            zip(documents, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            (document, float(score))
            for document, score in ranked_documents
        ]

    def rerank(
        self,
        query: str,
        documents: list[Document],
    ) -> list[Document]:

        ranked_documents = self.rerank_with_scores(
            query=query,
            documents=documents,
        )

        # Remove chunks below the relevance threshold
        relevant_documents = [
            (document, score)
            for document, score in ranked_documents
            if score >= self.score_threshold
        ]

        # Return only the strongest relevant chunks
        return [
            document
            for document, score in relevant_documents[:self.top_k]
        ]
