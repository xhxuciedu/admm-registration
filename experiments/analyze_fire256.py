#!/usr/bin/env python3
"""Audit, summarize, and plot the final FIRE 256 validation table.

The script keeps raw resumable shard files untouched.  A five-method P21
rerun replaces the only rows affected by an early overlapping checkpoint; the
audit JSON makes that replacement explicit.
"""
from __future__ import annotations

import json
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "real2d_v1"
FIGURES = ROOT / "figures"
PAPER = ROOT / "paper"
METHODS = ["manual_external", "fixed_1_18", "residual_balance",
           "adaptive_bb_proxy", "predict_pair_full"]
LABELS = {"manual_external": "Validation-selected fixed\n(0.1, 1.0)",
          "fixed_1_18": "Fixed oADMM\n(1.0, 1.8)",
          "residual_balance": "Residual\nbalancing",
          "adaptive_bb_proxy": "BB adaptive\nproxy",
          "predict_pair_full": "Four-corner\none-shot"}
COLORS = {"manual_external": "#7f7f7f", "fixed_1_18": "#b0b0b0",
          "residual_balance": "#c98b2e", "adaptive_bb_proxy": "#6b8e23",
          "predict_pair_full": "#0072b2"}


def ci_median(values: np.ndarray, rng: np.random.Generator, draws: int = 10_000) -> list[float]:
    values = np.asarray(values, float)
    samples = rng.choice(values, size=(draws, len(values)), replace=True)
    return [float(x) for x in np.quantile(np.median(samples, axis=1), [.025, .975])]


