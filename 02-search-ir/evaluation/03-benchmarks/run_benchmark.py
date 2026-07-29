from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter


SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
METRICS_DIR = SEARCH_IR_DIR / "evaluation" / "02-metrics"
if str(METRICS_DIR) not in sys.path:
    sys.path.insert(0, str(METRICS_DIR))

import evaluate_metrics_bm25 as evaluation


DATA_DIR = SEARCH_IR_DIR / "sparse-retrieval" / "03-bm25" / "data" / "generated"


def run_benchmark(
    docs_path: Path,
    queries_path: Path,
    qrels_path: Path,
    *,
    model: str,
    top_ks: list[int] | None = None,
    top_k: int | None = None,
) -> dict[str, object]:
    if top_ks is not None and top_k is not None:
        raise ValueError("use either top_ks or top_k, not both")
    requested_cutoffs = (
        top_ks if top_ks is not None else [top_k if top_k is not None else 10]
    )
    cutoffs = sorted(set(requested_cutoffs))
    if not cutoffs or cutoffs[0] <= 0:
        raise ValueError("top_ks must contain positive integers")

    bm25 = evaluation.bm25_module
    documents = bm25.load_documents(docs_path)
    queries = bm25.load_queries(queries_path)
    qrels = bm25.load_qrels(qrels_path)
    flat_index, field_index = bm25.build_indexes(documents)
    search_functions = evaluation.build_search_functions(flat_index, field_index)
    selected_models = search_functions if model == "all" else (model,)

    results: dict[str, dict[str, object]] = {}
    per_query: dict[str, dict[str, object]] = {}
    for model_key in selected_models:
        model_name, search_fn = search_functions[model_key]
        started_at = perf_counter()
        details = evaluation.evaluate_model_details(
            search_fn,
            queries,
            qrels,
            cutoffs=cutoffs,
        )
        results[model_name] = {
            "metrics_by_k": {
                str(cutoff): evaluation.metrics_to_dict(details.summaries[cutoff])
                for cutoff in cutoffs
            },
            "duration_seconds": perf_counter() - started_at,
        }
        per_query[model_name] = {
            query.query_id: {
                "query": query.text,
                "topic": query.topic,
                "intent": query.intent,
                "token_count": len(bm25.tokenize(query.text)),
                "metrics_by_k": {
                    str(cutoff): evaluation.metrics_to_dict(
                        details.per_query[query.query_id][cutoff]
                    )
                    for cutoff in cutoffs
                },
            }
            for query in queries
        }

    return {
        # top_k는 기존 단일-cutoff 결과를 읽는 코드와의 호환을 위해 최댓값을 기록한다.
        "top_k": cutoffs[-1],
        "top_ks": cutoffs,
        "query_count": len(queries),
        "document_count": len(documents),
        "inputs": {
            "docs": str(docs_path),
            "queries": str(queries_path),
            "qrels": str(qrels_path),
        },
        "models": results,
        "per_query": per_query,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark BM25 retrieval models.")
    parser.add_argument("--docs", type=Path, default=DATA_DIR / "corpus.jsonl")
    parser.add_argument("--queries", type=Path, default=DATA_DIR / "queries.json")
    parser.add_argument("--qrels", type=Path, default=DATA_DIR / "qrels.json")
    parser.add_argument(
        "--model", choices=evaluation.MODEL_CHOICES, default="all"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        nargs="+",
        default=[10],
        help="Evaluate one or more cutoffs. Example: --top-k 1 3 5 10",
    )
    parser.add_argument("--output", type=Path, help="Write the JSON result to this path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cutoffs = sorted(set(args.top_k))
    if not cutoffs or cutoffs[0] <= 0:
        raise SystemExit("--top-k values must be greater than zero")

    result = run_benchmark(
        args.docs,
        args.queries,
        args.qrels,
        model=args.model,
        top_ks=cutoffs,
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
