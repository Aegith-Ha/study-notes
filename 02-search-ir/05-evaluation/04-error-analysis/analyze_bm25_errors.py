"""BM25 검색 결과에서 오검색(false positive)과 미검색(false negative) 사례를 뽑는다.

- false positive: top-k에 있지만 정답이 아닌 문서 (relevance 0)
- false negative: 정답이지만 top-k에 들지 못한 문서
- 결과에는 문서의 concepts를 함께 저장해, query concept과 비교하며 원인을 볼 수 있게 한다.

실행: python 02-search-ir/05-evaluation/04-error-analysis/analyze_bm25_errors.py --model bm25 --intent paraphrase
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
METRICS_DIR = SEARCH_IR_DIR / "05-evaluation" / "02-metrics"
# 폴더 이름이 숫자로 시작해 패키지 import가 안 되므로 sys.path에 직접 추가한다.
if str(METRICS_DIR) not in sys.path:
    sys.path.insert(0, str(METRICS_DIR))

import evaluate_metrics_bm25 as evaluation


DATA_DIR = evaluation.bm25_module.DATA_DIR


def analyze_errors(
    docs_path: Path,
    queries_path: Path,
    qrels_path: Path,
    *,
    model: str,
    top_k: int,
    max_cases: int,
    intent: str = "all",
) -> dict[str, object]:
    bm25 = evaluation.bm25_module
    documents = bm25.load_documents(docs_path)
    queries = bm25.load_queries(queries_path)
    if intent != "all":
        queries = [query for query in queries if query.intent == intent]
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
        # 오검색도 미검색도 없는 query는 분석할 것이 없으므로 건너뛴다.
        # 00-data는 query당 정답이 k보다 많아서, 대부분의 query에 false negative가 남는다.
        if not false_positives and not false_negatives:
            continue

        cases.append(
            {
                "query_id": query.query_id,
                "query": query.text,
                "intent": query.intent,
                "concept_id": query.concept_id,
                "false_positive_doc_ids": false_positives,
                "false_negative_doc_ids": false_negatives,
                "results": [
                    {
                        "rank": rank,
                        "doc_id": doc_id,
                        "score": score,
                        "relevance": relevance_by_doc.get(doc_id, 0),
                        "doc_type": documents[doc_id].doc_type,
                        # title은 무작위 키워드 조합이라 정답 판단에는 concepts가 더 유용하다.
                        "concepts": documents[doc_id].concepts,
                    }
                    for rank, (doc_id, score) in enumerate(ranked, start=1)
                ],
            }
        )
        # queries.json 순서대로 앞에서부터 max_cases개만 모은다. (점수가 낮은 순이 아님)
        if len(cases) >= max_cases:
            break

    return {
        "model": model_name,
        "top_k": top_k,
        "intent": intent,
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
    parser.add_argument(
        "--intent",
        choices=("all", "keyword", "paraphrase"),
        default="all",
        help="Analyze only queries of this intent. Default: all.",
    )
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
        intent=args.intent,
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
