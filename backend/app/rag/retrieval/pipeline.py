from app.rag.retrieval.retriever import DocumentRetriever


class RetrievalPipeline:
    def __init__(self, top_k: int = 5):
        self.retriever = DocumentRetriever(top_k=top_k)

    def run(self, query: str) -> dict:
        documents = self.retriever.retrieve(query)

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        sources = [
            {
                "source": document.metadata.get("source"),
                "page": document.metadata.get("page"),
                "category": document.metadata.get("category"),
            }
            for document in documents
        ]

        return {
            "query": query,
            "context": context,
            "documents": documents,
            "sources": sources,
        }