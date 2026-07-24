from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
METRICS_DIR = SEARCH_IR_DIR / "evaluation" / "metrics"
if str(METRICS_DIR) not in sys.path:
    sys.path.insert(0, str(METRICS_DIR))

import evaluate_metrics_bm25 as evaluation


DATA_DIR = SEARCH_IR_DIR / "bm25" / "data" / "generated"


def analyze_errors(
    docs_path: Path,
    queries_path: Path,
    qrels_path: Path,
    *,
    model: str,
    top_k: int,
    max_cases: int,
) -> dict[str, object]:
    bm25 = evaluation.bm25_module
    documents = bm25.load_documents(docs_path)
    queries = bm25.load_queries(queries_path)
    qrels = bm25.load_qrels(qrels_path)
    flat_index, field_index = bm25.build_indexes(documents)
    model_name, search_fn = evaluation.build_search_functions(
        flat_index, field_index
    )[model]

    cases: list[dict[str, object]] = []
    for query in queries:
        ranked = bm25.rank_documents(search_fn(bm25.tokenize(query.text)), top_k)
        retrieved_ids = {doc_id for doc_id, _ in ranked}
        relevance_by_doc = qrels.get(query.query_id, {})
        relevant_ids = {
            doc_id for doc_id, relevance in relevance_by_doc.items() if relevance > 0
        }
        false_positives = [
            doc_id for doc_id, _ in ranked if relevance_by_doc.get(doc_id, 0) == 0
        ]
        false_negatives = sorted(relevant_ids - retrieved_ids)
        if not false_positives and not false_negatives:
            continue

        cases.append(
            {
                "query_id": query.query_id,
                "query": query.text,
                "false_positive_doc_ids": false_positives,
                "false_negative_doc_ids": false_negatives,
                "results": [
                    {
                        "rank": rank,
                        "doc_id": doc_id,
                        "score": score,
                        "relevance": relevance_by_doc.get(doc_id, 0),
                        "title": documents[doc_id].title,
                    }
                    for rank, (doc_id, score) in enumerate(ranked, start=1)
                ],
            }
        )
        if len(cases) >= max_cases:
            break

    return {
        "model": model_name,
        "top_k": top_k,
        "case_count": len(cases),
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze BM25 retrieval errors.")
    parser.add_argument("--docs", type=Path, default=DATA_DIR / "corpus.jsonl")
    parser.add_argument("--queries", type=Path, default=DATA_DIR / "queries.json")
    parser.add_argument("--qrels", type=Path, default=DATA_DIR / "qrels.json")
    parser.add_argument(
        "--model",
        choices=evaluation.bm25_module.MODEL_CHOICES,
        default="bm25",
    )
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--max-cases", type=int, default=10)
    parser.add_argument("--output", type=Path, help="Write the JSON result to this path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.top_k <= 0 or args.max_cases <= 0:
        raise SystemExit("--top-k and --max-cases must be greater than zero")

    result = analyze_errors(
        args.docs,
        args.queries,
        args.qrels,
        model=args.model,
        top_k=args.top_k,
        max_cases=args.max_cases,
    )
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"{output}\n", encoding="utf-8")
        print(f"Wrote error analysis to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
