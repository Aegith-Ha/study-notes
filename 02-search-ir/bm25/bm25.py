from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from heapq import nlargest
from pathlib import Path
from typing import DefaultDict, Callable


TOKEN_PATTERN = re.compile(r"[0-9a-zA-Z가-힣]+(?:-[0-9a-zA-Z가-힣]+)?")
# BM25F는 문서를 하나의 텍스트가 아니라 여러 필드로 나눠 점수를 계산한다.
FIELDS = ("title", "tags", "text")
MODEL_CHOICES = ("bm25", "bm25+", "bm25l", "bm25f")


@dataclass
class Document:
    doc_id: str
    topic: str
    doc_type: str
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
    # 일반 BM25 계열에서 쓰는 단일 역색인: term -> doc_id -> term frequency.
    postings: dict[str, dict[str, int]]
    doc_lengths: dict[str, int]
    avg_doc_length: float
    doc_freqs: dict[str, int]
    n_docs: int


@dataclass
class FieldIndex:
    # BM25F에서 쓰는 필드별 역색인: field -> term -> doc_id -> term frequency.
    field_postings: dict[str, dict[str, dict[str, int]]]
    field_lengths: dict[str, dict[str, int]]
    avg_field_lengths: dict[str, float]
    doc_freqs: dict[str, int]
    n_docs: int


def tokenize(text: str) -> list[str]:
    # 예제용 단순 토크나이저다. 영어/숫자/한국어와 하이픈 단어를 추출한다.
    return TOKEN_PATTERN.findall(text.lower())


def load_documents(path: Path) -> dict[str, Document]:
    documents: dict[str, Document] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = json.loads(line)
            documents[raw["id"]] = Document(
                doc_id=raw["id"],
                topic=raw.get("topic", ""),
                doc_type=raw.get("doc_type", ""),
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
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    qrels: DefaultDict[str, dict[str, int]] = defaultdict(dict)
    for item in payload["qrels"]:
        # query_id별로 평가 정답 문서와 relevance를 빠르게 찾기 위한 구조로 바꾼다.
        qrels[item["query_id"]][item["doc_id"]] = item["relevance"]
    return dict(qrels)


def build_indexes(documents: dict[str, Document]) -> tuple[FlatIndex, FieldIndex]:
    # 한 번의 순회에서 일반 BM25용 flat index와 BM25F용 field index를 함께 만든다.
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
            counts = Counter(tokenize(text))
            field_lengths[field][doc_id] = sum(counts.values())
            total_field_lengths[field] += sum(counts.values())

            for term, tf in counts.items():
                field_postings[field][term][doc_id] = tf

            # flat index는 title/tags/text를 하나의 문서 본문처럼 합쳐서 본다.
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
        field: total_field_lengths[field] / n_docs if n_docs else 0.0
        for field in FIELDS
    }

    return (
        FlatIndex(
            postings=dict(postings),
            doc_lengths=doc_lengths,
            avg_doc_length=avg_doc_length,
            doc_freqs=dict(doc_freqs),
            n_docs=n_docs,
        ),
        FieldIndex(
            field_postings={field: dict(index) for field, index in field_postings.items()},
            field_lengths=field_lengths,
            avg_field_lengths=avg_field_lengths,
            doc_freqs=dict(doc_freqs),
            n_docs=n_docs,
        ),
    )


def idf(term: str, doc_freqs: dict[str, int], n_docs: int) -> float:
    df = doc_freqs.get(term, 0)
    # 문서 전체에 흔한 단어는 낮게, 드문 단어는 높게 평가한다.
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
            # b는 문서 길이 정규화 강도, k1은 term frequency 포화 속도를 조절한다.
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
            # BM25+는 delta를 더해 긴 문서가 과하게 불리해지는 현상을 완화한다.
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
            # BM25L은 정규화된 tf에 delta를 더해 길이 보정을 조금 부드럽게 만든다.
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
    # 더미 qrels는 title/tags의 키워드 겹침을 강하게 보므로 본문 가중치는 낮춘다.
    weights = field_weights or {"title": 2.0, "tags": 2.0, "text": 0.5}
    b_values = field_b or {"title": 0.5, "tags": 0.0, "text": 0.75}

    for term, qtf in query_tf.items():
        if index.doc_freqs.get(term, 0) == 0:
            continue

        term_idf = idf(term, index.doc_freqs, index.n_docs)
        candidate_docs: set[str] = set()
        for field in FIELDS:
            candidate_docs.update(index.field_postings[field].get(term, {}).keys())

        # set 순회 순서는 실행마다 달라질 수 있으므로 동점 순위가 흔들리지 않게 정렬한다.
        for doc_id in sorted(candidate_docs):
            weighted_tf = 0.0
            for field in FIELDS:
                tf = index.field_postings[field].get(term, {}).get(doc_id, 0)
                if tf == 0:
                    continue

                field_len = index.field_lengths[field][doc_id]
                avg_len = index.avg_field_lengths[field] or 1.0
                # 필드마다 길이 분포가 다르므로 title/tags/text를 따로 정규화한다.
                norm = 1.0 - b_values[field] + b_values[field] * field_len / avg_len
                weighted_tf += weights[field] * (tf / norm)

            tf_component = (weighted_tf * (k1 + 1.0)) / (k1 + weighted_tf)
            scores[doc_id] += qtf * term_idf * tf_component

    return dict(scores)


