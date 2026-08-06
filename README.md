# Local spectral envelopes for ADMM registration

This repository reproduces the exact constant-gradient theorem, signed enclosures, and predict-then-certify method in `paper/paper.tex`. Pixel curvatures select parameters algebraically; a Perron comparison matrix then certifies the full variable-coefficient iteration. All ten regime cases received bounds below one, while the smooth-field median parameter gap was 0.027.

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_constant_coeff.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_variable_coeff.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_structured_envelopes.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_variation_regimes.py
MPLBACKEND=Agg MPLCONFIGDIR=/tmp .venv/bin/python experiments/plot_structured_results.py
cd paper && pdflatex -interaction=nonstopmode -halt-on-error paper.tex && pdflatex -interaction=nonstopmode -halt-on-error paper.tex
```

The experiment scripts overwrite only the machine-readable files under `results/`. The seed and gate are in `configs/controlled.yaml`. Raw results used by the paper are `results/raw/constant_coeff.json` and `results/raw/variable_coeff.csv`; the aggregate gate decision is `results/summary.json`.

## Layout

- `src/`: ADMM state matrices, local envelopes, algebraic candidates, operators, solver, and deformation metrics.
- `tests/`: double-precision algebra, spectral, transform, finite-difference, stopping-rule, and deformation checks.
- `experiments/`: committed result-generating scripts.
- `configs/`: seeds, parameter intervals, and the predeclared gate.
- `paper/`: revised signed-envelope manuscript and compiled PDF.
- `research_log.md`, `related_work_matrix.csv`, `internal_review.md`: derivation history, novelty audit, and reviewer-facing limitations.

## Scope

No medical dataset was bundled or downloaded. Predict-then-certify passes convergence, parameter-quality, and noncollapse gates, but not the certificate-tightness gate; real-subproblem and end-to-end stages remain gated.
