"""Shared guard for downstream experiments stopped by the research protocol."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def require_gate_2():
    summary = json.loads((ROOT / "results" / "summary.json").read_text())
    if not summary["gate_2_passed"]:
        raise SystemExit(
            "Gate 2 failed: controlled median relative spectral-radius gap "
            f"{summary['median_relative_radius_gap']:.3f} >= "
            f"{summary['gate_threshold']:.3f}. Downstream data experiments are intentionally stopped."
        )

