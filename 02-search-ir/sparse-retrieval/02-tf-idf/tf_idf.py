from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from dataclasses import dataclass
from heapq import nlargest


TOKEN_PATTERN = re.compile(r"[0-9a-zA-Z가-힣]+(?:-[0-9a-zA-Z가-힣]+)?")

SAMPLE_DOCUMENTS = {
    "doc-1": "검색 시스템은 역색인을 사용해 문서를 빠르게 찾는다.",
    "doc-2": "검색 및 평가 과정은 precision recall 같은 지표로 순위를 측정한다.",
    "doc-3": "BM25는 단어 빈도와 문서 길이를 반영하는 검색 모델이다.",
    "doc-4": "RAG는 검색한 문서를 언어 모델의 context로 사용한다.",
}


@dataclass
class TfIdfIndex:
    document_vectors: dict[str, dict[str, float]]
    inverse_document_frequencies: dict[str, float]
    document_count: int


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def calculate_idf(document_frequencies: Counter[str], document_count: int) -> dict[str, float]:
    return {
        term: math.log((document_count + 1) / (df + 1)) + 1.0
        for term, df in document_frequencies.items()
    }


def normalize(vector: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(weight * weight for weight in vector.values()))
    if norm == 0.0:
        return {}
    return {term: weight / norm for term, weight in vector.items()}


def vectorize(tokens: list[str], idf_values: dict[str, float]) -> dict[str, float]:
    term_counts = Counter(tokens)
    weights = {
        term: (1.0 + math.log(count)) * idf_values[term]
        for term, count in term_counts.items()
        if term in idf_values
    }
    return normalize(weights)


def build_tfidf_index(documents: dict[str, str]) -> TfIdfIndex:
    tokenized_documents = {
        doc_id: tokenize(text) for doc_id, text in documents.items()
    }
    document_frequencies: Counter[str] = Counter()
    for tokens in tokenized_documents.values():
        document_frequencies.update(set(tokens))

    document_count = len(documents)
    idf_values = calculate_idf(document_frequencies, document_count)
    document_vectors = {
        doc_id: vectorize(tokens, idf_values)
        for doc_id, tokens in tokenized_documents.items()
    }
    return TfIdfIndex(document_vectors, idf_values, document_count)


def cosine_similarity(
    left: dict[str, float],
    right: dict[str, float],
) -> float:
    # 두 vector가 이미 L2 정규화되어 있으므로 내적이 cosine similarity다.
    if len(left) > len(right):
        left, right = right, left
    return sum(weight * right.get(term, 0.0) for term, weight in left.items())


def search(
    index: TfIdfIndex,
    query: str,
    *,
    top_k: int = 3,
) -> list[tuple[str, float]]:
    query_vector = vectorize(tokenize(query), index.inverse_document_frequencies)
    scores = (
        (doc_id, cosine_similarity(query_vector, document_vector))
        for doc_id, document_vector in index.document_vectors.items()
    )
    return [
        (doc_id, score)
        for doc_id, score in nlargest(top_k, scores, key=lambda item: item[1])
        if score > 0.0
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TF-IDF와 cosine similarity 검색 예제")
    parser.add_argument("--query", default="검색 평가", help="검색할 query")
    parser.add_argument("--top-k", type=int, default=3, help="반환할 최대 문서 수")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.top_k < 1:
        raise SystemExit("--top-k는 1 이상이어야 한다.")

    index = build_tfidf_index(SAMPLE_DOCUMENTS)
    print(f"query: {args.query!r}")
    for rank, (doc_id, score) in enumerate(
        search(index, args.query, top_k=args.top_k),
        start=1,
    ):
        print(f"{rank}. {doc_id} score={score:.4f}: {SAMPLE_DOCUMENTS[doc_id]}")


if __name__ == "__main__":
    main()
