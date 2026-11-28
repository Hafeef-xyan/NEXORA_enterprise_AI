
from pathlib import Path

from langchain_ollama import ChatOllama

from app.core.llms import rag_generation_llm
from app.rag.retrieval.pipeline import RetrievalPipeline
from app.rag.generation.answer_generator import AnswerGenerator
from app.rag.generation.pipeline import GenerationPipeline


class RAGService:

    def __init__(self, top_k: int = 5):

        # Initialize retrieval pipeline
        self.retrieval_pipeline = RetrievalPipeline(
            top_k=top_k
        )


        # Initialize answer generator
        answer_generator = AnswerGenerator(
            llm=rag_generation_llm
        )

        # Initialize generation pipeline
        self.generation_pipeline = GenerationPipeline(
            answer_generator=answer_generator
        )

    def query(self, query: str) -> dict:

        # Step 1: Retrieve and rerank documents
        result = self.retrieval_pipeline.run(query)

        documents = result["documents"]

        # Step 2: Generate answer using retrieved documents
        answer = self.generation_pipeline.run(
            question=query,
            documents=documents,
        )

        # Step 3: Prepare source information
        sources = []

        for source in result["sources"]:

            source_path = source.get("source")

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
            "query": query,
            "answer": answer,
            "retrieved_count": len(documents),
            "sources": sources,
        }
