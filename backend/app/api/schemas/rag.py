
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question to search in the NEXORA knowledge base",
    )


class RAGSource(BaseModel):
    source: str | None = None
    page: int | None = None
    category: str | None = None


class RAGQueryResponse(BaseModel):
    query: str
    context: str
    retrieved_count: int
    sources: list[RAGSource]
