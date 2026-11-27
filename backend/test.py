
from app.rag.retrieval.reranker import DocumentReranker
from app.rag.vector_store import get_vector_store

query = "What is NEXORA's employee leave policy?"

vector_store = get_vector_store()

candidates = vector_store.similarity_search(
    query=query,
    k=15,
)

reranker = DocumentReranker(
    top_k=5,
    score_threshold=0.95,
)

ranked_results = reranker.rerank_with_scores(
    query=query,
    documents=candidates,
)

for rank, (document, score) in enumerate(
    ranked_results,
    start=1,
):
    print(f"\nRank: {rank}")
    print(f"Score: {score:.4f}")
    print(f"Source: {document.metadata.get('source')}")
    print(document.page_content[:250])
