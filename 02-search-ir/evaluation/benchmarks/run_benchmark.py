from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter


SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
METRICS_DIR = SEARCH_IR_DIR / "evaluation" / "metrics"
if str(METRICS_DIR) not in sys.path:
    sys.path.insert(0, str(METRICS_DIR))

import evaluate_metrics_bm25 as evaluation


DATA_DIR = SEARCH_IR_DIR / "bm25" / "data" / "generated"


def run_benchmark(
    docs_path: Path,
    queries_path: Path,
    qrels_path: Path,
    *,
    model: str,
    top_k: int,
) -> dict[str, object]:
    bm25 = evaluation.bm25_module
    documents = bm25.load_documents(docs_path)
    queries = bm25.load_queries(queries_path)
    qrels = bm25.load_qrels(qrels_path)
    flat_index, field_index = bm25.build_indexes(documents)
    search_functions = evaluation.build_search_functions(flat_index, field_index)
    selected_models = search_functions if model == "all" else (model,)

    results: dict[str, dict[str, float]] = {}
    for model_key in selected_models:
        model_name, search_fn = search_functions[model_key]
        started_at = perf_counter()
        metrics = evaluation.evaluate_model(search_fn, queries, qrels, k=top_k)
        results[model_name] = {
            "precision": metrics.precision,
            "recall": metrics.recall,
            "mrr": metrics.mrr,
            "ndcg": metrics.ndcg,
            "duration_seconds": perf_counter() - started_at,
        }

    return {
        "top_k": top_k,
        "query_count": len(queries),
        "document_count": len(documents),
        "inputs": {
            "docs": str(docs_path),
            "queries": str(queries_path),
            "qrels": str(qrels_path),
        },
        "models": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark BM25 retrieval models.")
    parser.add_argument("--docs", type=Path, default=DATA_DIR / "corpus.jsonl")
    parser.add_argument("--queries", type=Path, default=DATA_DIR / "queries.json")
    parser.add_argument("--qrels", type=Path, default=DATA_DIR / "qrels.json")
    parser.add_argument(
        "--model", choices=evaluation.MODEL_CHOICES, default="all"
    )
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output", type=Path, help="Write the JSON result to this path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.top_k <= 0:
        raise SystemExit("--top-k must be greater than zero")

    result = run_benchmark(
        args.docs,
        args.queries,
        args.qrels,
        model=args.model,
        top_k=args.top_k,
    )
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"{output}\n", encoding="utf-8")
        print(f"Wrote benchmark result to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
