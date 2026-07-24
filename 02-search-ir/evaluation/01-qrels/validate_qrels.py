from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SEARCH_IR_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = SEARCH_IR_DIR / "bm25" / "data" / "generated"


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
        if isinstance(relevance, bool) or not isinstance(relevance, int) or relevance < 0:
            errors.append(
                f"qrels item {index}: relevance must be a non-negative integer"
            )

        pair = (query_id, doc_id)
        if pair in seen_pairs:
            errors.append(f"qrels item {index}: duplicate pair {pair!r}")
        seen_pairs.add(pair)

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
