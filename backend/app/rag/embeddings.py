
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings


MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

# Task instruction used when embedding user queries
QUERY_INSTRUCTION = (
    "Given a question about an enterprise business operation, "
    "retrieve relevant company documents, policies, SOPs, "
    "and operational procedures that answer the question."
)


class QwenEmbeddings(Embeddings):
    """
    Local embedding implementation using Qwen3-Embedding-0.6B.
    """

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """
        Generate embeddings for document chunks.
        """

        vectors = self.model.encode(
            texts,
            batch_size=16,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        return vectors.tolist()

    def embed_query(
        self,
        text: str
    ) -> list[float]:
        """
        Generate an instruction-aware embedding for a user query.
        """

        query = (
            f"Instruct: {QUERY_INSTRUCTION}\n"
            f"Query: {text}"
        )

        vector = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        return vector.tolist()


@lru_cache(maxsize=1)
def get_embedding_model() -> QwenEmbeddings:
    """
    Load the embedding model once and reuse it.
    """

    return QwenEmbeddings()
