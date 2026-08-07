#!/usr/bin/env python3
"""Paired statistical summary of the complete controlled FIRE run."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "results/real2d_v1/fire_full_128_APS_000.csv"
OUT = ROOT / "results/real2d_v1/fire_summary_128.json"
SEED = 20260806


def interval(values: np.ndarray) -> list[float]:
    rng = np.random.default_rng(SEED)
    draws = rng.choice(values, (10000, len(values)), replace=True)
    return [float(x) for x in np.quantile(np.median(draws, axis=1), [.025, .975])]


def summarize(base: pd.DataFrame, proposed: pd.DataFrame) -> dict:
    total = 1 - proposed.total_seconds.to_numpy() / base.total_seconds.to_numpy()
    solver = 1 - proposed.solver_seconds.to_numpy() / base.solver_seconds.to_numpy()
    iterations = 1 - proposed.inner_iterations.to_numpy() / base.inner_iterations.to_numpy()
    tre = proposed.median_tre.to_numpy() - base.median_tre.to_numpy()
    return {
        "pairs": int(len(base)),
        "median_total_runtime_reduction": float(np.median(total)),
        "median_total_runtime_reduction_ci95": interval(total),
        "median_solver_runtime_reduction": float(np.median(solver)),
        "median_iteration_reduction": float(np.median(iterations)),
        "median_tre_difference_px": float(np.median(tre)),
        "tre_worse_pairs": int(np.sum(tre > 1e-5)),
        "baseline_medians": {k: float(base[k].median()) for k in ("median_tre", "inner_iterations", "solver_seconds", "total_seconds")},
        "predictor_medians": {k: float(proposed[k].median()) for k in ("median_tre", "inner_iterations", "solver_seconds", "total_seconds")},
        "predictor_tuning_fraction": float(proposed.tuning_seconds.sum() / proposed.total_seconds.sum()),
        "nonpositive_jacobian_cases": int(np.sum(proposed.min_jacobian <= 0)),
        "nonconverged_subproblem_cases": int(np.sum(proposed.failed_subproblems > 0)),
    }


def main() -> None:
    data = pd.read_csv(PATH)
    required = {"manual_external", "predict_pair_full"}
    data = data[data.method.isin(required)].copy()
    if len(data) != 268 or set(data.method) != required or data.pair.nunique() != 134:
        raise ValueError("FIRE result is incomplete or has unexpected methods")
    table = data.set_index(["pair", "group", "method"]).sort_index()
    base = table.xs("manual_external", level="method")
    proposed = table.xs("predict_pair_full", level="method")
    result = {"protocol": {"resolution": [128, 128], "pairs": 134,
                           "methods": ["manual_external (rho=0.1, alpha=1)", "four-corner predictor, pair-full reuse"],
                           "initialization": "phase correlation", "threading": "one BLAS/OMP thread"},
              "overall": summarize(base, proposed),
              "by_group": {group: summarize(base.xs(group, level="group"), proposed.xs(group, level="group")) for group in "APS"}}
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    reductions = pd.DataFrame({
        "group": base.index.get_level_values("group"),
        "runtime_reduction": 100 * (1 - proposed.total_seconds.to_numpy() / base.total_seconds.to_numpy()),
        "tre_difference": proposed.median_tre.to_numpy() - base.median_tre.to_numpy(),
    })
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.0))
    groups = ["A", "P", "S"]
    axes[0].boxplot([reductions.loc[reductions.group == g, "runtime_reduction"] for g in groups], tick_labels=groups, showfliers=False)
    axes[0].axhline(0, color="0.35", linewidth=.8)
    axes[0].set(xlabel="FIRE group", ylabel="Paired total-time reduction (%)")
    for j, g in enumerate(groups, 1):
        values = reductions.loc[reductions.group == g, "runtime_reduction"].to_numpy()
        axes[0].scatter(np.full(len(values), j), values, s=7, alpha=.35, color="tab:blue")
    axes[1].axhline(0, color="0.35", linewidth=.8)
    for g, color in zip(groups, ["tab:blue", "tab:orange", "tab:green"]):
        values = reductions.loc[reductions.group == g, "tre_difference"].to_numpy()
        axes[1].scatter(np.arange(len(values)), values, s=11, alpha=.7, label=g, color=color)
    axes[1].set(xlabel="Pair index within group", ylabel="Predictor $-$ fixed TRE (px)")
    axes[1].legend(title="Group", frameon=False)
    fig.tight_layout()
    fig.savefig(ROOT / "figures/fire_paired_runtime.pdf")
    plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
