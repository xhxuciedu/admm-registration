# Research Agent Prompt: Search-Free ADMM Parameter Selection for Diffeomorphic Image Registration via Local Spectral Envelopes

## Role

Act as a senior researcher in numerical optimization, medical image registration, operator splitting, and scientific computing. Your task is to carry out and complete a research project titled:

**Search-Free ADMM Parameter Selection for Diffeomorphic Image Registration via Local Spectral Envelopes**

You are responsible for theory verification, implementation, experiments, statistical analysis, figure/table generation, literature review, and final manuscript completion. Work as a skeptical research collaborator: verify every theorem and numerical claim; do not preserve a proposed statement merely because it appears in the initial draft.

## Starting materials

Use the supplied LaTeX manuscript as the initial specification. Its central proposed bound is

\[
\rho(T_{\rho,\alpha})
\le
U_{\mathrm{LFA}}(\rho,\alpha)
+\frac{\alpha}{\rho}(\delta_H+\delta_G),
\]

where the local Fourier envelope is generated from frozen image-gradient Hessians and the Fourier symbol of the velocity regularizer. The proposed parameter selector evaluates a finite algebraic candidate set rather than running gradient descent over \(\rho\) or repeated ADMM trials.

Treat all unverified statements in the draft as hypotheses until independently checked.

---

## Primary research questions

1. **Exact algebra:** Is the reduced oADMM operator
   \[
   E_{\rho,\alpha}
   =\left(1-\frac{\alpha}{2}\right)I
   +\frac{\alpha}{2}C_H(\rho)C_G(\rho)
   \]
   correct for the precise scaled over-relaxation convention implemented in code?

2. **Local model:** Under frozen patch coefficients and a transform-diagonalizable componentwise regularizer, are the local eigenvalues exactly
   \[
   e(h,g;\rho,\alpha)
   =1-\frac{\alpha}{2}
   +\frac{\alpha}{2}
   \frac{h-\rho}{h+\rho}
   \frac{g-\rho}{g+\rho}?
   \]

3. **Corner reduction:** Is the local worst-case factor attained at the curvature corners for all \(0<\alpha\le2\), including cases where the affine relaxed eigenvalue crosses zero?

4. **Perturbation theorem:** Does the full noncommuting iteration satisfy
   \[
   \rho(T_{\rho,\alpha})
   \le U_{\mathrm{LFA}}(\rho,\alpha)
   +\alpha(\delta_H+\delta_G)/\rho?
   \]
   Determine whether the constant can be improved and whether a weighted norm gives a substantially tighter theorem.

5. **Search-free selection:** Does finite candidate enumeration exactly minimize the certified ADMM envelope on the specified interval? Can the oADMM selection be made jointly optimal over the certified envelope without continuous hyperparameter optimization?

6. **Practical value:** Does the selected \((\rho,\alpha)\) achieve convergence close to full spectral-radius optimization while reducing parameter-selection and total registration time?

7. **Novelty:** Is the final contribution clearly different from Ghadimi et al., Giselsson--Boyd, Teixeira et al., adaptive spectral ADMM, and Song et al. 2024?

---

## Non-negotiable scientific rules

- Never invent experimental values, citations, theorem conditions, datasets, or runtime claims.
- Keep a `research_log.md` documenting every derivation, failed attempt, implementation choice, and change to the manuscript.
- Maintain exact reproducibility: environment file, random seeds, commands, dataset versions, preprocessing, and commit hashes.
- Separate total parameter-selection time from solver time.
- Compare methods at matched objective/residual tolerances and matched registration-quality constraints.
- Report negative results, loose bounds, and failure regimes.
- Do not describe a method as “closed form” if it uses continuous gradient-based or grid-based parameter optimization.
- A finite set of algebraically generated roots is allowed, but document how roots are computed and certified.
- Do not claim the selected parameters minimize the exact full spectral radius unless proved.

---

## Phase 1: Literature review and novelty audit

Conduct a current literature search using primary sources. At minimum review:

- Boyd et al., ADMM survey.
- Ghadimi et al., optimal ADMM parameters for quadratic problems.
- Teixeira et al., parameter selection and preconditioning for distributed quadratic ADMM.
- Giselsson and Boyd, tight convergence bounds and metric selection.
- Xu, Figueiredo, and Goldstein, adaptive spectral ADMM.
- Wohlberg, residual balancing.
- Song et al. 2024, optimization of ADMM/oADMM parameters for LQPs.
- Thorley et al. 2021, Nesterov accelerated ADMM for diffeomorphic registration.
- Classical and modern local Fourier analysis, including Chan--Elman, Wienands--Joppich, and variable-coefficient LFA.
- Current optimization-based diffeomorphic registration methods and public benchmarks.

Create `related_work_matrix.csv` with columns:

- citation;
- problem class;
- parameter selected;
- exact formula vs numerical search vs adaptive update;
- assumptions;
- image-registration application;
- theoretical guarantee;
- computational overhead;
- difference from the proposed method.

Write a concise novelty statement that survives adversarial comparison with Song et al. 2024. If the novelty does not survive, revise the method before proceeding.

