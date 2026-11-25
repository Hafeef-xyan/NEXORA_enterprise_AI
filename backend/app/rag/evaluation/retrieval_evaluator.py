
import argparse
import json
from pathlib import Path

from app.rag.retrieval.pipeline import RetrievalPipeline


BACKEND_DIR = Path(__file__).resolve().parents[3]

DEFAULT_DATASET = (
    BACKEND_DIR
    / "evaluation"
    / "datasets"
    / "retrieval_eval.json"
)


def normalize_source(source: str | None) -> str:
    """Normalize a source path to a lowercase filename."""
    if not source:
        return ""

    return source.replace("\\", "/").split("/")[-1].lower()


def evaluate_query(
    pipeline: RetrievalPipeline,
    item: dict,
    k: int,
) -> dict:
    result = pipeline.run(item["query"])

    expected_sources = {
        normalize_source(source)
        for source in item["expected_sources"]
    }

    # Preserve chunk ranking. Do not deduplicate by source.
    retrieved_documents = result["documents"][:k]

    retrieved_sources = [
        normalize_source(document.metadata.get("source"))
        for document in retrieved_documents
    ]

    # A chunk is relevant when its source is an expected source.
    relevant_chunks = [
        source
        for source in retrieved_sources
        if source in expected_sources
    ]

    # Chunk-level Precision@K.
    precision = (
        len(relevant_chunks) / len(retrieved_documents)
        if retrieved_documents
        else 0.0
    )

    # Source-level Recall@K:
    # expected source documents found in top K / all expected sources.
    found_sources = set(retrieved_sources) & expected_sources

    recall = (
        len(found_sources) / len(expected_sources)
        if expected_sources
        else 0.0
    )

    # Chunk-level MRR: reciprocal rank of the first relevant chunk.
    reciprocal_rank = 0.0

    for rank, source in enumerate(retrieved_sources, start=1):
        if source in expected_sources:
            reciprocal_rank = 1.0 / rank
            break

    return {
        "id": item["id"],
        "query": item["query"],
        "expected_sources": sorted(expected_sources),
        "retrieved_sources": retrieved_sources,
        f"precision@{k}": precision,
        f"source_recall@{k}": recall,
        "mrr": reciprocal_rank,
    }


def run_evaluation(
    dataset_path: Path = DEFAULT_DATASET,
    k: int = 5,
) -> None:
    with dataset_path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not dataset:
        raise ValueError("Evaluation dataset is empty.")

    pipeline = RetrievalPipeline(top_k=k)

    results = [
        evaluate_query(pipeline, item, k)
        for item in dataset
    ]

    precision_key = f"precision@{k}"
    recall_key = f"source_recall@{k}"

    average_precision = sum(
        result[precision_key] for result in results
    ) / len(results)

    average_source_recall = sum(
        result[recall_key] for result in results
    ) / len(results)

    mean_reciprocal_rank = sum(
        result["mrr"] for result in results
    ) / len(results)

    print("\n" + "=" * 60)
    print("NEXORA RETRIEVAL EVALUATION")
    print("=" * 60)

    for result in results:
        print(f"\n{result['id']}: {result['query']}")
        print(f"Expected:  {result['expected_sources']}")
        print(f"Retrieved: {result['retrieved_sources']}")

        print(
            f"Chunk Precision@{k}: "
            f"{result[precision_key]:.3f}"
        )

        print(
            f"Source Recall@{k}: "
            f"{result[recall_key]:.3f}"
        )

        print(f"Chunk MRR: {result['mrr']:.3f}")

    print("\n" + "-" * 60)
    print("AGGREGATE RESULTS")
    print("-" * 60)
    print(f"Evaluation queries: {len(results)}")
    print(f"Average Chunk Precision@{k}: {average_precision:.3f}")
    print(f"Average Source Recall@{k}:   {average_source_recall:.3f}")
    print(f"Mean Chunk Reciprocal Rank:  {mean_reciprocal_rank:.3f}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate NEXORA RAG retrieval quality"
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to retrieval evaluation JSON dataset",
    )

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of top retrieved chunks to evaluate",
    )

    args = parser.parse_args()

    run_evaluation(
        dataset_path=args.dataset,
        k=args.k,
    )
