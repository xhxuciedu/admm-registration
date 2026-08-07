# Reproducibility log: real2d_v1

- Branch: `real-registration-validation`
- Starting commit: `3dc78db3013b9ab2eed80f00b04d4455bc809a55`
- Date: 2026-08-06 (America/Los_Angeles)
- Python: 3.10.9, GCC 11.2.0
- NumPy: 2.2.6
- SciPy: 1.15.3
- pandas: 2.3.3
- Matplotlib: 3.10.9
- CPU: 2 x Intel Xeon Gold 5218, 32 physical/64 logical cores
- GPU: unavailable (`nvidia-smi` cannot communicate with a driver)
- Main seed: 20260806
- Predeclared configuration: `configs/real2d_v1.yaml`
- scikit-image: 0.25.2
- psutil: 7.2.2

## Initial reproduction

Commands:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m pytest -q
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_constant_coeff.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_structured_envelopes.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_variation_regimes.py
```

The original results were inspected but are not overwritten during this study. Reproduction copies and hashes are written by the audit script into this directory.

## Validation commands

```bash
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_four_corner_validation.py --start 0 --count 2500
# repeated for starts 2500, 5000, and 7500, then:
PYTHONPATH=. .venv/bin/python experiments/exp_four_corner_validation.py --merge
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_selector_scaling.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_certificate_scaling.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_public_sample_registration.py
PYTHONPATH=. MPLBACKEND=Agg MPLCONFIGDIR=/tmp .venv/bin/python experiments/analyze_real2d_v1.py
git clone --depth 1 https://github.com/Borda/dataset-histology-landmarks.git data/downloads/dataset-histology-landmarks
PYTHONPATH=. .venv/bin/python scripts/prepare_cima_sample.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_cima_landmarks.py --start 0 --count 10
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_cima_repeated_timing.py
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python experiments/exp_cima_spectral_baseline.py
PYTHONPATH=. MPLBACKEND=Agg MPLCONFIGDIR=/tmp .venv/bin/python experiments/analyze_cima.py
```

The public-sample experiment reserves deformation cases 1--2 for selecting one
global manual parameter pair and reports only held-out cases 3--5. The two
warm-up registrations are excluded from timing. See `RESEARCH_LOG.md` for the
discarded preliminary protocol and public-server acquisition failures.