---

## Phase 2: Verify and strengthen the mathematics

### 2.1 Re-derive ADMM and oADMM

Starting from

\[
\min_{v,w}\frac12v^THv+b^Tv+\frac12w^TGw,
\qquad v=w,
\]

derive the exact homogeneous state matrix for standard ADMM and for the exact relaxation convention used in implementation. Verify all signs and operator orderings numerically on random symmetric positive-semidefinite matrices.

### 2.2 Reduced Cayley representation

Prove or correct the reduced operator formula using the nonzero-spectrum identity for \(AB\) and \(BA\). Test the formula numerically by comparing eigenvalues of the full state matrix and the reduced operator.

### 2.3 Registration structure

Use

\[
H_i=\mu q_iq_i^T,
\qquad q_i=\nabla I(x_i),
\]

and a componentwise Sobolev regularizer

\[
G=G_0\otimes I_d.
\]

Support:

- first-order \(H^1\) regularization;
- higher-order Sobolev regularization;
- optional zeroth-order term \(\gamma I\);
- periodic, Neumann/cosine, and Dirichlet-compatible implementations.

### 2.4 Frozen-patch spectrum

For each patch, freeze \(H_i\) to a representative \(H_r\). Derive the exact symbol and show how the rank-one structure reduces the number of distinct data curvatures. Prove the corner principle rigorously.

### 2.5 Perturbation bound

Verify the Cayley Lipschitz identity:

\[
C_A-C_B
=2\rho(A+\rho I)^{-1}(A-B)(B+\rho I)^{-1}.
\]

Then prove the full envelope bound. Investigate improvements:

- use separate denominators involving \(\lambda_{\min}(A)+\rho\);
- use energy or block-weighted norms;
- exploit exact block diagonal structure of \(H\);
- replace \(\delta_G\) by an interface-local bound;
- use overlapping patches and partition-of-unity surrogates;
- derive a posteriori bounds from Lanczos estimates;
- determine whether a Bauer--Fike, field-of-values, or pseudospectral argument improves the spectral-radius certificate.

### 2.6 Finite-candidate optimization

For standard ADMM, independently verify:

\[
\theta(h,g;\rho)
=\frac{\rho^2+hg}{(\rho+h)(\rho+g)},
\]

pairwise branch intersections, and the stationary polynomial after adding \(\delta/\rho\). Implement certified positive-root extraction. A companion-matrix solve followed by interval verification is acceptable; document numerical safeguards.

For oADMM, prove the finite candidate set for \(\alpha\) conditional on \(\rho\). Then investigate a jointly search-free selector. A valid joint method may enumerate active corner pairs and solve the resulting low-degree polynomial equations. Do not use a dense \(\rho\)-grid and call it search-free.

### 2.7 Counterexample search

Actively search for counterexamples:

- random noncommuting \(H,G\);
- rapidly rotating image-gradient orientations;
- high coefficient contrast;
- common or nearly common nullspaces;
- small \(\rho\), large \(\rho\), and \(\alpha\approx2\);
- patch boundaries aligned with strong edges.

If a theorem fails, produce the smallest numerical counterexample, correct the statement, and update the manuscript.

---

## Phase 3: Reference implementation

Create a clean repository structure:

```text
src/
  admm_registration.py
  operators.py
  local_envelope.py
  candidate_roots.py
  spectral_tools.py
  metrics.py
experiments/
  exp_constant_coeff.py
  exp_variable_coeff.py
  exp_real_subproblems.py
  exp_registration_2d.py
  exp_registration_3d.py
configs/
tests/
figures/
tables/
paper/
```

### Required tests

- finite-difference gradient and adjoint consistency;
- Hessian block construction;
- FFT/DCT regularizer solve against sparse direct solve;
- equality of full and reduced spectra on small systems;
- equality of frozen symbol and direct patch eigenspectrum;
- perturbation bound validation;
- candidate-set minimizer versus dense diagnostic grid;
- primal/dual residual and objective stopping rules;
- diffeomorphic composition and Jacobian determinant checks.

Use double precision for all theory-validation experiments. GPU mixed precision may be used only in final runtime experiments after accuracy validation.

---

## Phase 4: Experiments

### Experiment A: constant-coefficient exactness

Generate 2D and 3D periodic systems with constant image gradient. Compare:

- analytical local spectrum;
- direct full state spectrum;
- reduced Cayley spectrum;
- finite-candidate optimum;
- dense diagnostic optimum.

Expected purpose: verify exact algebra to numerical precision. Do not pre-specify favorable results.

### Experiment B: controlled variable coefficients

Create gradient fields with controlled:

- magnitude contrast;
- orientation rotation frequency;
- smooth versus discontinuous changes;
- patch size and overlap;
- regularization order and strength.

For small grids compute the true spectral radius using dense eigendecomposition. For larger grids use Arnoldi and report residuals of Ritz pairs.

Measure:

- local-envelope gap;
- certified-envelope gap;
- parameter gap to exact spectral optimization;
- iteration gap;
- relation between bound tightness and \(\delta_H,\delta_G\);
- effect of nonnormality and pseudospectral growth.

