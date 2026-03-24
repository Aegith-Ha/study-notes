from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from heapq import nlargest
from pathlib import Path
from typing import DefaultDict


TOKEN_PATTERN = re.compile(r"[0-9a-zA-Z가-힣]+(?:-[0-9a-zA-Z가-힣]+)?")
FIELDS = ("title", "tags", "text")


@dataclass
class Document:
    doc_id: str
    topic: str
    title: str
    tags: list[str]
    text: str


@dataclass
class Query:
    query_id: str
    topic: str
    text: str
    intent: str


@dataclass
class FlatIndex:
    documents: dict[str, Document]
    postings: dict[str, dict[str, int]]
    doc_lengths: dict[str, int]
    avg_doc_length: float
    doc_freqs: dict[str, int]
    n_docs: int


@dataclass
class FieldIndex:
    documents: dict[str, Document]
    field_postings: dict[str, dict[str, dict[str, int]]]
    field_lengths: dict[str, dict[str, int]]
    avg_field_lengths: dict[str, float]
    doc_freqs: dict[str, int]
    n_docs: int


@dataclass
class Metrics:
    precision: float
    recall: float
    mrr: float
    ndcg: float


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def load_documents(path: Path) -> dict[str, Document]:
    documents: dict[str, Document] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = json.loads(line)
            documents[raw["id"]] = Document(
                doc_id=raw["id"],
                topic=raw.get("topic", ""),
                title=raw.get("title", ""),
                tags=raw.get("tags", []),
                text=raw.get("text", ""),
            )
    return documents


def load_queries(path: Path) -> list[Query]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    return [
        Query(
            query_id=item["query_id"],
            topic=item.get("topic", ""),
            text=item["query"],
            intent=item.get("intent", ""),
        )
        for item in payload["queries"]
    ]


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    qrels: DefaultDict[str, dict[str, int]] = defaultdict(dict)
    for item in payload["qrels"]:
        qrels[item["query_id"]][item["doc_id"]] = item["relevance"]
    return dict(qrels)


def build_indexes(documents: dict[str, Document]) -> tuple[FlatIndex, FieldIndex]:
    postings: DefaultDict[str, dict[str, int]] = defaultdict(dict)
    doc_lengths: dict[str, int] = {}
    doc_freqs: DefaultDict[str, int] = defaultdict(int)

    field_postings: dict[str, DefaultDict[str, dict[str, int]]] = {
        field: defaultdict(dict) for field in FIELDS
    }
    field_lengths: dict[str, dict[str, int]] = {field: {} for field in FIELDS}
    total_field_lengths = {field: 0 for field in FIELDS}

    for doc_id, document in documents.items():
        flattened_terms: Counter[str] = Counter()
        seen_terms: set[str] = set()

        field_texts = {
            "title": document.title,
            "tags": " ".join(document.tags),
            "text": document.text,
        }

        for field, text in field_texts.items():
            tokens = tokenize(text)
            counts = Counter(tokens)
            field_lengths[field][doc_id] = len(tokens)
            total_field_lengths[field] += len(tokens)

            for term, tf in counts.items():
                field_postings[field][term][doc_id] = tf

            flattened_terms.update(counts)
            seen_terms.update(counts.keys())

        doc_lengths[doc_id] = sum(flattened_terms.values())
        for term, tf in flattened_terms.items():
            postings[term][doc_id] = tf
        for term in seen_terms:
            doc_freqs[term] += 1

    n_docs = len(documents)
    avg_doc_length = sum(doc_lengths.values()) / n_docs if n_docs else 0.0
    avg_field_lengths = {
        field: (total_field_lengths[field] / n_docs if n_docs else 0.0)
        for field in FIELDS
    }

    flat_index = FlatIndex(
        documents=documents,
        postings=dict(postings),
        doc_lengths=doc_lengths,
        avg_doc_length=avg_doc_length,
        doc_freqs=dict(doc_freqs),
        n_docs=n_docs,
    )
    field_index = FieldIndex(
        documents=documents,
        field_postings={field: dict(index) for field, index in field_postings.items()},
        field_lengths=field_lengths,
        avg_field_lengths=avg_field_lengths,
        doc_freqs=dict(doc_freqs),
        n_docs=n_docs,
    )
    return flat_index, field_index


def idf(term: str, doc_freqs: dict[str, int], n_docs: int) -> float:
    df = doc_freqs.get(term, 0)
    return math.log1p((n_docs - df + 0.5) / (df + 0.5))


