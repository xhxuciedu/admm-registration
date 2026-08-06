# Research log

## 2026-08-06: setup and audit

- Read the supplied prompt and 740-line manuscript. The repository contained no code or data.
- Recorded starting Git commit `d5e7664` (`init`).
- Created `.venv` with Python 3.10 and installed the pinned-range scientific stack from `requirements.txt`.
- Fixed random seed at 20260806 and set the controlled usefulness gate to median relative spectral-radius gap below 0.10 before running it.
- Reviewed primary-source records for Boyd et al., Ghadimi et al., Teixeira et al., Giselsson--Boyd, Xu--Figueiredo--Goldstein, Wohlberg, Song et al., and Thorley et al. The closest novelty conflict is Song et al. 2024: they numerically optimize the LQP penalty spectrum and derive relaxation conditional on it; the proposed distinction is registration-specific LFA plus a finite certified envelope.

## Algebra and implementation

- Derived the homogeneous `[w,u]` state map for `z = alpha*v + (1-alpha)*w`, followed by the `w` and scaled-dual updates.
- Verified numerically that its nonzero spectrum equals that of `(1-alpha/2)I + (alpha/2) C_H C_G` for random noncommuting SPD matrices and `alpha` in `{0.5,1,1.7,2}`.
- Verified the commuting frozen symbol and the curvature-corner reduction. The absolute value is convex in the scalar modal value, so zero crossings do not invalidate the corner argument.
- Verified the Cayley resolvent identity and the norm certificate on 50 random noncommuting perturbations. No violation was found.
- Implemented finite algebraic penalty candidates: endpoints, pairwise rational-branch intersections, and verified real roots of `rho^2 s(rho^2-hg)-delta D(rho)^2`. During review, an initially coded spurious `2hg*rho` term in the derivative was caught, removed, and all tests/experiments were rerun.
- Implemented relaxation candidates as every vertex of the upper envelope of signed affine modal branches. Checked penalty and relaxation candidate minima against dense diagnostic grids.

## Experiments and failed hypothesis

- Constant periodic grids `n={4,6,8}`: selected `(rho,alpha)=(0.5435121023541,1.8981520704591)`; local-vs-direct radius absolute errors were `0`, `9.99e-16`, and `5.00e-16`.
- First controlled run compared against penalty optimization at the already selected alpha. This produced a tiny but scientifically meaningless gap because the certified joint selector had collapsed to `alpha=1e-6`. The statistic was rejected and replaced by genuinely joint full-spectrum diagnostic optimization.
- Final controlled experiment: 18 cases spanning grid sizes 4/5, magnitude contrasts 1/4/16, and orientation frequencies 0/1/3. The certificate had zero violations.
- Negative result: every certified joint selection chose `rho=100` and `alpha=1e-6`, with spectral radius approximately one. Median/mean/max relative gaps to joint spectral optimization were 2.904/2.839/4.505. The predeclared 0.10 gate failed.
- Per protocol, real subproblem and end-to-end 2D/3D experiments were not run. No public dataset, Dice, TRE, Jacobian, runtime, or GPU claim is made.

## Manuscript decision

- Reframed the paper as a negative-results report. Retained the verified algebra and certificate, removed all placeholders, and explicitly reported why the certificate is not presently a useful tuner.
- Recommended next direction: interface-local or weighted resolvent bounds, followed by rerunning Gate 2 before any medical-data study.

## 2026-08-06: signed structured-envelope phase

- Kept the global certificate as a baseline and retained the exact global regularizer in every new method.
- Implemented the exact pixel-block Cayley mismatch. On the original 18 cases its median enclosure gap improved to 0.166, but its median parameter gap was 0.926 and 6/18 selections still collapsed.
- Proved and implemented block-Gershgorin disks using exact $C_i$ blocks and exact scalar $K_\rho$. All 18 certificates held; no selection collapsed. Median enclosure and parameter gaps were 0.644 and 0.560.
- Derived the local symmetric/skew blocks $S_{ij}=k_{ij}(C_i+C_j)/2$ and $Q_{ij}=k_{ij}(C_i-C_j)/2$. Hermitian block-Gershgorin plus the symmetric block-norm row sum gives the rectangle certificate. The skew radius is zero for constant Hessians. All numerical certificate tests passed; median parameter gap improved to 0.431 without collapse.
- Derived and tested $\|[C_H,C_G]\|\le4\rho^2\|[H,G]\|/((h_{\min}+\rho)^2(g_{\min}+\rho)^2)$ from the inverse commutator identity. Tests compare against the explicit Cayley commutator.
- Completed the joint constant-gradient theorem. Eliminating fixed-$\rho$ relaxation produces $(b-a)/(2-a-b)$ or $2b-1$; branch intersections, $a+b=1$ transitions, stationary polynomial roots, and endpoints form a finite candidate superset. A 2D dense diagnostic test agrees with the finite result.
- Ran ten separated regimes (magnitude, orientation, discontinuity, and Gaussian-smoothed image gradients). The exact pixel-curvature predictor, which is not certified under rotation, achieved median parameter gap 0.057 overall and 0.027 over nine smooth cases, with no collapse. A strengthened multistart full-spectrum oracle was used after a low-budget differential-evolution oracle was found suboptimal.
- Gates: exact algebra passes; the pixel-curvature predictor passes empirical parameter quality and robustness; none of the rigorous variable-coefficient enclosures passes both tightness and parameter-quality gates. Real-data experiments therefore remain gated.

## 2026-08-06: Perron comparison and predict-then-certify

- Replaced maximum block row sums by scalar comparison matrices using $\lambda_{\min}(\operatorname{diag}(d^-)-B^S)$, $\lambda_{\max}(\operatorname{diag}(d^+)+B^S)$, and the Perron root of $B^Q$. Tests verify rigor and dominance over row sums.
- On the 18-case stress set, the comparison rectangle improved median parameter gap from 0.431 to 0.386, with zero violations and zero collapses.
- Introduced predict-then-certify: pixel curvatures select parameters; the comparison rectangle is evaluated once as an accept/reject certificate. This prevents a loose certificate from corrupting a good minimizer.
- In all ten regime cases the rigorous returned bound was below one. Median parameter gaps were 0.057 overall and 0.027 on smooth fields, with no collapse. Median relative certificate gap was 1.29, so tightness remains the limitation.
- A deterministic angular numerical-radius certificate with an explicit Lipschitz remainder was rigorous but looser in this study; it remains in code as a documented negative refinement.