### Experiment C: real registration subproblems

Extract linearized subproblems from actual registration trajectories at multiple pyramid levels. Recommended data sources include public Learn2Reg tasks, OASIS/brain MRI, and a thoracic or cardiac dataset with clear usage terms.

For each subproblem compare:

- default \((\rho,\alpha)\);
- residual balancing;
- adaptive spectral ADMM;
- Song et al. full spectral search;
- local envelope without perturbation correction;
- certified search-free ADMM;
- certified search-free oADMM.

### Experiment D: end-to-end 2D registration

Use a small, fully reproducible 2D benchmark first. Measure total runtime and registration quality. This experiment is required before expensive 3D studies.

### Experiment E: end-to-end 3D diffeomorphic registration

Embed the method into a composed velocity-field solver consistent with Thorley et al. Match stopping criteria and outer-loop settings across parameter methods.

Report:

- Dice;
- target registration error when landmarks exist;
- Hausdorff or surface distance;
- image similarity objective;
- regularization energy;
- percentage/minimum of Jacobian determinants;
- ADMM iterations per outer step;
- parameter-selection time;
- solver time;
- total wall-clock time;
- GPU memory.

### Experiment F: robustness and ablation

Ablate:

- patch size;
- overlap;
- gradient representative;
- \(\delta_H\) only versus \(\delta_H+\delta_G\);
- regularizer boundary closure;
- zeroth-order damping;
- standard versus relaxed ADMM;
- all candidate-root classes;
- certificate-driven adaptive patch refinement.

---

## Baseline implementation requirements

### Song et al. baseline

Implement the closest possible reproduction of the numerical spectral optimization in Song et al. Use the same iteration convention as the proposed method. Record:

- number of spectral objective evaluations;
- eigensolver tolerance;
- gradient or finite-difference method;
- initialization;
- tuning runtime;
- final \(\rho,\alpha\).

### Residual balancing

Implement the exact residual scaling and update schedule from the cited source. Avoid unfairly weak default settings.

### Adaptive spectral ADMM

Implement safeguards and correlation tests described in the original method.

### Direct diagnostic optimum

For small problems, use dense spectral-radius evaluation over a high-resolution diagnostic grid followed by local scalar optimization. This is for ground truth only, not a proposed practical method.

---

## Statistical analysis

- Use paired comparisons on the same image pairs.
- Report means, medians, standard deviations, and paired bootstrap 95% confidence intervals.
- Predefine primary outcomes:
  1. total runtime to matched tolerance;
  2. parameter-selection overhead;
  3. iteration count;
  4. registration accuracy;
  5. topology preservation.
- Report failure rates and timeouts.
- Correct for multiple comparisons when testing many baselines.
- Do not treat multiple outer iterations from the same image pair as independent biological samples.

---

## Decision gates

### Gate 1: theorem validity
Proceed only if the reduced operator, corner principle, and perturbation bound pass analytic and numerical checks.

### Gate 2: envelope usefulness
Proceed to full registration only if the certified or uncorrected local envelope selects parameters with a median spectral-radius gap below a predeclared threshold on controlled variable-coefficient tests. Choose and justify the threshold before examining real-data results.

### Gate 3: practical value
The project is publishable only if the method meaningfully reduces total tuning plus solve time without degrading registration accuracy or topology. Fewer iterations without lower total runtime is insufficient.

### Gate 4: novelty
Before submission, write a point-by-point comparison with Song et al. showing that the proposed method:

- uses no iterative \(\rho\)-optimization;
- derives a registration-specific local symbol;
- provides an explicit noncommuting perturbation certificate;
- selects parameters from a finite algebraic set;
- demonstrates lower total selection overhead.

---

## Manuscript completion instructions

Update the supplied LaTeX paper rather than creating a disconnected manuscript. The final paper must include:

1. Title and abstract reflecting actual results.
2. Introduction with a narrow, defensible novelty claim.
3. Related work with a direct Song et al. comparison table.
4. Exact problem formulation and algorithm convention.
5. Theorems with complete assumptions.
6. Full proofs in appendices.
7. Reproducible algorithm pseudocode.
8. Results with no placeholders.
9. Bound-tightness and failure-case analysis.
10. Discussion that distinguishes exact spectral optimality from certified-envelope optimality.
11. Data/code availability statements.
12. Complete primary-source references.

Replace every placeholder table and figure. Every plotted curve must be generated from a committed script and configuration. Every reported number must be traceable to a machine-readable result file.

---

## Final deliverables

Produce:

- completed `paper.tex` and compiled `paper.pdf`;
- source code and tests;
- environment specification;
- experiment configurations;
- raw and summarized results;
- figures in vector PDF/SVG where possible;
- `research_log.md`;
- `related_work_matrix.csv`;
- a concise README with exact reproduction commands;
- a final internal review memo covering novelty, limitations, likely reviewer objections, and recommended venue.

Do not declare the project complete until all decision gates are satisfied or until you provide a transparent negative-result report explaining why they could not be satisfied.