def bm25(
    query_tokens: list[str],
    index: FlatIndex,
    *,
    k1: float = 1.2,
    b: float = 0.75,
) -> dict[str, float]:
    query_tf = Counter(query_tokens)
    scores: DefaultDict[str, float] = defaultdict(float)

    for term, qtf in query_tf.items():
        postings = index.postings.get(term)
        if not postings:
            continue

        term_idf = idf(term, index.doc_freqs, index.n_docs)
        for doc_id, tf in postings.items():
            doc_len = index.doc_lengths[doc_id]
            norm = k1 * (1.0 - b + b * doc_len / index.avg_doc_length)
            score = term_idf * ((tf * (k1 + 1.0)) / (tf + norm))
            scores[doc_id] += qtf * score

    return dict(scores)


def bm25_plus(
    query_tokens: list[str],
    index: FlatIndex,
    *,
    k1: float = 1.2,
    b: float = 0.75,
    delta: float = 1.0,
) -> dict[str, float]:
    query_tf = Counter(query_tokens)
    scores: DefaultDict[str, float] = defaultdict(float)

    for term, qtf in query_tf.items():
        postings = index.postings.get(term)
        if not postings:
            continue

        term_idf = idf(term, index.doc_freqs, index.n_docs)
        for doc_id, tf in postings.items():
            doc_len = index.doc_lengths[doc_id]
            norm = k1 * (1.0 - b + b * doc_len / index.avg_doc_length)
            tf_component = (tf * (k1 + 1.0)) / (tf + norm)
            scores[doc_id] += qtf * term_idf * (tf_component + delta)

    return dict(scores)


def bm25l(
    query_tokens: list[str],
    index: FlatIndex,
    *,
    k1: float = 1.2,
    b: float = 0.75,
    delta: float = 0.5,
) -> dict[str, float]:
    query_tf = Counter(query_tokens)
    scores: DefaultDict[str, float] = defaultdict(float)

    for term, qtf in query_tf.items():
        postings = index.postings.get(term)
        if not postings:
            continue

        term_idf = idf(term, index.doc_freqs, index.n_docs)
        for doc_id, tf in postings.items():
            doc_len = index.doc_lengths[doc_id]
            length_norm = 1.0 - b + b * doc_len / index.avg_doc_length
            normalized_tf = tf / length_norm
            tf_component = ((k1 + 1.0) * (normalized_tf + delta)) / (
                k1 + normalized_tf + delta
            )
            scores[doc_id] += qtf * term_idf * tf_component

    return dict(scores)


def bm25f(
    query_tokens: list[str],
    index: FieldIndex,
    *,
    k1: float = 1.2,
    field_weights: dict[str, float] | None = None,
    field_b: dict[str, float] | None = None,
) -> dict[str, float]:
    query_tf = Counter(query_tokens)
    scores: DefaultDict[str, float] = defaultdict(float)
    weights = field_weights or {"title": 2.2, "tags": 1.6, "text": 1.0}
    b_values = field_b or {"title": 0.3, "tags": 0.2, "text": 0.75}

    for term, qtf in query_tf.items():
        if index.doc_freqs.get(term, 0) == 0:
            continue

        term_idf = idf(term, index.doc_freqs, index.n_docs)
        candidate_docs: set[str] = set()
        for field in FIELDS:
            candidate_docs.update(index.field_postings[field].get(term, {}).keys())

        for doc_id in candidate_docs:
            weighted_tf = 0.0
            for field in FIELDS:
                tf = index.field_postings[field].get(term, {}).get(doc_id, 0)
                if tf == 0:
                    continue
                field_len = index.field_lengths[field][doc_id]
                avg_len = index.avg_field_lengths[field] or 1.0
                norm = 1.0 - b_values[field] + b_values[field] * field_len / avg_len
                weighted_tf += weights[field] * (tf / norm)

            tf_component = (weighted_tf * (k1 + 1.0)) / (k1 + weighted_tf)
            scores[doc_id] += qtf * term_idf * tf_component

    return dict(scores)


def rank_documents(scores: dict[str, float], top_k: int) -> list[tuple[str, float]]:
    return nlargest(top_k, scores.items(), key=lambda item: item[1])


