from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
BM25_DIR = SEARCH_IR_DIR / "bm25"
if str(BM25_DIR) not in sys.path:
    # evaluation/metrics/ 위치에서도 bm25/bm25.py를 import할 수 있게 한다.
    sys.path.insert(0, str(BM25_DIR))

import bm25 as bm25_module


MODEL_CHOICES = (*bm25_module.MODEL_CHOICES, "all")


@dataclass
class Metrics:
    precision: float
    recall: float
    mrr: float
    ndcg: float


def evaluate_ranking(
    ranked_docs: list[tuple[str, float]],
    qrel: dict[str, int],
    *,
    k: int,
) -> Metrics:
    # qrels에는 평가 기준이 되는 정답 문서와 관련도(relevance)가 들어 있다.
    relevant_docs = {doc_id: rel for doc_id, rel in qrel.items() if rel > 0}
    hits = 0
    reciprocal_rank = 0.0
    dcg = 0.0

    for rank, (doc_id, _) in enumerate(ranked_docs[:k], start=1):
        relevance = relevant_docs.get(doc_id, 0)
        if relevance > 0:
            hits += 1
            if reciprocal_rank == 0.0:
                # MRR은 첫 번째 정답 문서가 나온 순위의 역수만 사용한다.
                reciprocal_rank = 1.0 / rank
        # DCG는 관련도가 높은 문서가 앞 순위에 나올수록 더 큰 값을 준다.
        dcg += (2**relevance - 1) / math.log2(rank + 1)

    # IDCG는 가능한 가장 좋은 순서로 정렬했을 때의 DCG다.
    ideal_relevances = sorted(relevant_docs.values(), reverse=True)[:k]
    idcg = sum(
        (2**relevance - 1) / math.log2(rank + 1)
        for rank, relevance in enumerate(ideal_relevances, start=1)
    )

    return Metrics(
        # P@k: top-k 중 정답 문서 비율, R@k: 전체 정답 문서 중 찾은 비율.
        precision=hits / k if k else 0.0,
        recall=hits / len(relevant_docs) if relevant_docs else 0.0,
        mrr=reciprocal_rank,
        ndcg=dcg / idcg if idcg else 0.0,
    )


def mean_metrics(metrics: list[Metrics]) -> Metrics:
    if not metrics:
        return Metrics(0.0, 0.0, 0.0, 0.0)

    count = len(metrics)
    return Metrics(
        precision=sum(item.precision for item in metrics) / count,
        recall=sum(item.recall for item in metrics) / count,
        mrr=sum(item.mrr for item in metrics) / count,
        ndcg=sum(item.ndcg for item in metrics) / count,
    )


def build_search_functions(
    flat_index: bm25_module.FlatIndex,
    field_index: bm25_module.FieldIndex,
) -> dict[str, tuple[str, Callable[[list[str]], dict[str, float]]]]:
    # BM25F는 title/tags/text 필드를 따로 쓰므로 field_index가 필요하다.
    return {
        "bm25": ("bm25", lambda tokens: bm25_module.bm25(tokens, flat_index)),
        "bm25+": ("bm25+", lambda tokens: bm25_module.bm25_plus(tokens, flat_index)),
        "bm25l": ("bm25L", lambda tokens: bm25_module.bm25l(tokens, flat_index)),
        "bm25f": ("bm25F", lambda tokens: bm25_module.bm25f(tokens, field_index)),
    }


def evaluate_model(
    search_fn: Callable[[list[str]], dict[str, float]],
    queries: list[bm25_module.Query],
    qrels: dict[str, dict[str, int]],
    *,
    k: int,
) -> Metrics:
    per_query_metrics: list[Metrics] = []

    for query in queries:
        # 각 query를 검색한 뒤 qrels 기준으로 query별 metric을 계산한다.
        query_tokens = bm25_module.tokenize(query.text)
        scores = search_fn(query_tokens)
        ranked_docs = bm25_module.rank_documents(scores, k)
        per_query_metrics.append(
            evaluate_ranking(ranked_docs, qrels.get(query.query_id, {}), k=k)
        ) 

    return mean_metrics(per_query_metrics)


def print_summary(summary: dict[str, Metrics], *, k: int, n_queries: int) -> None:
    print(f"Evaluated {n_queries} queries @ {k}")
    print(f"{'model':<8} {'P@k':>8} {'R@k':>8} {'MRR@k':>8} {'nDCG@k':>8}")
    print("-" * 44)
    for model_name, metrics in summary.items():
        print(
            f"{model_name:<8} "
            f"{metrics.precision:>8.4f} "
            f"{metrics.recall:>8.4f} "
            f"{metrics.mrr:>8.4f} "
            f"{metrics.ndcg:>8.4f}"
        )


def parse_args() -> argparse.Namespace:
    data_dir = BM25_DIR / "data" / "generated"

    parser = argparse.ArgumentParser(
        description="Evaluate generated BM25 search results with P@k, R@k, MRR@k, and nDCG@k."
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=bm25_module.resolve_generated_path(data_dir, "corpus.jsonl"),
        help="Path to generated corpus JSONL.",
    )
    parser.add_argument(
        "--queries",
        type=Path,
        default=bm25_module.resolve_generated_path(data_dir, "queries.json"),
        help="Path to generated queries JSON.",
    )
    parser.add_argument(
        "--qrels",
        type=Path,
        default=bm25_module.resolve_generated_path(data_dir, "qrels.json"),
        help="Path to generated qrels JSON.",
    )
    parser.add_argument(
        "--model",
        type=str.lower,
        choices=MODEL_CHOICES,
        default="all",
        help="Model to evaluate. Default: all.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Evaluate the top-k ranked documents. Default: 10.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    documents = bm25_module.load_documents(args.docs)
    queries = bm25_module.load_queries(args.queries)
    qrels = bm25_module.load_qrels(args.qrels)
    flat_index, field_index = bm25_module.build_indexes(documents)
    search_functions = build_search_functions(flat_index, field_index)

    # --model all이면 모든 모델을, 아니면 선택한 모델 하나만 평가한다.
    selected_models = (
        search_functions.keys() if args.model == "all" else (args.model,)
    )
    summary: dict[str, Metrics] = {}
    for model_key in selected_models:
        model_name, search_fn = search_functions[model_key]
        summary[model_name] = evaluate_model(search_fn, queries, qrels, k=args.top_k)

    print_summary(summary, k=args.top_k, n_queries=len(queries))


if __name__ == "__main__":
    main()
