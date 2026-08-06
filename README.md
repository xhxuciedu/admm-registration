# Local spectral envelopes for ADMM registration

This repository reproduces the theory checks and controlled negative result in `paper/paper.tex`. The central certificate is valid in the tested cases, but its certified joint parameter selector fails the predeclared usefulness gate by choosing nearly zero relaxation. The project therefore makes no real-data registration claim.

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_constant_coeff.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_variable_coeff.py
cd paper && pdflatex -interaction=nonstopmode -halt-on-error paper.tex && pdflatex -interaction=nonstopmode -halt-on-error paper.tex
```

The experiment scripts overwrite only the machine-readable files under `results/`. The seed and gate are in `configs/controlled.yaml`. Raw results used by the paper are `results/raw/constant_coeff.json` and `results/raw/variable_coeff.csv`; the aggregate gate decision is `results/summary.json`.

## Layout

- `src/`: ADMM state matrices, local envelopes, algebraic candidates, operators, solver, and deformation metrics.
- `tests/`: double-precision algebra, spectral, transform, finite-difference, stopping-rule, and deformation checks.
- `experiments/`: committed result-generating scripts.
- `configs/`: seeds, parameter intervals, and the predeclared gate.
- `paper/`: completed negative-results manuscript and compiled PDF.
- `research_log.md`, `related_work_matrix.csv`, `internal_review.md`: derivation history, novelty audit, and reviewer-facing limitations.

## Scope

No medical dataset was bundled or downloaded. Gate 2 failed, so the mandated real-subproblem and end-to-end registration stages were intentionally not run. This is recorded in the manuscript and log rather than filled with unsupported values.
