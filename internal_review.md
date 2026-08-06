# Internal review memo

The algebraic contribution is defensible: the exact relaxation convention, reduced Cayley product, frozen-patch modes, corner reduction, and noncommuting norm certificate are independently tested. The practical proposed contribution is not defensible as a positive method. In controlled variable-coefficient problems, the correction term drives relaxation to zero and penalty to the upper bound, making the iteration stagnate.

The clearest distinction from Song et al. (AAAI 2024) is structural: their method treats general LQPs through numerical spectral optimization, whereas this work derives a registration LFA symbol and finite algebraic certificate. A reviewer will correctly object that the new selector performs poorly and lacks real-data evidence. The paper therefore must remain framed as a limitation/negative result unless a tighter certificate passes the existing gate.

Likely objections include the small grids, one trial per factorial setting, a single mean-Hessian patch, no confidence intervals, no Song implementation with matched wall time, and no end-to-end registration. These are valid. They arise because the predeclared gate failed so strongly that expensive downstream evaluation would not test a viable method. Another objection is that the global operator norm discards interface locality and nonnormal structure; this is precisely the likely source of conservatism.

Recommended next work: derive patch-weighted resolvent bounds or an a posteriori Arnoldi/Lanczos correction; test multiple/overlapping patches; use a gate based on joint optimum as now implemented; then expand trial counts and only proceed to a small licensed 2D benchmark if the gate passes.

Recommended venue in the current state: a numerical optimization workshop, reproducibility/negative-results track, or technical report. It is not ready for a medical imaging methods venue.

## Revised assessment after structured-envelope work

The paper is no longer only a negative report. The joint constant-gradient finite-candidate theorem is a complete positive result, and exact pixel-curvature enumeration gives a strong empirical predictor (median smooth-case parameter gap 0.027). Block-Gershgorin and commutator rectangles rigorously preserve sign and eliminate the former boundary collapse. However, their parameter gaps remain 0.560 and 0.431 on the original stress set and above 0.3 on the small smooth-regime study. The pixel-curvature predictor must not be described as a spectral enclosure until a rotating-field proof is found.

The most likely reviewer objection is now sharper: why prefer a rigorous bound that does not tune well, or a predictor that is not rigorous? The honest answer is that this revision maps the gap between them and identifies the symmetric dense-Cayley row sum, rather than the skew commutator term, as the remaining bottleneck. Larger grids, repetitions, adaptive patches, and real registration are still absent. The appropriate framing remains a theory/technical report, not yet a validated medical-registration method.

Predict-then-certify partially resolves this objection: the predictor chooses useful parameters and the independent Perron comparison bound certifies convergence without moving them. All ten regime bounds were below one, while median parameter quality passed the gate. This is a legitimate positive methodology, but not evidence of registration runtime benefit. The remaining reviewer concern is certificate tightness (median relative gap 1.29) and the very small synthetic sample.
