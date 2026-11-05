"""같은 데이터와 cutoff 조건에서 BM25 계열 모델을 비교하고 JSON 결과를 만든다.

출력 JSON
- models: 모델별 cutoff 평균 지표와 소요 시간
- per_query: query별 지표와 메타데이터(topic, intent, concept_id, token_count)
  -> 05-slice-analysis, 06-significance의 입력으로 사용한다.

실행: python 02-search-ir/05-evaluation/03-benchmarks/run_benchmark.py --top-k 1 3 5 10 50 --output .../generated/bm25.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter


SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
METRICS_DIR = SEARCH_IR_DIR / "05-evaluation" / "02-metrics"
# 폴더 이름이 숫자로 시작해 패키지 import가 안 되므로 sys.path에 직접 추가한다.
if str(METRICS_DIR) not in sys.path:
    sys.path.insert(0, str(METRICS_DIR))

import evaluate_metrics_bm25 as evaluation


DATA_DIR = evaluation.bm25_module.DATA_DIR


def run_benchmark(
    docs_path: Path,
    queries_path: Path,
    qrels_path: Path,
    *,
    model: str,
    top_ks: list[int] | None = None,
    top_k: int | None = None,
) -> dict[str, object]:
    # top_ks(여러 cutoff)와 top_k(단일 cutoff, 이전 호출 방식) 중 하나만 받는다.
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
        # index 생성은 위에서 한 번만 하므로, 측정 시간은 검색 + 지표 계산 구간이다.
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
                "concept_id": query.concept_id,
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
