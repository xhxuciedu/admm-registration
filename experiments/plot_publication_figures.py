#!/usr/bin/env python3
"""Generate compact vector figures for the final manuscript."""
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
REAL = ROOT / "results" / "real2d_v1"
FIG = ROOT / "figures"
COLORS = {"blue": "#0072B2", "orange": "#D55E00", "green": "#009E73",
          "purple": "#CC79A7", "gray": "#666666", "light": "#D9EAF7"}


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.labelsize": 9, "axes.titlesize": 10, "legend.fontsize": 8,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "pdf.fonttype": 42,
        "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": .8, "xtick.major.width": .8, "ytick.major.width": .8,
    })


def panel_label(ax, text: str) -> None:
    ax.text(-0.22, 1.12, text, transform=ax.transAxes,
            fontsize=10, fontweight="bold", va="top", ha="left")


def algebraic_figure() -> None:
    constant = json.loads((RAW / "constant_coeff.json").read_text())
    n = np.array([row["n"] for row in constant])
    error = np.array([row["absolute_error"] for row in constant])
    regimes = pd.read_csv(RAW / "variation_regimes.csv")
    predictor = regimes[regimes.method == "pixel_curvature_predictor"].copy()
    certificate = regimes[regimes.method == "predict_then_certify"].copy()

    fig, axes = plt.subplots(1, 3, figsize=(7.25, 2.45), constrained_layout=True)
    ax = axes[0]
    ax.semilogy(n, np.maximum(error, 1e-17), "o-", color=COLORS["blue"], lw=1.7, ms=5)
    ax.axhline(1e-14, color=COLORS["gray"], ls="--", lw=.9)
    ax.set(title="Constant coefficients", xlabel="Grid side length",
           ylabel=r"$|U_{\mathrm{4C}}-\varrho(E_{\rho,\alpha})|$")
    ax.set_xticks(n)
    ax.text(.05, .90, "machine precision", transform=ax.transAxes, color=COLORS["gray"],
            fontsize=8, va="top")
    panel_label(ax, "(a)")

    ax = axes[1]
    all_gap = predictor.parameter_gap.to_numpy()
    smooth_gap = predictor[predictor.smooth].parameter_gap.to_numpy()
    box = ax.boxplot([all_gap, smooth_gap], tick_labels=["all", "smooth"], widths=.55,
                     patch_artist=True, showfliers=True,
                     medianprops={"color": "black", "linewidth": 1.2})
    for p, color in zip(box["boxes"], [COLORS["light"], "#BFE3D0"]):
        p.set(facecolor=color, edgecolor=COLORS["gray"])
    rng = np.random.default_rng(20260806)
    for j, values in enumerate([all_gap, smooth_gap], 1):
        ax.scatter(j + rng.normal(0, .045, len(values)), values, s=15, alpha=.75, color=COLORS["blue"])
    ax.axhline(.10, color=COLORS["orange"], ls="--", lw=1.1, label="quality gate")
    ax.set(title="Predictor quality", ylabel="Spectral-radius regret")
    ax.legend(frameon=False, loc="upper right")
    panel_label(ax, "(b)")

    ax = axes[2]
    actual = certificate.actual_radius.to_numpy()
    bound = certificate.bound.to_numpy()
    ax.scatter(actual, bound, s=35, color=COLORS["green"], edgecolor="white", linewidth=.5)
    lo, hi = 0, max(1.02, 1.05 * bound.max())
    ax.plot([lo, hi], [lo, hi], color=COLORS["gray"], ls="--", lw=1, label="exact")
    ax.axhline(1, color=COLORS["orange"], ls=":", lw=1, label="convergence threshold")
    ax.set(xlim=(lo, hi), ylim=(lo, hi), title="Certificate behavior",
           xlabel=r"True spectral radius $\varrho(E_{\rho,\alpha})$", ylabel="Rigorous bound")
    ax.legend(frameon=False, loc="upper left")
    panel_label(ax, "(c)")
    fig.savefig(FIG / "algebraic_validation.pdf", bbox_inches="tight")
    plt.close(fig)


