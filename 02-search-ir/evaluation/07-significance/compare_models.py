from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


METRIC_CHOICES = ("precision", "recall", "mrr", "ndcg")


def resolve_model_name(per_query: dict[str, Any], requested: str) -> str:
    if requested in per_query:
        return requested
    matches = [
        model_name
        for model_name in per_query
        if model_name.casefold() == requested.casefold()
    ]
    if len(matches) == 1:
        return matches[0]
    raise ValueError(f"unknown model: {requested}")


def get_query_metric_values(
    per_query: dict[str, Any],
    *,
    model_name: str,
    cutoff: int,
    metric: str,
) -> dict[str, float]:
    values: dict[str, float] = {}
    for query_id, query_result in per_query[model_name].items():
        metrics_by_k = query_result.get("metrics_by_k", {})
        metrics = metrics_by_k.get(str(cutoff))
        if not isinstance(metrics, dict):
            raise ValueError(
                f"{model_name} does not contain per-query metrics for k={cutoff}"
            )
        values[query_id] = float(metrics.get(metric, 0.0))
    return values


def percentile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("cannot calculate a percentile from empty values")
    position = (len(sorted_values) - 1) * probability
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    fraction = position - lower_index
    return (
        sorted_values[lower_index] * (1.0 - fraction)
        + sorted_values[upper_index] * fraction
    )


def paired_bootstrap(
    baseline_values: list[float],
    contender_values: list[float],
    *,
    samples: int,
    seed: int,
) -> tuple[float, float, float]:
    if len(baseline_values) != len(contender_values) or not baseline_values:
        raise ValueError("paired bootstrap requires equal non-empty samples")
    if samples <= 0:
        raise ValueError("samples must be greater than zero")

    differences = [
        contender - baseline
        for baseline, contender in zip(baseline_values, contender_values)
    ]
    observed_delta = sum(differences) / len(differences)
    rng = random.Random(seed)
    bootstrap_deltas = sorted(
        sum(rng.choice(differences) for _ in differences) / len(differences)
        for _ in range(samples)
    )
    lower = percentile(bootstrap_deltas, 0.025)
    upper = percentile(bootstrap_deltas, 0.975)
    return observed_delta, lower, upper


def compare_models(
    result: dict[str, Any],
    *,
    baseline: str,
    contender: str,
    cutoff: int | None,
    metric: str,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    per_query = result.get("per_query", {})
    if not isinstance(per_query, dict) or not per_query:
        raise ValueError(
            "benchmark result does not contain per-query metrics; "
            "rerun run_benchmark.py"
        )

    baseline_name = resolve_model_name(per_query, baseline)
    contender_name = resolve_model_name(per_query, contender)
    if baseline_name == contender_name:
        raise ValueError("baseline and contender must be different models")

    selected_cutoff = cutoff if cutoff is not None else int(result.get("top_k", 0))
    available_cutoffs = {
        int(value) for value in result.get("top_ks", [result.get("top_k", 0)])
    }
    if selected_cutoff not in available_cutoffs:
        raise ValueError(
            f"k={selected_cutoff} is unavailable; "
            f"choose one of {sorted(available_cutoffs)}"
        )

    baseline_by_query = get_query_metric_values(
        per_query,
        model_name=baseline_name,
        cutoff=selected_cutoff,
        metric=metric,
    )
    contender_by_query = get_query_metric_values(
        per_query,
        model_name=contender_name,
        cutoff=selected_cutoff,
        metric=metric,
    )
    if baseline_by_query.keys() != contender_by_query.keys():
        raise ValueError("models must contain the same query IDs for paired comparison")

    query_ids = sorted(baseline_by_query)
    baseline_values = [baseline_by_query[query_id] for query_id in query_ids]
    contender_values = [contender_by_query[query_id] for query_id in query_ids]
    observed_delta, lower, upper = paired_bootstrap(
        baseline_values,
        contender_values,
        samples=samples,
        seed=seed,
    )
    significant = lower > 0.0 or upper < 0.0
    if significant and observed_delta > 0.0:
        direction = "contender_better"
    elif significant and observed_delta < 0.0:
        direction = "baseline_better"
    else:
        direction = "inconclusive"

    return {
        "baseline": baseline_name,
        "contender": contender_name,
        "metric": metric,
        "top_k": selected_cutoff,
        "query_count": len(query_ids),
        "bootstrap_samples": samples,
        "seed": seed,
        "baseline_mean": sum(baseline_values) / len(baseline_values),
        "contender_mean": sum(contender_values) / len(contender_values),
        "delta": observed_delta,
        "confidence_level": 0.95,
        "confidence_interval": {
            "lower": lower,
            "upper": upper,
        },
        "significant": significant,
        "direction": direction,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two models with a query-level paired bootstrap."
    )
    parser.add_argument("result", type=Path, help="Benchmark result JSON path.")
    parser.add_argument("--baseline", required=True, help="Baseline model name.")
    parser.add_argument("--contender", required=True, help="Contender model name.")
    parser.add_argument("--metric", choices=METRIC_CHOICES, default="ndcg")
    parser.add_argument("--top-k", type=int, help="Cutoff to compare. Default: largest.")
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, help="Write JSON to this path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.result.open(encoding="utf-8") as handle:
        benchmark_result = json.load(handle)

    try:
        result = compare_models(
            benchmark_result,
            baseline=args.baseline,
            contender=args.contender,
            cutoff=args.top_k,
            metric=args.metric,
            samples=args.samples,
            seed=args.seed,
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(f"{output}\n", encoding="utf-8")
        print(f"Wrote significance result to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
