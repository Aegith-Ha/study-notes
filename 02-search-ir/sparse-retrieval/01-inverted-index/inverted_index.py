from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Literal


TOKEN_PATTERN = re.compile(r"[0-9a-zA-Z가-힣]+(?:-[0-9a-zA-Z가-힣]+)?")
Operator = Literal["and", "or"]

SAMPLE_DOCUMENTS = {
    "doc-1": "검색 시스템은 역색인을 사용한다.",
    "doc-2": "검색 및 평가 과정은 관련 문서의 순위를 측정한다.",
    "doc-3": "BM25는 대표적인 sparse retrieval 모델이다.",
}


@dataclass
class InvertedIndex:
    # term -> doc_id -> 문서 안에서 term이 등장한 위치
    postings: dict[str, dict[str, list[int]]]
    document_count: int

    def term_frequency(self, term: str, doc_id: str) -> int:
        return len(self.postings.get(term, {}).get(doc_id, []))

    def document_frequency(self, term: str) -> int:
        return len(self.postings.get(term, {}))


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def build_inverted_index(documents: dict[str, str]) -> InvertedIndex:
    postings: DefaultDict[str, DefaultDict[str, list[int]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for doc_id, text in documents.items():
        for position, term in enumerate(tokenize(text)):
            postings[term][doc_id].append(position)

    return InvertedIndex(
        postings={
            term: {doc_id: positions for doc_id, positions in doc_postings.items()}
            for term, doc_postings in postings.items()
        },
        document_count=len(documents),
    )


def search(index: InvertedIndex, query: str, operator: Operator = "and") -> list[str]:
    query_terms = list(dict.fromkeys(tokenize(query)))
    if not query_terms:
        return []

    posting_sets = [set(index.postings.get(term, {})) for term in query_terms]
    if operator == "and":
        matched = set.intersection(*posting_sets)
    else:
        matched = set.union(*posting_sets)
    return sorted(matched)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="positional inverted index 예제")
    parser.add_argument("--query", default="검색 평가", help="검색할 query")
    parser.add_argument(
        "--operator",
        choices=("and", "or"),
        default="and",
        help="query term의 posting을 결합하는 방법",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    index = build_inverted_index(SAMPLE_DOCUMENTS)
    query_terms = tokenize(args.query)

    print(f"query: {args.query!r} ({args.operator.upper()})")
    for term in query_terms:
        print(
            f"- {term}: postings={index.postings.get(term, {})}, "
            f"df={index.document_frequency(term)}"
        )

    results = search(index, args.query, args.operator)
    print(f"matched documents: {results}")


if __name__ == "__main__":
    main()
