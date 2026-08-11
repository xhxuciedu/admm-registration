```markdown
# Task: Major Reorganization and Revision of the JMIV Manuscript

You are working in the existing git repository containing the LaTeX source, figures, supplementary material, code references, and experimental results for the manuscript currently titled approximately:

> "Four-Corner Spectral Tuning for Search-Free ADMM in Diffeomorphic Image Registration"

The manuscript currently contains the right core mathematical ideas and useful experimental results, but its conceptual organization is too complicated. The central contribution — **four-corner spectral tuning** — should become the clear mathematical centerpiece of the paper.

Your task is to substantially reorganize and rewrite the manuscript while preserving all valid results, experiments, citations, and mathematical content.

Do NOT fabricate new experiments, numerical values, citations, theorems, or claims.

Do NOT silently strengthen any theorem beyond what can actually be proved.

If an additional experiment is recommended but has not yet been run, clearly mark it as a proposed/TODO experiment rather than inventing results.

---

# 1. Central New Story of the Paper

Reframe the manuscript around the following conceptual progression:

\[
\text{quadratic ADMM}
\rightarrow
\text{modal error factor}
\rightarrow
\text{four-corner spectral reduction}
\rightarrow
\text{finite algebraic parameter selection}
\rightarrow
\text{extension to noncommuting spatially varying problems}
\rightarrow
\text{diffeomorphic image registration}.
\]

The paper should first introduce **four-corner spectral tuning as a general mathematical method for an appropriate class of quadratic ADMM problems**, and only afterward specialize it to image registration.

Image registration should become the primary application and motivating noncommuting case, not the framework in which every theoretical result is initially introduced.

---

# 2. Critical Mathematical Qualification

This point is essential and must be handled rigorously.

Do **NOT** claim:

> "If H and G commute, four-corner tuning is exact."

Commutativity alone is not sufficient for exact four-corner characterization of the true modal spectrum.

If

\[
HG=GH,
\]

then there exists a common eigenbasis

\[
Hx_i=h_i x_i,\qquad
Gx_i=g_i x_i,
\]

but the actual joint modal spectrum is

\[
\{(h_i,g_i)\}_i,
\]

which need not equal the Cartesian product

\[
\operatorname{spec}(H)\times\operatorname{spec}(G).
\]

For example, the endpoint combination \((h_-,g_-)\) may not correspond to any actual common eigenvector.

Therefore distinguish carefully between:

### General simultaneously diagonalizable / commuting case

The scalar modal formula is valid on the actual paired joint spectrum

\[
\{(h_i,g_i)\}.
\]

A rectangular four-corner construction can provide an envelope, but the four artificial endpoint pairs are not necessarily actual modes.

### Separable / Cartesian-product modal case

The exact four-corner result holds when the modal structure factors such that the relevant modes independently combine

\[
h\in\mathcal H,\qquad g\in\mathcal G,
\]

for example through tensor-product operators such as

\[
H_{\rm sep}=I_m\otimes H_c,
\qquad
G_{\rm sep}=G_s\otimes I_d.
\]

Then eigenvectors have the form

\[
\phi_\xi\otimes z_j,
\]

with

\[
H_c z_j=h_j z_j,\qquad
G_s\phi_\xi=g(\xi)\phi_\xi,
\]

and every pair

\[
(h_j,g(\xi))
\]

is a legitimate mode.

This is the precise setting in which the four-corner theorem should be presented as exact.

Use a terminology such as one of the following, choosing the clearest:

- separable quadratic ADMM,
- separable commuting quadratic split,
- tensor-product quadratic split,
- quadratic ADMM with Cartesian-product joint spectrum.

Define the term formally before using it.

---

# 3. Generic Quadratic ADMM Formulation

Move the generic quadratic ADMM theory before image registration.

Start from

\[
\min_{v,w}
\frac12 v^\top Hv+b^\top v
+
\frac12 w^\top Gw,
\qquad
v-w=0,
\]

with

\[
H,G\succeq0.
\]

Present standard scaled ADMM:

\[
(H+\rho I)v^{k+1}
=
-b+\rho(w^k-u^k),
\]

\[
(G+\rho I)w^{k+1}
=
\rho(v^{k+1}+u^k),
\]

\[
u^{k+1}
=
u^k+v^{k+1}-w^{k+1}.
\]

For over-relaxed ADMM, define

\[
\widehat v^{k+1}
=
\alpha v^{k+1}+(1-\alpha)w^k,
\qquad
0<\alpha\le2,
\]

and use \(\widehat v^{k+1}\) in the \(w\) and dual updates.

Explicitly define:

> oADMM = over-relaxed ADMM.

Do not leave this acronym ambiguous.

State clearly that \(b\) affects the fixed point but not homogeneous error propagation.

---

# 4. Reduced Cayley Representation

Introduce the Cayley transforms

\[
C_H(\rho)
=
(H-\rho I)(H+\rho I)^{-1},
\]

\[
C_G(\rho)
=
(G-\rho I)(G+\rho I)^{-1}.
\]

Derive the reduced error operator

\[
E_{\rho,\alpha}
=
\left(1-\frac{\alpha}{2}\right)I
+
\frac{\alpha}{2}C_H(\rho)C_G(\rho).
\]

Preserve the existing derivation and proof, but present it as supporting machinery rather than the headline contribution.

Do not oversell this result as the principal novelty.

The principal novelty should be the four-corner reduction and finite algebraic tuning.

---

# 5. Scalar Modal Factor

For a separable commuting modal pair \((h,g)\), derive

\[
e(h,g;\rho,\alpha)
=
1-\frac{\alpha}{2}
+
\frac{\alpha}{2}
\frac{h-\rho}{h+\rho}
\frac{g-\rho}{g+\rho}.
\]

Equivalently define

\[
\theta(h,g;\rho)
=
\frac{\rho^2+hg}
{(\rho+h)(\rho+g)}
\]

so that

\[
e(h,g;\rho,\alpha)
=
1-\alpha+\alpha\theta(h,g;\rho).
\]

Explain this formula carefully.

This is the core object around which the rest of the theory is organized.

---

# 6. Four-Corner Principle

Make this the main theorem of the theoretical section.

For fixed \(\rho>0\),

\[
\frac{\partial\theta}{\partial h}
=
\frac{\rho(g-\rho)}
{(g+\rho)(h+\rho)^2},
\]

\[
\frac{\partial\theta}{\partial g}
=
\frac{\rho(h-\rho)}
{(h+\rho)(g+\rho)^2}.
\]

Emphasize the key observation:

- the sign of \(\partial\theta/\partial h\) does not depend on \(h\);
- the sign of \(\partial\theta/\partial g\) does not depend on \(g\).

Thus \(\theta\) is coordinatewise monotone on a rectangle

\[
[h_-,h_+]\times[g_-,g_+].
\]

Because

\[
|1-\alpha+\alpha\theta|
\]

is convex as a function of \(\theta\), its maximum over the rectangle is attained at one of the four corners:

\[
(h_-,g_-),\qquad
(h_-,g_+),\qquad
(h_+,g_-),\qquad
(h_+,g_+).
\]

State a theorem of the form:

> **Four-Corner Spectral Theorem.**
> For a separable quadratic ADMM problem whose modal spectrum is the Cartesian product of data curvatures and regularizer modes contained in the specified intervals, the worst-case oADMM contraction factor equals
>
> \[
> U_{4C}(\rho,\alpha)
> =
> \max_{(h,g)\in
> \{h_-,h_+\}\times\{g_-,g_+\}}
> |e(h,g;\rho,\alpha)|.
> \]

Be explicit about whether endpoint combinations must be attained for equality with the true spectral radius.

If only an interval enclosure is available, state the result as an upper envelope rather than an equality.

---

# 7. Distinguish Three Cases Explicitly

Add a short subsection or boxed explanation distinguishing:

### Case A: Exact separable commuting problem

\[
\rho(E_{\rho,\alpha})
=
U_{4C}(\rho,\alpha).
\]

Four-corner tuning produces the true optimal parameters for the model.

### Case B: Arbitrary commuting problem

A common eigenbasis exists, but the joint eigenvalue pairs need not form a Cartesian product.

Four corners characterize a rectangular envelope, not necessarily the exact joint spectral radius.

### Case C: Noncommuting variable-coefficient problem

The scalar modal decomposition itself is no longer globally valid.

Four-corner tuning becomes a surrogate/predictor unless additional arguments are supplied.

This distinction must appear early enough that readers cannot confuse:

> "four-corner optimization is exact"

with

> "the parameters are globally optimal for the full image-registration operator."

---

# 8. Search-Free Joint Parameter Selection

After establishing the four-corner objective,

\[
U_{4C}(\rho,\alpha)
=
\max_c |1-\alpha+\alpha\theta_c(\rho)|,
\]

derive the optimal conditional relaxation.

Define

\[
a(\rho)=\min_c\theta_c(\rho),
\qquad
b(\rho)=\max_c\theta_c(\rho).
\]

Then

\[
U_{4C}
=
\max\{
|1-\alpha+\alpha a|,
|1-\alpha+\alpha b|
\}.
\]

Derive

\[
\alpha^\star(\rho)
=
\min\left\{
2,
\frac{2}{2-a(\rho)-b(\rho)}
\right\}
\]

when applicable.

Explain the equioscillation interpretation.

Then present the finite algebraic selection of \(\rho\):

- interval endpoints,
- pairwise branch intersections,
- \(a+b=1\) transition roots,
- stationary roots of active rational objectives.

Preserve the valid degree bounds already proved in the manuscript.

The final message should be:

\[
\boxed{
\text{no grid search}
+
\text{no gradient descent in }\rho
+
\text{no repeated spectral-radius calculation}
}
\]

because the optimization has been reduced to a constant number of rational branches and a finite algebraic candidate set.

---

# 9. Comparison to Song et al.

Make the distinction with Song et al. much more transparent.

Song et al. solve a more general linear-quadratic problem.

Their approach:

\[
\rho
\rightarrow
E_\rho
\rightarrow
\varrho(E_\rho)
\rightarrow
\text{numerical optimization over }\rho,
\]

with an optimal/closed-form conditional relaxation parameter.

The computational burden is not that \(\rho\) changes during ADMM.

Within one quadratic subproblem, optimal \(\rho\) and \(\alpha\) are fixed.

The expense arises from **finding** the optimal \(\rho\):

\[
\text{many trial }\rho
\times
\text{spectral-radius evaluation of a large operator}.
\]

Explain this carefully in the Introduction and Related Work.

Then contrast the proposed method:

\[
(h_-,h_+,g_-,g_+)
\rightarrow
4\text{ rational branches}
\rightarrow
\text{finite algebraic candidates}
\rightarrow
(\rho_p,\alpha_p).
\]

Avoid claiming superiority to full-resolution Song optimization unless an experiment directly establishes it.

Retain the current manuscript's careful statement that the existing \(8\times8\) Song-style diagnostic measures tuning overhead/model transfer rather than proving superiority over full-resolution Song optimization.

---

# 10. Image Registration as the Main Application

Only after the general theory is complete, introduce the image-registration model.

Use notation consistently:

\[
q_i=\nabla I(x_i),
\]

\[
H_i
=
\nu I_d+\mu q_iq_i^\top,
\]

\[
H=\operatorname{diag}(H_1,\ldots,H_n).
\]

Make sure \(\nu\) is either present consistently from the original registration objective onward or clearly introduced as optional damping.

Do not claim it was "already in the objective" if the displayed earlier objective does not contain it.

For the regularizer use

\[
G=G_0\otimes I_d.
\]

Use \(\Delta x\), NOT \(h\), for grid spacing, because \(h\) is also used for Hessian/data curvature.

For first-order Sobolev regularization write

\[
g(\xi)
=
\gamma+
\frac{4\beta}{(\Delta x)^2}
\sum_{\ell=1}^{d}
\sin^2\left(\frac{\xi_\ell}{2}\right).
\]

Avoid using \(g\) simultaneously as both:
- the regularization objective \(g(w)\), and
- the scalar Fourier symbol \(g(\xi)\).

Rename the objective components, e.g.

\[
f(v)+r(w).
\]

---

# 11. Explain Clearly Why Full Registration Is Noncommuting

Make this one of the key conceptual points.

Because

\[
H=\operatorname{diag}(H_i)
\]

varies spatially while

\[
G=G_0\otimes I_d
\]

couples neighboring pixels,

\[
HG\neq GH
\]

in general.

Therefore a global common Fourier/eigenbasis is unavailable.

Consequently, the exact true convergence factor is

\[
R_{\rm true}(\rho,\alpha)
=
\varrho(E_{\rho,\alpha}),
\]

whereas the four-corner objective is a surrogate/predictor

\[
R_{4C}(\rho,\alpha).
\]

State clearly:

\[
(\rho_{4C},\alpha_{4C})
=
\arg\min R_{4C}
\]

is exactly optimal for the four-corner model,

but generally

\[
(\rho_{4C},\alpha_{4C})
\neq
\arg\min R_{\rm true}.
\]

Do not call the practical parameters "globally optimal for registration."

Use language such as:

- predictor,
- search-free parameter predictor,
- surrogate-optimal parameters,
- exact constant/separable-model optimum.

---

# 12. Recast Patches as Local Commuting Approximations

The role of patches should become much clearer.

The current manuscript introduces patches before the reader fully understands why they are needed.

Instead explain:

> The full image-registration problem is noncommuting because the local image Hessian changes spatially. We therefore locally freeze the image-gradient Hessian to recover the separable commuting structure required by the general four-corner theory.

For patch \(\Omega_r\), define

\[
H_r
=
\nu I_d+\mu\bar q_r\bar q_r^\top,
\]

and

\[
\widetilde H_r
=
I_{|\Omega_r|}\otimes H_r,
\]

\[
\widetilde G_r
=
G_r\otimes I_d.
\]

Then

\[
\widetilde H_r\widetilde G_r
=
\widetilde G_r\widetilde H_r.
\]

The joint eigenvectors are

\[
\phi_\xi\otimes z_j,
\]

giving the exact local modal factors

\[
e_{r,j}(\xi;\rho,\alpha).
\]

Now explain how one global \((\rho,\alpha)\) is obtained from many patches:

\[
U_{\rm patch}(\rho,\alpha)
=
\max_{r,j,\xi}
|e_{r,j}(\xi;\rho,\alpha)|.
\]

The same global \(\rho\) and \(\alpha\) are used everywhere.

Do NOT imply that each patch receives its own ADMM penalty.

Apply the corner principle patchwise:

\[
\mathcal C
=
\bigcup_{r,j}
\{
(h_{r,j},g_r^-),
(h_{r,j},g_r^+)
\},
\]

so

\[
U_{\rm patch}
=
\max_{(h,g)\in\mathcal C}
|e(h,g;\rho,\alpha)|.
\]

This gives a global minimax parameter choice across all local models.

---

# 13. Then Show the Stronger Rank-One Registration Collapse

After presenting patchwise local freezing, exploit the special registration Hessian.

For

\[
H_r=\nu I_d+\mu\bar q_r\bar q_r^\top,
\]

the eigenvalues are

\[
\nu
\]

with multiplicity \(d-1\), and

\[
\nu+\mu\|\bar q_r\|^2.
\]

Globally,

\[
h_-=\nu,
\]

\[
h_+
=
\nu+\mu\max_i\|q_i\|^2.
\]

Together with

\[
g_-=\lambda_{\min}(G_0),
\qquad
g_+=\lambda_{\max}(G_0),
\]

the practical registration predictor reduces to exactly four scalar branches:

\[
(h_-,g_-),
\quad
(h_-,g_+),
\quad
(h_+,g_-),
\quad
(h_+,g_+).
\]

Present this as a registration-specific corollary of the general four-corner framework.

This should be one of the strongest results in the paper.

---

# 14. Clarify Exact vs Predictive Language

Audit the ENTIRE manuscript for the following words:

- exact,
- optimal,
- global,
- guaranteed,
- spectral,
- predictor,
- surrogate.

Use them precisely.

Recommended terminology:

### Exact

Use only for:
- reduced operator identities,
- modal formulas under the stated separable assumptions,
- four-corner reduction of the appropriate model/envelope,
- finite optimization of the four-corner objective.

### Optimal

Distinguish:

\[
\text{optimal for the four-corner/separable surrogate}
\]

from

\[
\text{optimal for the actual variable-coefficient registration operator}.
\]

Do not conflate them.

### Predictor

Use this for the practical full-registration parameter pair.

A sentence that should appear prominently is:

> The four-corner reduction is exact for the separable commuting surrogate; the resulting parameter pair is therefore globally optimal for that surrogate, but serves as a predictor of the optimal parameters for the full variable-coefficient registration iteration.

---

# 15. Simplify the Certification Material

The current manuscript spends too much main-text space on:

- additive perturbation bounds,
- block-Gershgorin disks,
- signed rectangles,
- Perron comparison,
- truncated convolution certificates,
- certificate scaling diagnostics.

These results are mathematically interesting but are NOT used by the deployed tuning method and are empirically conservative.

Move most of this machinery to Supplementary Information.

In the main manuscript retain only a concise section such as:

## Optional Variable-Coefficient Rate Bounds

Explain:

1. four-corner tuning produces the practical parameters;
2. rigorous noncommuting bounds can optionally validate them;
3. these bounds are conservative;
4. they are not used during deployed parameter selection.

Retain perhaps one main theorem giving the essence of the rigorous extension.

Move detailed proofs and the block-Gershgorin/Perron/truncated-kernel hierarchy to the supplement.

Do not allow the certificate story to compete with the main four-corner story.

---

# 16. Replace the Current Algorithms with a Clear Main Algorithm

The current practical algorithm should be unmistakable.

Create a main algorithm such as:

## Algorithm 1: One-Shot Four-Corner ADMM Tuning

Inputs:
- image/data curvature information,
- \(\mu,\nu\),
- regularizer parameters,
- admissible penalty interval.

Steps:

1. Compute

\[
h_-=\nu,
\qquad
h_+=\nu+\mu\max_i\|q_i\|^2.
\]

2. Compute analytically

\[
g_-,
\qquad
g_+.
\]

3. Form the four corners.

4. Construct the four rational functions

\[
\theta_c(\rho).
\]

5. Generate the finite algebraic candidate set for \(\rho\).

6. For each candidate compute

\[
a(\rho),\quad b(\rho),\quad\alpha^\star(\rho).
\]

7. Select the pair minimizing the four-corner envelope.

8. Run oADMM with this fixed pair.

9. In the deployed one-shot registration policy, reuse the pair through subsequent outer iterations/pyramid levels unless an alternative retuning policy is explicitly enabled.

Make this the algorithm readers remember.

Move any "legacy certified-envelope minimization" algorithm to the supplement or describe it explicitly as a diagnostic baseline.

---

# 17. Explain Inner vs Outer Iterations

The paper should explicitly distinguish:

### Inner ADMM iterations

Within a single quadratic subproblem:

\[
H,G,b
\]

are fixed.

Therefore the true optimal

\[
\rho^\star,\alpha^\star
\]

for that subproblem are fixed constants.

They do not need to change during inner ADMM iterations.

### Outer registration iterations

After updating the deformation and relinearizing,

\[
H^{(m)}
\]

may change because the warped image gradients change.

Therefore the theoretically optimal pair for the next subproblem may also change.

The deployed algorithm nevertheless uses one-shot reuse for computational efficiency.

Preserve the existing empirical ablation showing that per-level retuning reduces iterations but increases total runtime.

Be precise that the current manuscript tested per-level retuning; do not claim that per-outer-Gauss–Newton-iteration retuning was separately tested unless such data actually exist.

---

# 18. Reorganize the Experiments

Recommended experiment order:

## Experiment 1: Exact separable/commuting verification

Verify the reduced modal spectrum and four-corner equality to machine precision.

Use current constant-coefficient tests.

This validates the theorem.

## Experiment 2: Controlled departure from the assumptions

Use controlled variable-coefficient problems.

Quantify:
- degree of noncommutativity,
- gap between four-corner predicted convergence and exact spectral radius,
- parameter gap,
- smooth versus abrupt coefficient variation.

If existing experiments already provide this, reorganize them accordingly.

Do not invent new results.

## Experiment 3: Comparison with direct spectral optimization

Use existing Song-style diagnostics.

Clearly distinguish:
- oracle/direct spectral optimization,
- four-corner tuning,
- tuning overhead,
- resulting iteration count,
- resulting total time.

Add a TODO/recommended experiment, if not already available:

> On a tractable subset/resolution, compare four-corner parameters to an expensive direct spectral oracle and report spectral-radius regret:
>
> \[
> \frac{
> R_{\rm true}(\rho_{4C},\alpha_{4C})
> -
> R_{\rm true}(\rho^\star,\alpha^\star)
> }{
> R_{\rm true}(\rho^\star,\alpha^\star)
> }.
> \]

Do NOT fabricate this experiment.

## Experiment 4: End-to-end CIMA

Preserve all existing values and matched-protocol claims.

## Experiment 5: End-to-end FIRE

Preserve:
- 134 pairs,
- iteration reductions,
- runtime reductions,
- TRE,
- Jacobian/topology results,
- BB comparison.

## Experiment 6: One-shot reuse ablation

Keep the current per-level tuning comparison.

Explain the tradeoff:

\[
\text{fewer iterations}
\not\Rightarrow
\text{lower total runtime}
\]

because tuning itself has a cost.

---

# 19. Figures

Improve figure placement and clarity.

### Figure 1

Create or revise a conceptual/theoretical figure that communicates:

1. exact four-corner equality under the separable model;
2. increasing deviation under variable coefficients/noncommutativity;
3. optional conservative certificate.

Make axis labels larger and visually clear.

### FIRE figure

Move the FIRE benchmark figure near the FIRE results, not after the Conclusion.

Retain panels showing:
- runtime reduction,
- iteration reduction,
- TRE agreement,
- image-dependent predicted \(\rho\).

Make panel labels (a), (b), (c), (d) prominent.

### Tables

Place CIMA and FIRE tables close to their corresponding Results subsections.

Avoid large floating gaps.

---

# 20. Suggested New Paper Structure

Use approximately the following structure:

## 1. Introduction
- ADMM parameter tuning problem
- direct spectral optimization and its cost
- key observation: four spectral corners
- contribution summary
- image registration as noncommuting application

## 2. Related Work
### 2.1 ADMM parameter selection
### 2.2 Spectral and over-relaxed ADMM
### 2.3 Fourier/local Fourier analysis
### 2.4 Variational image registration

## 3. Quadratic ADMM and Reduced Error Dynamics
### 3.1 Quadratic splitting
### 3.2 Standard and over-relaxed ADMM
### 3.3 Reduced Cayley representation
### 3.4 Scalar modal factor

## 4. Four-Corner Spectral Tuning
### 4.1 Separable commuting modal structure
### 4.2 Four-corner theorem
### 4.3 Optimal relaxation for fixed penalty
### 4.4 Finite algebraic penalty selection
### 4.5 General commuting case versus Cartesian-product spectrum

## 5. Spatially Varying and Noncommuting Problems
### 5.1 Why global modal analysis fails
### 5.2 Local freezing / patchwise commuting approximation
### 5.3 Global minimax over local modes
### 5.4 Optional rate bounds
Keep this short in the main text.

## 6. Application to Diffeomorphic Image Registration
### 6.1 Linearized registration model
### 6.2 Rank-one data Hessian
### 6.3 Sobolev regularizer and symbol
### 6.4 Global four-corner registration predictor
### 6.5 One-shot deployment policy

## 7. Experimental Protocol

## 8. Results
### 8.1 Exact four-corner validation
### 8.2 Controlled noncommuting tests
### 8.3 Direct spectral optimization comparison
### 8.4 CIMA
### 8.5 FIRE
### 8.6 One-shot reuse ablation

## 9. Discussion
### 9.1 Why four corners work
### 9.2 Exact model optimum versus full-problem prediction
### 9.3 Comparison with Song et al.
### 9.4 Limitations

## 10. Conclusion

Appendices/Supplement:
- detailed perturbation certificate theory,
- Gershgorin/Perron comparison,
- truncated-kernel results,
- lengthy proofs,
- implementation details,
- seeds/software/hardware,
- additional plots/tables.

---

# 21. Rewrite the Introduction Around One Main Insight

The Introduction should become substantially simpler.

A possible logical flow:

Paragraph 1:
ADMM is attractive for large quadratic imaging problems because the split subproblems can exploit specialized structure, but convergence is sensitive to \(\rho\) and \(\alpha\).

Paragraph 2:
Existing optimal spectral methods such as Song et al. address general LQPs but require numerical optimization of the iteration spectrum.

Paragraph 3:
For an important separable class of quadratic splits, the oADMM modal contraction depends only on two scalar curvatures \(h\) and \(g\). The dependence is coordinatewise monotone, so the worst contraction over the modal rectangle occurs at four corners.

Paragraph 4:
This converts a potentially large spectral optimization into four rational scalar branches and a finite algebraic parameter-selection problem.

Paragraph 5:
Real image registration is not globally separable because the image Hessian varies spatially. We handle this using local freezing and exploit the rank-one optical-flow structure to obtain an extremely inexpensive global predictor.

Paragraph 6:
Summarize empirical results.

Then give 3–4 concise contributions.

Suggested contribution list:

1. A four-corner spectral theorem for separable quadratic ADMM/oADMM, reducing worst-case modal contraction to four endpoint pairs.
2. A finite algebraic search-free method for jointly selecting penalty and relaxation parameters.
3. A local-freezing extension to spatially varying noncommuting problems and a rank-one specialization for diffeomorphic registration.
4. FIRE/CIMA validation showing substantial runtime and iteration reductions at matched registration accuracy/topology.

---

# 22. Possible New Title

Consider changing the title to emphasize the general method.

Preferred candidate:

> **Four-Corner Spectral Tuning for Quadratic ADMM with Application to Diffeomorphic Image Registration**

Alternative:

> **Search-Free Four-Corner Spectral Tuning for Quadratic ADMM and Diffeomorphic Image Registration**

Alternative:

> **Four-Corner Spectral Parameter Selection for ADMM: Theory and Application to Diffeomorphic Image Registration**

Choose the title that best matches the final mathematical scope.

Do not claim generality beyond the actual assumptions.

---

# 23. Abstract Rewrite

Rewrite the abstract around:

1. expensive spectral parameter selection in quadratic ADMM;
2. separable modal structure;
3. four-corner theorem;
4. finite algebraic joint selection of \(\rho,\alpha\);
5. noncommuting image registration handled by local freezing/rank-one structure;
6. existing FIRE and CIMA results;
7. optional certificates are secondary.

Avoid spending much abstract space on the certificate machinery.

Avoid saying the four-corner parameters are globally optimal for the full variable-coefficient registration operator.

---

# 24. Discussion and Limitations

Strengthen the Discussion around the exact distinction:

\[
\text{exact surrogate optimization}
\neq
\text{exact full variable-coefficient optimization}.
\]

Explicitly acknowledge:

- full registration generally has \(HG\neq GH\);
- four-corner parameters are not guaranteed to minimize the true spectral radius;
- local freezing is an approximation;
- rank-one endpoint reduction ignores orientation interactions;
- rigorous certificates are conservative;
- CIMA is limited in size;
- FIRE is evaluated at 256×256;
- the paper concerns the linearized convex subproblem, not global convergence of the outer nonlinear registration algorithm.

Present these as clear scope boundaries, not apologetic caveats.

---

# 25. Writing Style

Rewrite for a professional mathematical/numerical-analysis audience.

Avoid:
- meta-writing,
- defensive prose,
- statements like "for completeness we retain...",
- repeated reminders that something is not claimed,
- LLM-like transitions,
- unnecessary repetition.

Prefer direct scientific statements.

Use consistent terminology throughout.

The paper should feel like one coherent argument, not several research threads combined.

---

# 26. Preserve Existing Valid Results

Do NOT alter numerical results unless the source files demonstrate that a correction is needed.

Preserve existing findings including approximately:

- FIRE: 134 landmarked pairs;
- four-corner one-shot substantially reduces inner iterations and total runtime relative to the frozen external fixed baseline;
- essentially unchanged TRE;
- no observed nonpositive Jacobian in the reported protocol;
- CIMA runtime and iteration reductions;
- tuning overhead near ~1% in deployed experiments;
- per-level retuning decreases iterations but increases total runtime;
- Song-style 8×8 diagnostic requires many spectral objective evaluations and is explicitly not a full-resolution Song comparison;
- rigorous certificates are valid but conservative.

Verify all exact numbers from the manuscript source before writing them.

---

# 27. LaTeX / Repository Work

Perform the changes directly in the manuscript source.

Tasks:

1. Inspect the repository structure.
2. Identify the main manuscript `.tex` file.
3. Identify supplementary source.
4. Identify bibliography.
5. Identify figure-generation scripts and figure assets.
6. Reorganize sections according to the revised outline.
7. Move appropriate theorem/proof/certificate material to supplementary files.
8. Update theorem numbering, equation references, figure references, and cross-references.
9. Fix notation conflicts.
10. Rebuild the PDF.
11. Resolve all LaTeX warnings that can reasonably be fixed:
   - undefined references,
   - duplicate labels,
   - broken citations,
   - overfull equations where practical,
   - misplaced floats.
12. Do NOT remove valid bibliography entries merely because sections moved.
13. Preserve code/data availability information.

---

# 28. Validation Before Finishing

Before declaring completion, systematically check:

### Mathematical consistency
- Is commutativity alone ever incorrectly claimed sufficient?
- Is Cartesian-product/separable modal structure stated where needed?
- Are exact and predictive results clearly distinguished?
- Are the \(\rho,\alpha\) optimization claims correct?
- Are inner versus outer registration iterations distinguished?

### Notation
- no conflict between grid spacing and curvature \(h\);
- no conflict between objective \(g(w)\) and Fourier symbol \(g(\xi)\);
- \(\nu\) consistently appears wherever required;
- \(G_0\otimes I_d\) uses stacking convention consistently.

### Narrative
A reader should be able to summarize the paper as:

> Four-corner tuning exactly solves the minimax spectral parameter problem for a separable quadratic ADMM model. Local freezing makes this structure available patchwise in image registration, while the rank-one optical-flow Hessian yields a very inexpensive global predictor that avoids direct spectral optimization.

### Empirical claims
Every reported numerical value must be traceable to an existing source/result file.

---

# 29. Output at Completion

When finished, provide:

1. a concise summary of the major structural changes;
2. the revised title;
3. the new section outline;
4. a list of theorem changes, including any assumptions strengthened or clarified;
5. a list of material moved to supplementary information;
6. notation fixes;
7. any experiments that remain TODO;
8. the path to the rebuilt PDF;
9. `git diff --stat`;
10. a short list of the most important remaining scientific risks.

Do not merely edit wording. This is a **substantive reorganization of the mathematical narrative** around four-corner spectral tuning.
```

One addition I would strongly consider before giving this to Codex is asking it to create a separate branch such as `four-corner-reorg`, so the current JMIV version remains intact while the new conceptual structure is developed.
