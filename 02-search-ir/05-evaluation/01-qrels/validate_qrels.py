"""qrels가 queries, corpus와 구조적으로 맞는지 검증한다.

검사 항목: 존재하지 않는 query_id / doc_id, relevance 값, 중복 쌍, 정답이 없는 query
라벨이 의미적으로 맞는지는 검사하지 않는다.

실행: python 02-search-ir/05-evaluation/01-qrels/validate_qrels.py
오류가 있으면 목록을 출력하고 종료 코드 1을 반환한다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


# 이 파일 기준 parents[0]=01-qrels, [1]=05-evaluation, [2]=02-search-ir
SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = SEARCH_IR_DIR / "00-data" / "generated"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_qrels(
    qrels_path: Path,
    queries_path: Path,
    docs_path: Path,
) -> tuple[list[str], int, int, int]:
    qrels_payload = load_json(qrels_path)
    queries_payload = load_json(queries_path)

    query_ids = {
        item["query_id"]
        for item in queries_payload.get("queries", [])
        if isinstance(item, dict) and "query_id" in item
    }
    doc_ids: set[str] = set()
    with docs_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                # corpus 자체가 깨졌으면 이후 검증이 의미 없으므로 바로 반환한다.
                return ([f"docs line {line_number}: invalid JSON ({error})"], 0, 0, 0)
            if isinstance(item, dict) and "id" in item:
                doc_ids.add(item["id"])

    errors: list[str] = []
    judgments = qrels_payload.get("qrels", [])
    if not isinstance(judgments, list):
        return (["qrels must be a list"], len(query_ids), len(doc_ids), 0)

    seen_pairs: set[tuple[str, str]] = set()
    for index, item in enumerate(judgments, start=1):
        if not isinstance(item, dict):
            errors.append(f"qrels item {index}: must be an object")
            continue

        query_id = item.get("query_id")
        doc_id = item.get("doc_id")
        relevance = item.get("relevance")
        if query_id not in query_ids:
            errors.append(f"qrels item {index}: unknown query_id {query_id!r}")
        if doc_id not in doc_ids:
            errors.append(f"qrels item {index}: unknown doc_id {doc_id!r}")
        # bool은 int의 하위 타입이라 True가 1로 통과하므로 따로 걸러낸다.
        if isinstance(relevance, bool) or not isinstance(relevance, int) or relevance < 0:
            errors.append(
                f"qrels item {index}: relevance must be a non-negative integer"
            )

        pair = (query_id, doc_id)
        if pair in seen_pairs:
            errors.append(f"qrels item {index}: duplicate pair {pair!r}")
        seen_pairs.add(pair)

    # 정답이 하나도 없는 query는 Recall, nDCG가 항상 0이 되어 평균을 왜곡한다.
    judged_query_ids = {
        item.get("query_id") for item in judgments if isinstance(item, dict)
    }
    for query_id in sorted(query_ids - judged_query_ids):
        errors.append(f"query {query_id!r}: has no qrels judgments")

    return errors, len(query_ids), len(doc_ids), len(judgments)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate qrels references and values.")
    parser.add_argument("--qrels", type=Path, default=DATA_DIR / "qrels.json")
    parser.add_argument("--queries", type=Path, default=DATA_DIR / "queries.json")
    parser.add_argument("--docs", type=Path, default=DATA_DIR / "corpus.jsonl")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors, query_count, doc_count, judgment_count = validate_qrels(
        args.qrels, args.queries, args.docs
    )
    print(
        f"Validated {judgment_count} judgments against "
        f"{query_count} queries and {doc_count} documents."
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Qrels are valid.")


if __name__ == "__main__":
    main()
