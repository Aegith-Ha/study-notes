from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METRIC_KEYS = ("precision", "recall", "mrr", "ndcg")


def get_cutoffs(result: dict[str, Any]) -> list[int]:
    raw_cutoffs = result.get("top_ks")
    if isinstance(raw_cutoffs, list) and raw_cutoffs:
        return sorted({int(cutoff) for cutoff in raw_cutoffs})
    return [int(result.get("top_k", 0))]


def get_metrics(model_result: dict[str, Any], cutoff: int) -> dict[str, Any]:
    metrics_by_k = model_result.get("metrics_by_k")
    if isinstance(metrics_by_k, dict):
        metrics = metrics_by_k.get(str(cutoff))
        if not isinstance(metrics, dict):
            raise ValueError(f"model result does not contain metrics for k={cutoff}")
        return metrics
    # 이전 단일-cutoff benchmark JSON도 계속 보고서로 변환할 수 있게 한다.
    return model_result


def render_report(result: dict[str, Any], baseline: str | None = None) -> str:
    models = result.get("models", {})
    if not models:
        raise ValueError("benchmark result does not contain models")

    baseline_name = baseline or next(iter(models))
    if baseline_name not in models:
        raise ValueError(f"unknown baseline: {baseline_name}")
    cutoffs = get_cutoffs(result)

    lines = [
        "# Retrieval Benchmark Report",
        "",
        f"- Queries: {result.get('query_count', 0)}",
        f"- Documents: {result.get('document_count', 0)}",
        f"- Cutoffs: {', '.join(f'@{cutoff}' for cutoff in cutoffs)}",
        f"- Baseline: `{baseline_name}`",
        "",
        "| Model | k | P@k | R@k | MRR@k | nDCG@k | nDCG delta | Seconds |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cutoff in cutoffs:
        baseline_metrics = get_metrics(models[baseline_name], cutoff)
        for model_name, model_result in models.items():
            metrics = get_metrics(model_result, cutoff)
            values = [float(metrics.get(key, 0.0)) for key in METRIC_KEYS]
            ndcg_delta = values[3] - float(baseline_metrics.get("ndcg", 0.0))
            duration = float(model_result.get("duration_seconds", 0.0))
            lines.append(
                f"| {model_name} | {cutoff} | {values[0]:.4f} | "
                f"{values[1]:.4f} | {values[2]:.4f} | {values[3]:.4f} | "
                f"{ndcg_delta:+.4f} | {duration:.4f} |"
            )

    lines.extend(
        [
            "",
            "## Inputs",
            "",
            *[
                f"- {name}: `{path}`"
                for name, path in result.get("inputs", {}).items()
            ],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a benchmark JSON result as Markdown."
    )
    parser.add_argument("result", type=Path, help="Benchmark result JSON path.")
    parser.add_argument("--baseline", help="Model name used for delta comparison.")
    parser.add_argument("--output", type=Path, help="Write Markdown to this path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.result.open(encoding="utf-8") as handle:
        result = json.load(handle)
    try:
        report = render_report(result, args.baseline)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote report to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