def method_summary(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method in METHODS:
        x = data[data.method == method]
        rows.append({"method": method, "label": LABELS[method], "n": len(x),
                     "median_iterations": float(x.inner_iterations.median()),
                     "iqr_iterations": float(x.inner_iterations.quantile(.75)-x.inner_iterations.quantile(.25)),
                     "median_total_seconds": float(x.total_seconds.median()),
                     "iqr_total_seconds": float(x.total_seconds.quantile(.75)-x.total_seconds.quantile(.25)),
                     "median_tuning_seconds": float(x.tuning_seconds.median()),
                     "median_tre": float(x.median_tre.median()),
                     "iqr_tre": float(x.median_tre.quantile(.75)-x.median_tre.quantile(.25)),
                     "nonpositive_fields": int((x.nonpositive_jacobian_fraction > 0).sum()),
                     "minimum_jacobian": float(x.min_jacobian.min())})
    return pd.DataFrame(rows)


def paired(data: pd.DataFrame, baseline: str, rng: np.random.Generator) -> dict:
    wide = data.pivot(index="pair", columns="method",
                      values=["total_seconds", "inner_iterations", "median_tre"])
    runtime_pct = 100 * (wide["total_seconds"][baseline] - wide["total_seconds"]["predict_pair_full"]) / wide["total_seconds"][baseline]
    iteration_pct = 100 * (wide["inner_iterations"][baseline] - wide["inner_iterations"]["predict_pair_full"]) / wide["inner_iterations"][baseline]
    tre_delta = wide["median_tre"]["predict_pair_full"] - wide["median_tre"][baseline]
    return {"baseline": baseline, "baseline_label": LABELS[baseline], "n": int(len(wide)),
            "median_runtime_difference_seconds": float((wide["total_seconds"][baseline]-wide["total_seconds"]["predict_pair_full"]).median()),
            "median_runtime_improvement_pct": float(runtime_pct.median()),
            "runtime_improvement_iqr_pct": float(runtime_pct.quantile(.75)-runtime_pct.quantile(.25)),
            "runtime_improvement_bootstrap_95_pct": ci_median(runtime_pct.to_numpy(), rng),
            "faster_pair_fraction": float((runtime_pct > 0).mean()),
            "median_iteration_improvement_pct": float(iteration_pct.median()),
            "iteration_improvement_bootstrap_95_pct": ci_median(iteration_pct.to_numpy(), rng),
            "median_tre_difference_px": float(tre_delta.median()),
            "max_absolute_tre_difference_px": float(np.abs(tre_delta).max())}


def plot_headline(data: pd.DataFrame, strongest: str) -> None:
    plt.rcParams.update({"font.size": 9, "axes.labelsize": 9, "axes.titlesize": 10,
                         "xtick.labelsize": 8, "ytick.labelsize": 8, "pdf.fonttype": 42,
                         "ps.fonttype": 42, "axes.linewidth": .8})
    FIGURES.mkdir(exist_ok=True)
    proposed = data[data.method == "predict_pair_full"].set_index("pair")
    base = data[data.method == strongest].set_index("pair")
    common = proposed.index.intersection(base.index)
    p, b = proposed.loc[common], base.loc[common]
    runtime = 100 * (b.total_seconds-p.total_seconds)/b.total_seconds
    iterations = 100 * (b.inner_iterations-p.inner_iterations)/b.inner_iterations
    fig, ax = plt.subplots(2, 2, figsize=(7.15, 5.55), constrained_layout=True)
    groups = ["A", "P", "S"]
    for axis, values, title, ylabel in [(ax[0, 0], runtime, "Paired total-runtime improvement", "Improvement (%)"),
                                        (ax[0, 1], iterations, "Paired inner-iteration improvement", "Improvement (%)")]:
        samples = [values[p.group == g].to_numpy() for g in groups]
        bp = axis.boxplot(samples, tick_labels=[f"{g}\n(n={len(x)})" for g, x in zip(groups, samples)], patch_artist=True, showfliers=False,
                          medianprops={"color": "black", "linewidth": 1.4})
        for box in bp["boxes"]: box.set(facecolor="#9ecae1", edgecolor="#0072b2")
        axis.axhline(0, color="0.35", lw=.8); axis.set(title=title, ylabel=ylabel)
        axis.grid(axis="y", color=".9", lw=.6)
    tre_delta = p.median_tre - b.median_tre
    tre_samples = [tre_delta[p.group == g].to_numpy() for g in groups]
    bp = ax[1, 0].boxplot(
        tre_samples,
        tick_labels=[f"{g}\n(n={len(x)})" for g, x in zip(groups, tre_samples)],
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "black", "linewidth": 1.4},
    )
    for box in bp["boxes"]:
        box.set(facecolor="#c7e9c0", edgecolor="#238b45")
    rng = np.random.default_rng(20260811)
    for j, values in enumerate(tre_samples, 1):
        ax[1, 0].scatter(
            j + rng.normal(0, .045, len(values)),
            values,
            s=12,
            alpha=.55,
            color="#238b45",
            edgecolors="none",
        )
    ax[1, 0].axhline(0, color=".35", lw=.8)
    ax[1, 0].set(
        title="Landmark-accuracy difference",
        ylabel=r"$\Delta$TRE: four-corner $-$ fixed (px)",
    )
    for group, color in zip(groups,["#0072b2","#d55e00","#009e73"]):
        z=p[p.group==group]; ax[1,1].scatter(z.h_plus,z.rho_initial,s=18,alpha=.75,label=group,color=color,edgecolors="none")
    ax[1,1].set(title="Image-dependent penalty selection",xlabel=r"Maximum curvature $h_+$",ylabel=r"Predicted penalty $\rho_{\mathrm{4C}}$")
    ax[1,1].legend(title="FIRE group",frameon=False,fontsize=8,title_fontsize=8,ncol=3,loc="upper right")
    for label,axis in zip(["(a)","(b)","(c)","(d)"],ax.flat): axis.text(-.16,1.08,label,transform=axis.transAxes,fontweight="bold",fontsize=10)
    fig.savefig(FIGURES / "fire256_headline.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / "fire256_headline.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_baselines(summary: pd.DataFrame) -> None:
    FIGURES.mkdir(exist_ok=True)
    ordered = summary.sort_values("median_total_seconds", ascending=False)
    fig, ax = plt.subplots(1, 2, figsize=(10.6, 4.2), constrained_layout=True)
    labels = [LABELS[m].replace("\n", " ") for m in ordered.method]
    colors = [COLORS[m] for m in ordered.method]
    ax[0].barh(labels, ordered.median_total_seconds, color=colors)
    ax[0].set(xlabel="Median end-to-end time (s)", title="FIRE 256 runtime")
    ax[1].barh(labels, ordered.median_iterations, color=colors)
    ax[1].set(xlabel="Median inner ADMM iterations", title="FIRE 256 optimization work")
    for axis, values in [(ax[0], ordered.median_total_seconds), (ax[1], ordered.median_iterations)]:
        for i, value in enumerate(values): axis.text(value, i, f" {value:.2f}" if axis is ax[0] else f" {value:.0f}", va="center", fontsize=8)
    fig.savefig(FIGURES / "fire256_baselines.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / "fire256_baselines.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_fire_table(summary: pd.DataFrame, data: pd.DataFrame) -> None:
    """Generate the manuscript table from the audited pair-level table."""
    normalized = 100 * data.groupby("method").median_rtre.median()
    rows = []
    for method in ["manual_external", "residual_balance", "adaptive_bb_proxy", "fixed_1_18", "predict_pair_full"]:
        item = summary.set_index("method").loc[method]
        label = LABELS[method].replace("\n", " ")
        if method == "predict_pair_full":
            label = r"\textbf{" + label + "}"
        rows.append(f"{label} & {item.median_iterations:.1f} & {item.median_total_seconds:.3f} & {item.median_tre:.5f} & {normalized[method]:.5f}\\\\")
    target = PAPER / "generated"
    target.mkdir(exist_ok=True)
    (target / "fire256_table.tex").write_text("\n".join(rows + [r"\bottomrule"]) + "\n")


def rebuild_clean_table() -> pd.DataFrame:
    """Reconstruct the audited table from checkpoints; used only for audit."""
    metadata = json.loads((ROOT / "data/processed/fire_256/metadata.json").read_text())
    expected = {p["pair"] for p in metadata["pairs"]}
    shard_paths = sorted(RESULTS.glob("fire256_full_APS_*.csv"))
    raw = pd.concat([pd.read_csv(p) for p in shard_paths], ignore_index=True)
    malformed = raw[~raw.pair.astype(str).isin(expected)].copy()
    data = raw[raw.pair.astype(str).isin(expected)].copy()
    # The P21--P26 clean rerun supersedes all rows affected by the early
    # overlapping checkpoint process.
    replacement_pairs = {f"P{i:02d}" for i in range(15, 50)}
    replacement_pairs |= {"S01", "S02", "S03", "S04"}
    replacement_pairs |= {"A11", "P14"}
    replacement_paths = [RESULTS / "fire256_clean_P15_P17_APS_028.csv",
                         RESULTS / "fire256_clean_P18_P20_APS_031.csv",
                         RESULTS / "fire256_clean_P21_P24_APS_034.csv",
                         RESULTS / "fire256_clean_P25_P28_APS_038.csv",
                         RESULTS / "fire256_clean_P29_P32_APS_042.csv",
                         RESULTS / "fire256_clean_P33_P34_APS_046.csv",
                         RESULTS / "fire256_clean_P35_P38_APS_048.csv",
                         RESULTS / "fire256_clean_P39_P42_APS_052.csv",
                         RESULTS / "fire256_clean_P43_P46_APS_056.csv",
                         RESULTS / "fire256_clean_P47_P49_APS_060.csv"]
    replacement_paths.append(RESULTS / "fire256_clean_S01_S02_APS_063.csv")
    replacement_paths.append(RESULTS / "fire256_clean_S03_S04_APS_065.csv")
    replacement_paths.extend([RESULTS / "fire256_clean_A11_APS_010.csv",
                              RESULTS / "fire256_clean_P14_APS_027.csv"])
    replacement = pd.concat([pd.read_csv(p) for p in replacement_paths], ignore_index=True)
    replacement = replacement[replacement.pair.isin(replacement_pairs)].copy()
    data = pd.concat([data[~data.pair.isin(replacement_pairs)], replacement], ignore_index=True)
    data = data[data.method.isin(METHODS)].copy()
    assert set(data.pair) == expected
    assert not data.duplicated(["pair", "method"]).any()
    assert len(data) == len(expected) * len(METHODS)
    data.to_csv(RESULTS / "fire256_final_clean.csv", index=False)
    malformed.to_csv(RESULTS / "fire256_excluded_malformed_rows.csv", index=False)
    return data


def validate_clean_table(data: pd.DataFrame) -> None:
    """Fail loudly if the committed analysis input is incomplete or malformed."""
    assert set(data.method) == set(METHODS)
    assert data.pair.nunique() == 134
    assert len(data) == 134 * len(METHODS)
    assert not data.duplicated(["pair", "method"]).any()
    assert (data.prepared_size == 256).all()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild-clean", action="store_true",
                        help="Rebuild the audited table from raw checkpoint files (requires processed FIRE metadata).")
    args = parser.parse_args()
    if args.rebuild_clean:
        data = rebuild_clean_table()
    else:
        data = pd.read_csv(RESULTS / "fire256_final_clean.csv")
    validate_clean_table(data)

    rng = np.random.default_rng(20260807)
    summary = method_summary(data)
    summary.to_csv(RESULTS / "fire256_method_summary.csv", index=False)
    write_fire_table(summary, data)
    baseline_candidates = [m for m in METHODS if m != "predict_pair_full"]
    strongest = summary[summary.method.isin(baseline_candidates)].sort_values("median_total_seconds").iloc[0].method
    comparisons = [paired(data, m, rng) for m in baseline_candidates]
    pd.DataFrame(comparisons).to_csv(RESULTS / "fire256_paired_comparisons.csv", index=False)
    group = []
    for g in "APS":
        group.append({"group": g, **paired(data[data.group == g], strongest, rng)})
    pd.DataFrame(group).to_csv(RESULTS / "fire256_group_paired_comparisons.csv", index=False)

    reuse_parts = []
    for tag, policy in [("fire256_reuse_one_shot", "one_shot"), ("fire256_reuse_per_level", "per_level")]:
        reuse_parts.extend([pd.read_csv(p).assign(policy=policy) for p in RESULTS.glob(f"{tag}_*_000.csv")])
    reuse = pd.concat(reuse_parts, ignore_index=True)
    reuse_summary = (reuse.groupby("policy").agg(n=("pair", "nunique"), median_tuning_seconds=("tuning_seconds", "median"),
                    median_iterations=("inner_iterations", "median"), median_total_seconds=("total_seconds", "median"),
                    median_tre=("median_tre", "median")).reset_index())
    reuse_summary.to_csv(RESULTS / "fire256_reuse_summary.csv", index=False)
    audit = {"expected_pairs": int(data.pair.nunique()), "final_rows": len(data),
             "analysis_input": "fire256_final_clean.csv", "strongest_practical_baseline": strongest,
             "method_summary": summary.to_dict(orient="records"), "paired_comparisons": comparisons,
             "reuse_summary": reuse_summary.to_dict(orient="records")}
    (RESULTS / "fire256_summary.json").write_text(json.dumps(audit, indent=2) + "\n")
    plot_headline(data, strongest)
    plot_baselines(summary)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