def registration_figure() -> None:
    cima = pd.read_csv(REAL / "cima_landmarks_part_00.csv")
    fire = pd.read_csv(REAL / "fire_full_128_APS_000.csv")
    fire = fire[fire.method.isin(["manual_external", "predict_pair_full"])]
    fwide = fire.pivot(index=["pair", "group"], columns="method",
                       values=["total_seconds", "median_tre"])
    runtime = 100 * (1 - fwide["total_seconds"]["predict_pair_full"] /
                     fwide["total_seconds"]["manual_external"])
    tre_diff = (fwide["median_tre"]["predict_pair_full"] -
                fwide["median_tre"]["manual_external"])

    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.05), constrained_layout=True)
    ax = axes[0, 0]
    p = cima[cima.method == "predict_pair_full"].sort_values("pair_index")
    ax.plot(p.pair_index, p.initial_tre, "o--", color=COLORS["gray"], lw=1.2, ms=4, label="initial")
    ax.plot(p.pair_index, p.median_tre, "o-", color=COLORS["blue"], lw=1.8, ms=4, label="registered")
    ax.set(title="CIMA landmark accuracy", xlabel="Pair", ylabel="Median TRE (px)")
    ax.legend(frameon=False)

    ax = axes[0, 1]
    order = ["fixed_1_1", "fixed_1_18", "residual_balance", "adaptive_bb_proxy",
             "manual_external", "predict_pair_full"]
    labels = ["fixed\n(1, 1)", "fixed\n(1, 1.8)", "residual\nbalancing",
              "BB\nproxy", "external\nfixed", "four-\ncorner"]
    med = cima.groupby("method").total_seconds.median().reindex(order)
    bars = ax.bar(np.arange(len(order)), med, color=[COLORS["gray"]] * 5 + [COLORS["blue"]])
    ax.set(title="CIMA runtime", ylabel="Median total time (s)", xticks=np.arange(len(order)), xticklabels=labels)
    ax.bar_label(bars, labels=[f"{v:.1f}" for v in med], fontsize=7, padding=1)

    ax = axes[1, 0]
    groups = ["A", "P", "S"]
    values = [runtime.loc[runtime.index.get_level_values("group") == g].to_numpy() for g in groups]
    box = ax.boxplot(values, tick_labels=groups, widths=.55, patch_artist=True, showfliers=False,
                     medianprops={"color": "black", "linewidth": 1.2})
    for p, color in zip(box["boxes"], [COLORS["light"], "#F7D3C5", "#BFE3D0"]):
        p.set(facecolor=color, edgecolor=COLORS["gray"])
    rng = np.random.default_rng(20260806)
    for j, v in enumerate(values, 1):
        ax.scatter(j + rng.normal(0, .045, len(v)), v, s=10, alpha=.45, color=COLORS["blue"])
    ax.axhline(0, color=COLORS["gray"], lw=.8)
    ax.set(title="FIRE paired runtime", xlabel="Benchmark group", ylabel="Total-time reduction (%)")

    ax = axes[1, 1]
    for g, color in zip(groups, [COLORS["blue"], COLORS["orange"], COLORS["green"]]):
        v = tre_diff.loc[tre_diff.index.get_level_values("group") == g].to_numpy()
        ax.scatter(np.arange(1, len(v) + 1), v, s=13, alpha=.75, color=color, label=g)
    ax.axhline(0, color=COLORS["gray"], lw=.8)
    ax.set(title="FIRE landmark accuracy", xlabel="Pair index within group",
           ylabel="Predictor $-$ fixed TRE (px)")
    ax.legend(title="Group", frameon=False, ncol=3, loc="upper right")
    fig.savefig(FIG / "registration_results.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    style()
    algebraic_figure()
    registration_figure()
