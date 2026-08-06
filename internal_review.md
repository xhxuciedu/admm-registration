# Internal review memo

The algebraic contribution is defensible: the exact relaxation convention, reduced Cayley product, frozen-patch modes, corner reduction, and noncommuting norm certificate are independently tested. The practical proposed contribution is not defensible as a positive method. In controlled variable-coefficient problems, the correction term drives relaxation to zero and penalty to the upper bound, making the iteration stagnate.

The clearest distinction from Song et al. (AAAI 2024) is structural: their method treats general LQPs through numerical spectral optimization, whereas this work derives a registration LFA symbol and finite algebraic certificate. A reviewer will correctly object that the new selector performs poorly and lacks real-data evidence. The paper therefore must remain framed as a limitation/negative result unless a tighter certificate passes the existing gate.

Likely objections include the small grids, one trial per factorial setting, a single mean-Hessian patch, no confidence intervals, no Song implementation with matched wall time, and no end-to-end registration. These are valid. They arise because the predeclared gate failed so strongly that expensive downstream evaluation would not test a viable method. Another objection is that the global operator norm discards interface locality and nonnormal structure; this is precisely the likely source of conservatism.

Recommended next work: derive patch-weighted resolvent bounds or an a posteriori Arnoldi/Lanczos correction; test multiple/overlapping patches; use a gate based on joint optimum as now implemented; then expand trial counts and only proceed to a small licensed 2D benchmark if the gate passes.

Recommended venue in the current state: a numerical optimization workshop, reproducibility/negative-results track, or technical report. It is not ready for a medical imaging methods venue.
