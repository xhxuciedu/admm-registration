# Final editorial revision

## Main-paper changes

- Reframed convergence, four-corner prediction, and signed rate certification as distinct results.
- Added a strict Cayley-product contraction theorem and nullspace qualification.
- Made FIRE 256 the principal real-data result and retained all five tested methods.
- Replaced the exploratory FIRE figure with a vector 2×2 paired-analysis figure.
- Corrected the Song et al. AAAI citation and standardized one-shot/four-corner terminology.
- Renamed research-note-style headings to conventional scientific section titles.

## Supplementary information

`paper/supplementary.tex` contains reproducibility settings, baseline details,
legacy perturbation and signed-rate analyses, additional spectral experiments,
FIRE parameter/subgroup summaries, and the reuse ablation.

## Consistency checks

- FIRE clean table: 134 pairs × 5 methods.
- Headline statistics sourced from `results/real2d_v1/fire256_summary.json`.
- Tests include basic contraction, common-nullspace, and near-singular cases.
- Main and supplementary PDFs compile separately.
