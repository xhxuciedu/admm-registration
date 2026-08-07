# Local spectral envelopes for ADMM registration

This repository reproduces the exact constant-gradient theorem, signed enclosures, and predict-then-certify method in `paper/paper.tex`. The global rank-one predictor now uses exactly four curvature/symbol corners; a Perron or sparse truncated-kernel comparison matrix can separately certify the full variable-coefficient iteration.

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
PYTHONPATH=. .venv/bin/python experiments/exp_selector_scaling.py
PYTHONPATH=. .venv/bin/python experiments/exp_certificate_scaling.py
PYTHONPATH=. .venv/bin/python experiments/exp_public_sample_registration.py
PYTHONPATH=. .venv/bin/python scripts/prepare_cima_sample.py
PYTHONPATH=. .venv/bin/python experiments/exp_cima_landmarks.py --start 0 --count 10
PYTHONPATH=. .venv/bin/python experiments/exp_cima_repeated_timing.py
PYTHONPATH=. .venv/bin/python experiments/exp_cima_spectral_baseline.py
MPLBACKEND=Agg MPLCONFIGDIR=/tmp PYTHONPATH=. .venv/bin/python experiments/analyze_cima.py
PYTHONPATH=. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 .venv/bin/python scripts/prepare_fire.py --size 128
PYTHONPATH=. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 .venv/bin/python experiments/exp_fire_landmarks.py --groups APS --tag fire_full_128 --methods manual_external,predict_pair_full --initialization phase
MPLBACKEND=Agg MPLCONFIGDIR=/tmp PYTHONPATH=. .venv/bin/python experiments/analyze_fire.py
cd paper && pdflatex -interaction=nonstopmode -halt-on-error paper.tex && pdflatex -interaction=nonstopmode -halt-on-error paper.tex
```

The original experiment scripts write their historical files under `results/`. The real-validation study writes only to the versioned `results/real2d_v1/` directory. Its seed, tolerances, timing repetitions, and success criteria were predeclared in `configs/real2d_v1.yaml` before the final runs.

## Layout

- `src/`: ADMM state matrices, local envelopes, algebraic candidates, operators, solver, and deformation metrics.
- `tests/`: double-precision algebra, spectral, transform, finite-difference, stopping-rule, and deformation checks.
- `experiments/`: committed result-generating scripts.
- `configs/`: seeds, parameter intervals, and the predeclared gate.
- `paper/`: revised signed-envelope manuscript and compiled PDF.
- `data/`: dataset provenance, download scripts, and ignored raw/processed data.
- `RESEARCH_LOG.md`: current successes, discarded runs, acquisition failures, and limitations.
- `research_log.md`, `related_work_matrix.csv`, `internal_review.md`: earlier derivation history, novelty audit, and reviewer-facing limitations.

## Scope

The scikit-image retina and immunohistochemistry samples provide controlled
known-deformation engineering validation. The CIMA lung-lesion sample provides
ten differently stained landmark pairs and supports the matched-accuracy runtime
claim in the paper. FIRE provides 134 retinal landmark pairs; the completed
128x128 CPU study supports the second matched-accuracy runtime claim. Raw FIRE
data remain local and are counted only after the archive passes `7z t`.
