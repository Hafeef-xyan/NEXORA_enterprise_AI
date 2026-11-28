"""
Benchmark two local Ollama models sequentially and compare generation speed.
Install dependency: pip install requests
Ensure Ollama is running before starting this script.
"""

import statistics
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELS = [
    "qwen3:8b",
    "qwen2.5:14b-instruct-q4_K_M",
]

PROMPT = """
You are an assistant for an enterprise company.
Explain why inventory records should be updated immediately after
a warehouse stock transfer. Give a clear, practical answer.
"""

NUM_PREDICT = 180
TRIALS = 3
WARMUP = True


def generate(model, prompt, warmup=False):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 40 if warmup else NUM_PREDICT,
            "num_ctx": 4096,
        },
        # Unload after each request; benchmark models one at a time.
        "keep_alive": 0,
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=900)
    response.raise_for_status()
    return response.json()


def benchmark_model(model):
    print("\n" + "=" * 65)
    print("Model:", model)

    if WARMUP:
        print("Warm-up...")
        generate(model, PROMPT, warmup=True)

    trial_results = []

    for trial in range(1, TRIALS + 1):
        result = generate(model, PROMPT)
        tokens = result.get("eval_count", 0)
        eval_seconds = result.get("eval_duration", 0) / 1e9
        tps = tokens / eval_seconds if eval_seconds else 0
        total_seconds = result.get("total_duration", 0) / 1e9

        trial_results.append((tps, total_seconds))
        print(
            f"Trial {trial}: {tokens} generated tokens | "
            f"{tps:.2f} tokens/sec | total {total_seconds:.2f}s"
        )

    avg_tps = statistics.mean(x[0] for x in trial_results)
    avg_total = statistics.mean(x[1] for x in trial_results)
    print(f"Average generation speed: {avg_tps:.2f} tokens/sec")
    print(f"Average total request time: {avg_total:.2f}s")

    return model, avg_tps, avg_total


def main():
    try:
        requests.get("http://localhost:11434/api/tags", timeout=5).raise_for_status()
    except requests.RequestException as exc:
        print("Cannot connect to Ollama. Make sure Ollama is running.")
        print("Details:", exc)
        return

    summaries = []
    for model in MODELS:
        try:
            summaries.append(benchmark_model(model))
        except requests.RequestException as exc:
            print(f"Could not test {model}: {exc}")
            print("Check the model name with: ollama list")

    print("\n" + "=" * 65)
    print("FINAL COMPARISON")
    print(f"{'Model':40} {'Avg tokens/sec':>15} {'Avg total (s)':>14}")
    print("-" * 72)
    for model, tps, total in summaries:
        print(f"{model[:40]:40} {tps:15.2f} {total:14.2f}")

    if summaries:
        fastest = max(summaries, key=lambda row: row[1])
        print(f"\nFastest generation throughput in this test: {fastest[0]}")


if __name__ == "__main__":
    main()
