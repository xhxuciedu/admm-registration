# Executive summary

## Does the method work?

Yes in the tested constant, synthetic, controlled-real, and CIMA histology
regimes. The rank-one predictor is exactly a four-corner finite calculation and
matched pixelwise enumeration in 10,000/10,000 randomized configurations.

On the public CIMA differently stained lung-lesion sample (five images, ten
landmark pairs), a single full-resolution predictor call reduced median ADMM
iterations by 30.1%, solver time by 23.5%, and total runtime by 20.1% versus the
strongest externally validated fixed pair. The paired bootstrap 95% interval
for total-runtime reduction was 19.4%--20.7% over five repetitions and 50 paired
runs. Tuning used 1.16% of runtime. Median TRE was unchanged at 7.33 pixels
(2.02% of the diagonal), median landmark improvement was 36.5%, and no final
deformation folded.

On all 134 public FIRE retinal landmark pairs at 128x128, the predictor reduced
median ADMM iterations by 40.7% and paired total runtime by 33.6% (bootstrap
95% CI 32.5%--34.7%) versus the external fixed pair $(0.1,1)$. Median TRE was
unchanged (2.85282 versus 2.85284 pixels), tuning used 2.0% of proposed runtime,
and no final field folded or failed to converge.

## How close is it to spectral optimization?

Smooth synthetic cases have a 2.7% median spectral-radius gap; the broader ten-
case median is 5.7%. On exact 8x8 variable-coefficient CIMA surrogates, numerical
spectral optimization required a median 97 objective evaluations and 2.18 s of
tuning. Transferred to the full solve, it used 251 median iterations versus 210
for the predictor and took 4.39 s versus 2.02 s, with the same TRE. This is a
coarse-surrogate Song-style diagnostic, not full-resolution Song optimization.

## Where does it fail?

- One difficult CIMA stain pair retains TRE above 22 pixels; global
  initialization and cross-stain representation dominate that failure.
- The BB comparator is a safeguarded proxy, not a complete published AADMM
  reproduction.
- FIRE uses a 128x128 CPU protocol and one external fixed comparator; it does
  not yet reproduce every adaptive published baseline or clinical-scale run.
- CIMA contains one reduced-resolution tissue set, so dataset-level medical
  generalization is not established.

## Is certification worthwhile?

Not in the current implementation. Twenty tests through 64x64 had no enclosure
violations, but relative bound gaps were 1.38--1.54 and the slowest 64x64 case
took 81.4 seconds. A 128x128 attempt did not finish in its diagnostic window.
Certification remains a small-problem diagnostic; the predictor is the
practical contribution.

## Publication decision

The work is now a **go for a numerical-methods preprint or workshop paper**:
there is an exact theorem, robust implementation, established landmark sample,
matched-accuracy speedup, repeated timing, and preserved failure analysis.

It remains a **no-go for a broad clinical-registration performance claim** until
clinical-scale resolution, multiple tissue sets, and a complete published
adaptive-spectral baseline are reproduced. A strong eventual target is *SIAM
Journal on Imaging Sciences*; *Medical Image Analysis* should wait for the
broader benchmark phase.
