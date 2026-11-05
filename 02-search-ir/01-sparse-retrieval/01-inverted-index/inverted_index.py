"""Positional inverted index와 AND/OR 검색 예제.

- 문서마다 term이 등장한 위치(position)까지 저장하는 역색인을 만든다.
- query term의 posting list를 교집합(AND) 또는 합집합(OR)으로 결합해 문서를 찾는다.
- 점수(ranking)는 계산하지 않는다. 순위는 02-tf-idf, 03-bm25에서 다룬다.

실행: python 02-search-ir/01-sparse-retrieval/01-inverted-index/inverted_index.py --query "검색 평가"
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Literal


# 영문/숫자/한글 연속 구간을 하나의 토큰으로 본다. "tf-idf"처럼 하이픈 하나로 이어진 단어도 허용한다.
# 형태소 분석을 하지 않으므로 "역색인을"과 "역색인"은 서로 다른 토큰이 된다.
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
        # 위치 목록의 길이 = 문서 안에서 term이 등장한 횟수(TF)
        return len(self.postings.get(term, {}).get(doc_id, []))

    def document_frequency(self, term: str) -> int:
        # posting에 있는 문서 수 = term이 등장한 문서 수(DF)
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

    # defaultdict는 없는 key를 조회만 해도 항목이 생기므로, 일반 dict로 바꿔 고정한다.
    return InvertedIndex(
        postings={
            term: {doc_id: positions for doc_id, positions in doc_postings.items()}
            for term, doc_postings in postings.items()
        },
        document_count=len(documents),
    )


def search(index: InvertedIndex, query: str, operator: Operator = "and") -> list[str]:
    # 같은 term이 query에 여러 번 나와도 posting은 한 번만 조회한다. (순서 유지 중복 제거)
    query_terms = list(dict.fromkeys(tokenize(query)))
    if not query_terms:
        return []

    # 색인에 없는 term은 빈 집합이 되므로, AND 검색에서는 결과가 비게 된다.
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
