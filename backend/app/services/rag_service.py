
from pathlib import Path

from app.rag.retrieval.pipeline import RetrievalPipeline


class RAGService:
    def __init__(self, top_k: int = 5):
        self.retrieval_pipeline = RetrievalPipeline(top_k=top_k)

    def query(self, query: str) -> dict:
        result = self.retrieval_pipeline.run(query)

        sources = []

        for source in result["sources"]:
            source_path = source.get("source")

            # Return only the document filename,
            # not the full local filesystem path.
            filename = (
                Path(str(source_path).replace("\\", "/")).name
                if source_path
                else None
            )

            sources.append(
                {
                    "source": filename,
                    "page": source.get("page"),
                    "category": source.get("category"),
                }
            )

        return {
            "query": result["query"],
            "context": result["context"],
            "retrieved_count": len(result["documents"]),
            "sources": sources,
        }
