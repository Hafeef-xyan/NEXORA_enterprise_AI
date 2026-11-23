from langchain_core.documents import Document

from app.rag.vector_store import get_vector_store


class DocumentRetriever:
    def __init__(self, top_k: int = 5):
        self.vector_store = get_vector_store()
        self.top_k = top_k

    def retrieve(self, query: str) -> list[Document]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        documents = self.vector_store.similarity_search(
            query=query,
            k=self.top_k,
        )

        return documents