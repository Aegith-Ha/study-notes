"""benchmark JSON의 query별 지표를 query 속성(intent, topic, query 길이)으로 묶어 평균낸다.

전체 평균에 가려진 약한 query 그룹을 찾는 용도다. 차이가 우연인지는 06-significance에서 확인한다.

실행: python 02-search-ir/05-evaluation/05-slice-analysis/analyze_query_slices.py .../generated/bm25.json --model bm25 --slice-by intent
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METRIC_KEYS = ("precision", "recall", "mrr", "ndcg")
SLICE_CHOICES = ("intent", "topic", "query_length")


def resolve_model_name(
    per_query: dict[str, Any],
    requested: str | None,
) -> str:
    if not per_query:
        raise ValueError("benchmark result does not contain per-query metrics")
    if requested is None:
        return next(iter(per_query))
    if requested in per_query:
        return requested

    # JSON의 모델 이름은 "bm25F"처럼 대소문자가 섞여 있으므로 대소문자를 무시하고도 찾는다.
    matches = [
        model_name
        for model_name in per_query
        if model_name.casefold() == requested.casefold()
    ]
    if len(matches) == 1:
        return matches[0]
    raise ValueError(f"unknown model: {requested}")


def query_length_bucket(token_count: int) -> str:
    # 00-data에서는 paraphrase query가 대부분 5토큰 이상이라 intent와 길이가 함께 움직인다(confounding).
    if token_count <= 2:
        return "short (1-2)"
    if token_count <= 4:
        return "medium (3-4)"
    return "long (5+)"


def get_slice_value(query_result: dict[str, Any], slice_by: str) -> str:
    if slice_by == "query_length":
        return query_length_bucket(int(query_result.get("token_count", 0)))
    value = query_result.get(slice_by, "")
    return str(value) if value else "unknown"


def analyze_slices(
    result: dict[str, Any],
    *,
    model: str | None,
    cutoff: int | None,
    slice_by: str,
) -> dict[str, Any]:
    per_query = result.get("per_query", {})
    if not isinstance(per_query, dict):
        raise ValueError("benchmark per_query field must be an object")

    model_name = resolve_model_name(per_query, model)
    selected_cutoff = cutoff if cutoff is not None else int(result.get("top_k", 0))
    available_cutoffs = {
        int(value) for value in result.get("top_ks", [result.get("top_k", 0)])
    }
    if selected_cutoff not in available_cutoffs:
        raise ValueError(
            f"k={selected_cutoff} is unavailable; "
            f"choose one of {sorted(available_cutoffs)}"
        )

    grouped: dict[str, list[dict[str, float]]] = {}
    for query_result in per_query[model_name].values():
        metrics_by_k = query_result.get("metrics_by_k", {})
        metrics = metrics_by_k.get(str(selected_cutoff))
        if not isinstance(metrics, dict):
            raise ValueError(
                f"per-query result does not contain metrics for k={selected_cutoff}"
            )
        slice_value = get_slice_value(query_result, slice_by)
        grouped.setdefault(slice_value, []).append(
            {key: float(metrics.get(key, 0.0)) for key in METRIC_KEYS}
        )

    groups: dict[str, dict[str, Any]] = {}
    for slice_value, query_metrics in sorted(grouped.items()):
        query_count = len(query_metrics)
        # 그룹 안 query 지표의 단순 평균(macro average)이다. query 수가 적은 그룹은 변동이 크다.
        groups[slice_value] = {
            "query_count": query_count,
            "metrics": {
                key: sum(metrics[key] for metrics in query_metrics) / query_count
                for key in METRIC_KEYS
            },
        }

    return {
        "model": model_name,
        "top_k": selected_cutoff,
        "slice_by": slice_by,
        "query_count": sum(group["query_count"] for group in groups.values()),
        "groups": groups,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate benchmark per-query metrics by query slice."
    )
    parser.add_argument("result", type=Path, help="Benchmark result JSON path.")
    parser.add_argument("--model", help="Model name. Default: first model.")
    parser.add_argument("--top-k", type=int, help="Cutoff to analyze. Default: largest.")
    parser.add_argument(
        "--slice-by",
        choices=SLICE_CHOICES,
        default="intent",
        help="Query attribute used to create groups. Default: intent.",
    )
    parser.add_argument("--output", type=Path, help="Write JSON to this path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.result.open(encoding="utf-8") as handle:
        benchmark_result = json.load(handle)

    try:
        result = analyze_slices(
            benchmark_result,
            model=args.model,
            cutoff=args.top_k,
            slice_by=args.slice_by,
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"{output}\n", encoding="utf-8")
        print(f"Wrote slice analysis to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