def rank_documents(scores: dict[str, float], top_k: int) -> list[tuple[str, float]]:
    # 점수가 높은 문서 top-k만 뽑는다.
    return nlargest(top_k, scores.items(), key=lambda item: item[1])


def select_query(args: argparse.Namespace, queries: list[Query]) -> tuple[str, str | None]:
    # 우선순위: 직접 입력한 --query, generated의 --query-id, generated 첫 번째 query.
    if args.query:
        return args.query, None

    if args.query_id:
        queries_by_id = {query.query_id: query for query in queries}
        if args.query_id not in queries_by_id:
            raise SystemExit(f"Unknown query id: {args.query_id}")
        query = queries_by_id[args.query_id]
        return query.text, query.query_id

    if queries:
        query = queries[0]
        return query.text, query.query_id

    raise SystemExit("No query was provided and no generated query exists.")


def print_results(
    model_name: str,
    ranked_docs: list[tuple[str, float]],
    documents: dict[str, Document],
    relevance_by_doc: dict[str, int],
) -> None:
    print(f"\n[{model_name}]")
    if not ranked_docs:
        print("No results")
        return

    for rank, (doc_id, score) in enumerate(ranked_docs, start=1):
        document = documents[doc_id]
        relevance = relevance_by_doc.get(doc_id, 0)
        tags = ", ".join(document.tags)
        print(
            f"{rank:>2}. {doc_id:<10} score={score:>8.4f} rel={relevance} "
            f"topic={document.topic:<10} type={document.doc_type:<16} "
            f"title={document.title} tags=[{tags}]"
        )


def parse_args() -> argparse.Namespace:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data" / "generated"

    parser = argparse.ArgumentParser(
        description="Search generated corpus with a selected BM25 model."
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=data_dir / "corpus.jsonl",
        help="Path to generated corpus JSONL.",
    )
    parser.add_argument(
        "--queries",
        type=Path,
        default=data_dir / "queries.json",
        help="Path to generated queries JSON.",
    )
    parser.add_argument(
        "--qrels",
        type=Path,
        default=data_dir / "qrels.json",
        help="Path to generated qrels JSON.",
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Search text. If omitted, --query-id or the first generated query is used.",
    )
    parser.add_argument(
        "--query-id",
        type=str,
        help="Generated query id such as q_1.",
    )
    parser.add_argument(
        "--model",
        type=str.lower,
        choices=MODEL_CHOICES,
        default="bm25",
        help="Search model to use. Default: bm25.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to print.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    documents = load_documents(args.docs)
    queries = load_queries(args.queries) if args.queries.exists() else []
    qrels = load_qrels(args.qrels)
    query_text, query_id = select_query(args, queries)
    query_tokens = tokenize(query_text)
    flat_index, field_index = build_indexes(documents)

    search_functions: dict[str, tuple[str, Callable[[list[str]], dict[str, float]]]] = {
        "bm25": ("bm25", lambda tokens: bm25(tokens, flat_index)),
        "bm25+": ("bm25+", lambda tokens: bm25_plus(tokens, flat_index)),
        "bm25l": ("bm25L", lambda tokens: bm25l(tokens, flat_index)),
        "bm25f": ("bm25F", lambda tokens: bm25f(tokens, field_index)),
    }
    # --model로 선택한 검색 함수 하나만 실행한다. 기본값은 bm25다.
    model_name, search_fn = search_functions[args.model]

    print(f"Loaded {len(documents)} docs")
    print(f"Model: {model_name}")
    print(f"Query: {query_text}")
    if query_id:
        print(f"Query id: {query_id}")
    print(f"Tokens: {query_tokens}")

    relevance_by_doc = qrels.get(query_id, {}) if query_id else {}
    scores = search_fn(query_tokens)
    ranked_docs = rank_documents(scores, args.top_k)
    print_results(model_name, ranked_docs, documents, relevance_by_doc)


if __name__ == "__main__":
    main()
