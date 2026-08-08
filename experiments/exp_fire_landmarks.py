#!/usr/bin/env python3
"""FIRE landmark benchmark for the common registration pipeline."""
from pathlib import Path
import argparse
import json
import time

import numpy as np
import pandas as pd
from scipy.ndimage import map_coordinates

from src.metrics import jacobian_determinant_2d
from src.registration2d import (register, phase_translation_initialization,
                                robust_translation_initialization)
from src.operators import regularizer_symbol


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/fire"
OUT = ROOT / "results/real2d_v1"
METHODS = {
    "fixed_1_1": dict(method="fixed", rho_fixed=1.0, alpha_fixed=1.0),
    "fixed_1_18": dict(method="fixed", rho_fixed=1.0, alpha_fixed=1.8),
    "manual_external": dict(method="fixed", rho_fixed=0.1, alpha_fixed=1.0),
    "residual_balance": dict(method="residual_balance", rho_fixed=1.0, alpha_fixed=1.0),
    "adaptive_bb_proxy": dict(method="adaptive_bb", rho_fixed=1.0, alpha_fixed=1.0),
    "predict_pair_full": dict(method="predictor", reuse="pair_full"),
}


def metrics(displacement: np.ndarray, fixed: np.ndarray, moving: np.ndarray) -> dict:
    coords = np.vstack([fixed[:, 1], fixed[:, 0]])
    dy = map_coordinates(displacement[..., 0], coords, order=1, mode="nearest")
    dx = map_coordinates(displacement[..., 1], coords, order=1, mode="nearest")
    errors = np.linalg.norm(fixed + np.stack([dx, dy], axis=1) - moving, axis=1)
    initial = np.linalg.norm(fixed - moving, axis=1)
    return {"initial_tre": float(np.median(initial)), "median_tre": float(np.median(errors)),
            "mean_tre": float(np.mean(errors)), "p95_tre": float(np.quantile(errors, .95)),
            "median_rtre": float(np.median(errors) / (np.sqrt(2) * displacement.shape[0])),
            "landmark_improvement": float(1 - np.median(errors) / (np.median(initial) + 1e-12))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", default="APS", help="FIRE pair groups, e.g. APS or A")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--methods", default=",".join(METHODS))
    parser.add_argument("--tag", default="fire_landmarks")
    parser.add_argument("--initialization", choices=("phase", "robust"), default="phase")
    parser.add_argument("--data-dir", type=Path, default=DATA,
                        help="Prepared FIRE directory; e.g. data/processed/fire_256.")
    parser.add_argument("--reuse", choices=("pair_full", "pair", "level", "outer"),
                        default=None, help="Override predictor reuse policy for an ablation.")
    parser.add_argument("--outer-iterations", type=int, default=8)
    parser.add_argument("--max-iter", type=int, default=400)
    parser.add_argument("--beta", type=float, default=.2)
    parser.add_argument("--gamma", type=float, default=.05)
    parser.add_argument("--atol", type=float, default=1e-6)
    parser.add_argument("--rtol", type=float, default=1e-5)
    parser.add_argument("--max-completed", type=int, default=None,
                        help="Stop after this many newly completed method runs (resumable batches).")
    args = parser.parse_args()
    data = args.data_dir
    metadata = json.loads((data / "metadata.json").read_text())
    pairs = [p for p in metadata["pairs"] if p["group"] in args.groups]
    pairs = pairs[args.start:] if args.count is None else pairs[args.start:args.start + args.count]
    chosen = {key: METHODS[key].copy() for key in args.methods.split(",")}
    if args.reuse is not None:
        for kwargs in chosen.values():
            if kwargs["method"] == "predictor":
                kwargs["reuse"] = args.reuse
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"{args.tag}_{args.groups}_{args.start:03d}.csv"

    def append_rows(rows_to_add: list[dict]) -> None:
        """Checkpoint completed pairs, replacing only deliberate re-runs."""
        current = pd.DataFrame(rows_to_add)
        if target.exists():
            old = pd.read_csv(target)
            keys = ["pair", "method"]
            old = old.merge(current[keys].drop_duplicates(), on=keys, how="left", indicator=True)
            old = old[old["_merge"] == "left_only"].drop(columns="_merge")
            current = pd.concat([old, current], ignore_index=True)
        current.to_csv(target, index=False)

    rows = []
    completed_now = 0
    for index, pair in enumerate(pairs, start=args.start):
        fixed = np.load(data / f"{pair['fixed']}.npy")
        moving = np.load(data / f"{pair['moving']}.npy")
        points = np.load(data / f"control_points_{pair['pair']}.npz")
        started = time.perf_counter()
        initial = (phase_translation_initialization(fixed, moving)
                   if args.initialization == "phase"
                   else robust_translation_initialization(fixed, moving))
        init_seconds = time.perf_counter() - started
        pair_rows = []
        for name, kwargs in chosen.items():
            if target.exists():
                completed = pd.read_csv(target)
                already = ((completed["pair"] == pair["pair"]) &
                           (completed["method"] == name)).any()
                if already:
                    continue
            result = register(fixed, moving, factors=(4, 2, 1),
                              outer_iterations=args.outer_iterations, beta=args.beta,
                              gamma=args.gamma, atol=args.atol, rtol=args.rtol,
                              max_iter=args.max_iter, initial_displacement=initial, **kwargs)
            jac = jacobian_determinant_2d(result.displacement)
            first = result.records[0]
            last = result.records[-1]
            symbol = regularizer_symbol(fixed.shape, args.beta, args.gamma, order=1)
            q_initial = np.stack(np.gradient(moving), axis=-1)
            row = {"pair_index": index, **pair, "method": name,
                   "initialization_seconds": init_seconds, "solver_seconds": result.total_seconds,
                   "total_seconds": init_seconds + result.total_seconds,
                   "tuning_seconds": result.tuning_seconds,
                   "inner_iterations": sum(r["inner_iterations"] for r in result.records),
                   "failed_subproblems": sum(not r["inner_converged"] for r in result.records),
                   "accepted_steps": sum(r["accepted"] for r in result.records),
                   "subproblems": len(result.records), "min_jacobian": float(jac.min()),
                   "nonpositive_jacobian_fraction": float(np.mean(jac <= 0)),
                   "rho_initial": float(first["rho"]), "alpha_initial": float(first["alpha"]),
                   "rho_final": float(last["rho"]), "alpha_final": float(last["alpha"]),
                   "h_minus": 0.0, "h_plus": float(np.max(np.sum(q_initial*q_initial, axis=-1))),
                   "g_minus": float(symbol.min()), "g_plus": float(symbol.max()),
                   "prepared_size": int(fixed.shape[0]), "reuse_policy": kwargs.get("reuse", "fixed"),
                   **metrics(result.displacement, points["fixed"], points["moving"])}
            rows.append(row); pair_rows.append(row)
            # Method-granular checkpoints make long adaptive baseline runs
            # resumable without losing already timed methods for a pair.
            append_rows([row])
            completed_now += 1
            print(index, pair["pair"], name, "TRE", row["median_tre"], "time", row["total_seconds"], flush=True)
            if args.max_completed is not None and completed_now >= args.max_completed:
                print(json.dumps({"completed": completed_now, "path": str(target)}, indent=2))
                return
    print(json.dumps({"pairs": len(pairs), "rows": len(rows), "path": str(target)}, indent=2))


if __name__ == "__main__":
    main()
