
import json
from pathlib import Path

from app.rag.vector_store import get_vector_store
from app.rag.retrieval.reranker import DocumentReranker


# ============================================================
# Configuration
# ============================================================

CANDIDATE_K = 15
FINAL_TOP_K = 5

# Diagnostic setting:
# First check retrieval quality without aggressively filtering.
RELEVANCE_THRESHOLD = 0.50

# Update this path according to your project structure.
DATASET_PATH = (
    Path(__file__).parent
    / "evaluation"
    / "datasets"
    / "retrieval_eval.json"
)


# ============================================================
# Utility Functions
# ============================================================

def print_separator():
    print("=" * 100)


def load_evaluation_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {DATASET_PATH}"
        )

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    return dataset


def normalize_source(source):
    """
    Normalize source names so that paths and filenames
    can be compared consistently.
    """
    return Path(str(source)).name.lower().strip()


def source_matches(actual_source, expected_sources):
    """
    Check whether the retrieved source matches
    any expected source document.
    """
    actual = normalize_source(actual_source)

    expected = {
        normalize_source(source)
        for source in expected_sources
    }

    return actual in expected


# ============================================================
# Retrieval Evaluation
# ============================================================

def run_retrieval_test():

    evaluation_dataset = load_evaluation_dataset()

    vector_store = get_vector_store()

    reranker = DocumentReranker(
        top_k=FINAL_TOP_K,
        score_threshold=RELEVANCE_THRESHOLD,
    )

    total_questions = len(evaluation_dataset)

    total_candidates = 0
    total_filtered = 0
    total_final = 0

    source_hits = 0
    zero_result_questions = 0

    print_separator()
    print("RAG RETRIEVAL EVALUATION")
    print_separator()

    print(f"Dataset: {DATASET_PATH}")
    print(f"Total questions: {total_questions}")
    print(f"Candidate K: {CANDIDATE_K}")
    print(f"Final Top K: {FINAL_TOP_K}")
    print(f"Relevance threshold: {RELEVANCE_THRESHOLD}")

    # --------------------------------------------------------
    # Evaluate each question
    # --------------------------------------------------------

    for index, item in enumerate(evaluation_dataset, start=1):

        question_id = item.get("id", index)
        question = item["query"]

        expected_sources = item.get(
            "expected_sources",
            [],
        )

        print_separator()
        print(f"QUESTION {index}/{total_questions}")
        print(f"ID: {question_id}")
        print(f"QUERY: {question}")
        print(f"EXPECTED SOURCES: {expected_sources}")
        print_separator()

        # Step 1: Retrieve candidate chunks
        candidates = vector_store.similarity_search(
            query=question,
            k=CANDIDATE_K,
        )

        total_candidates += len(candidates)

        # Step 2: Rerank candidate chunks
        ranked_results = reranker.rerank_with_scores(
            query=question,
            documents=candidates,
        )

        # Step 3: Apply relevance threshold
        relevant_results = [
            (document, score)
            for document, score in ranked_results
            if score >= RELEVANCE_THRESHOLD
        ]

        filtered_count = (
            len(ranked_results) - len(relevant_results)
        )

        # Step 4: Select final top-k chunks
        final_results = relevant_results[:FINAL_TOP_K]

        total_filtered += filtered_count
        total_final += len(final_results)

        if not final_results:
            zero_result_questions += 1

        # ----------------------------------------------------
        # Source evaluation
        # ----------------------------------------------------

        retrieved_sources = []

        for document, score in final_results:

            source = document.metadata.get(
                "source",
                "Unknown source",
            )

            retrieved_sources.append(source)

        source_hit = any(
            source_matches(source, expected_sources)
            for source in retrieved_sources
        )

        if source_hit:
            source_hits += 1

        print("\nRETRIEVAL STATISTICS")
        print(f"Candidates retrieved: {len(candidates)}")
        print(f"Reranked candidates: {len(ranked_results)}")
        print(f"Chunks filtered: {filtered_count}")
        print(f"Final chunks returned: {len(final_results)}")

        print(
            f"Expected source retrieved: "
            f"{'PASS' if source_hit else 'FAIL'}"
        )

        # ----------------------------------------------------
        # Display reranked candidates
        # ----------------------------------------------------

        print("\nRERANKED CANDIDATES")

        if not ranked_results:
            print("No candidates returned.")

        for rank, (document, score) in enumerate(
            ranked_results,
            start=1,
        ):

            status = (
                "PASS"
                if score >= RELEVANCE_THRESHOLD
                else "FILTERED"
            )

            source = document.metadata.get(
                "source",
                "Unknown source",
            )

            print(
                f"\n[{rank}] "
                f"Score: {score:.4f} | {status}"
            )

            print(f"Source: {source}")

            print(
                document.page_content[:300]
                .replace("\n", " ")
            )

        # ----------------------------------------------------
        # Display final context
        # ----------------------------------------------------

        print("\nFINAL RETRIEVED CONTEXT")

        if not final_results:
            print("No chunks passed the relevance threshold.")

        for rank, (document, score) in enumerate(
            final_results,
            start=1,
        ):

            source = document.metadata.get(
                "source",
                "Unknown source",
            )

            print(
                f"\nFinal Rank: {rank} | "
                f"Score: {score:.4f}"
            )

            print(f"Source: {source}")
            print(document.page_content[:500])

        print("\n")


    # ========================================================
    # Overall Evaluation Summary
    # ========================================================

    print_separator()
    print("RETRIEVAL EVALUATION SUMMARY")
    print_separator()

    print(f"Total questions: {total_questions}")
    print(f"Total candidates retrieved: {total_candidates}")
    print(f"Total chunks filtered: {total_filtered}")
    print(f"Total final chunks returned: {total_final}")

    print(
        f"Questions with zero results: "
        f"{zero_result_questions}"
    )

    print(
        f"Expected source successfully retrieved: "
        f"{source_hits}/{total_questions}"
    )

    if total_questions:

        source_recall_at_k = (
            source_hits / total_questions
        ) * 100

        average_final_chunks = (
            total_final / total_questions
        )

        print(
            f"Source Recall@{FINAL_TOP_K}: "
            f"{source_recall_at_k:.2f}%"
        )

        print(
            f"Average final chunks per question: "
            f"{average_final_chunks:.2f}"
        )

    print_separator()


if __name__ == "__main__":
    run_retrieval_test()