def evaluate_ranking(
    ranked_docs: list[tuple[str, float]],
    qrel: dict[str, int],
    *,
    k: int,
) -> Metrics:
    relevant_docs = {doc_id: rel for doc_id, rel in qrel.items() if rel > 0}
    hits = 0
    dcg = 0.0
    reciprocal_rank = 0.0

    for rank, (doc_id, _) in enumerate(ranked_docs[:k], start=1):
        rel = relevant_docs.get(doc_id, 0)
        if rel > 0:
            hits += 1
            if reciprocal_rank == 0.0:
                reciprocal_rank = 1.0 / rank
        dcg += (2**rel - 1) / math.log2(rank + 1)

    ideal_rels = sorted(relevant_docs.values(), reverse=True)[:k]
    idcg = sum((2**rel - 1) / math.log2(rank + 1) for rank, rel in enumerate(ideal_rels, start=1))
    recall_denom = len(relevant_docs)

    return Metrics(
        precision=hits / k if k else 0.0,
        recall=hits / recall_denom if recall_denom else 0.0,
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


def print_summary(
    summary: dict[str, Metrics],
    *,
    top_k: int,
) -> None:
    print(f"\n=== Overall metrics @ {top_k} ===")
    print(f"{'model':<8} {'P@k':>8} {'R@k':>8} {'MRR@k':>8} {'nDCG@k':>8}")
    print("-" * 44)
    for model_name, metrics in sorted(summary.items(), key=lambda item: item[1].ndcg, reverse=True):
        print(
            f"{model_name:<8} "
            f"{metrics.precision:>8.4f} "
            f"{metrics.recall:>8.4f} "
            f"{metrics.mrr:>8.4f} "
            f"{metrics.ndcg:>8.4f}"
        )


def print_preview(
    model_name: str,
    query: Query,
    ranked_docs: list[tuple[str, float]],
    qrel: dict[str, int],
    documents: dict[str, Document],
    *,
    depth: int,
) -> None:
    print(
        f"\n[{model_name}] {query.query_id} | topic={query.topic} | intent={query.intent}\n"
        f"query: {query.text}"
    )
    for rank, (doc_id, score) in enumerate(ranked_docs[:depth], start=1):
        document = documents[doc_id]
        relevance = qrel.get(doc_id, 0)
        print(
            f"{rank:>2}. {doc_id:<10} score={score:>8.4f} "
            f"rel={relevance} title={document.title}"
        )


def parse_args() -> argparse.Namespace:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data" / "generated"

    parser = argparse.ArgumentParser(
        description="Compare BM25, BM25+, BM25L, and BM25F using generated data and qrels."
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=data_dir / "bm25f_corpus.jsonl",
        help="Path to the corpus JSONL file.",
    )
    parser.add_argument(
        "--queries",
        type=Path,
        default=data_dir / "bm25f_queries.json",
        help="Path to the queries JSON file.",
    )
    parser.add_argument(
        "--qrels",
        type=Path,
        default=data_dir / "bm25f_qrels.json",
        help="Path to the qrels JSON file.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Use top-k results when ranking and evaluating.",
    )
    parser.add_argument(
        "--preview-queries",
        type=int,
        default=3,
        help="Print detailed ranking results for the first N queries.",
    )
    parser.add_argument(
        "--preview-depth",
        type=int,
        default=5,
        help="How many documents to print per preview query.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    documents = load_documents(args.docs)
    queries = load_queries(args.queries)
    qrels = load_qrels(args.qrels)
    flat_index, field_index = build_indexes(documents)

    search_functions = {
        "bm25": lambda tokens: bm25(tokens, flat_index),
        "bm25+": lambda tokens: bm25_plus(tokens, flat_index),
        "bm25L": lambda tokens: bm25l(tokens, flat_index),
        "bm25F": lambda tokens: bm25f(tokens, field_index),
    }

    print(
        f"Loaded {len(documents)} docs, {len(queries)} queries, "
        f"{sum(len(items) for items in qrels.values())} qrels"
    )

    summary: dict[str, Metrics] = {}
    previews: dict[str, list[tuple[Query, list[tuple[str, float]]]]] = defaultdict(list)

    for model_name, search_fn in search_functions.items():
        per_query_metrics: list[Metrics] = []

        for index, query in enumerate(queries):
            query_tokens = tokenize(query.text)
            scores = search_fn(query_tokens)
            ranked_docs = rank_documents(scores, args.top_k)
            per_query_metrics.append(
                evaluate_ranking(ranked_docs, qrels.get(query.query_id, {}), k=args.top_k)
            )

            if index < args.preview_queries:
                previews[model_name].append((query, ranked_docs))

        summary[model_name] = mean_metrics(per_query_metrics)

    print_summary(summary, top_k=args.top_k)

    for model_name in ("bm25", "bm25+", "bm25L", "bm25F"):
        for query, ranked_docs in previews[model_name]:
            print_preview(
                model_name,
                query,
                ranked_docs,
                qrels.get(query.query_id, {}),
                documents,
                depth=min(args.preview_depth, args.top_k),
            )


if __name__ == "__main__":
    main()
