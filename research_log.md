# Research log

This file records both successful and failed work. Dates use America/Los_Angeles.

## 2026-08-06: audit and reproduction

- Started branch `real-registration-validation` at commit
  `3dc78db3013b9ab2eed80f00b04d4455bc809a55`.
- Reproduced the existing test suite and inspected all existing raw result files.
- Confirmed that the prior manuscript contained no real-registration experiment;
  its numerical claims remain explicitly synthetic.

## 2026-08-06: four-corner reduction

- Proved that rank-one registration requires only the rectangle
  `{nu, nu + mu max_i |q_i|^2} x {g_min, g_max}` for the global predictor.
- Compared the four-branch and pixel-curvature finite selectors on 10,000
  randomized configurations, including nullspaces and first/second-order
  symbols: 10,000 exact parameter matches and zero failures.
- The four-branch selector took about 31--35 ms from 64 to 1,048,576 pixels.
  The legacy selector took 34, 144, 785, and 5,404 ms for 2, 4, 8, and 16
  distinct curvature branches, respectively. A 32-branch timing attempt was
  stopped after it exceeded the useful benchmark budget; no result is reported.

## 2026-08-06: oracle and registration implementation

- Added independent dense and matrix-free reduced operators and conditional
  relaxation minimization. Dense/matrix-free equivalence is covered by tests.
- Added a CPU multiresolution 2D registration reference pipeline with FFT ADMM,
  over-relaxation, composition, and a positive-Jacobian line-search safeguard.
- A first public-sample experiment was deliberately discarded before results
  were saved: its manual baseline was hard-coded rather than validation-selected,
  and its reported displacement error used `-u` as an approximate inverse.
  The corrected protocol uses validation cases 1--2, held-out cases 3--5, and a
  fixed-point inverse field for inverse-consistent known-warp construction.
- The current `adaptive_bb_proxy` is a safeguarded BB penalty heuristic. It is
  not the full Xu et al. adaptive spectral ADMM and must not be labelled as such.
- A first attempt at five-repeat registration timing overlapped with the 128^2
  Arnoldi certificate process. It was interrupted during repetition 1 and no
  result file was written. The clean timing study was restarted with no
  compute-intensive experiment running concurrently.
- In the clean study (five repetitions, six held-out image/deformation pairs,
  alternating method order), full-resolution one-shot prediction reduced median
  iterations by 44.4% and paired total time by 41.7% versus the validation-
  selected global pair. The bootstrap 95% interval for time reduction was
  [40.9%, 42.6%], tuning was 1.58% of proposed runtime, median relative MSE
  change was -0.0068%, and no case folded. These are controlled known warps on
  two public images; they are not FIRE/ANHIR benchmark results.
- Coarse-level one-shot reuse met the overhead gate but missed the paired runtime
  gate. Per-level reuse met the runtime gate but missed the overhead gate. The
  full-resolution one-shot statistic is therefore a tested methodological
  improvement, not a relabelling of the earlier reuse policy.

## 2026-08-06: public data acquisition

- Prepared two reproducible public sample images distributed by scikit-image:
  a CC0 retina and an unrestricted immunohistochemistry image. These constitute
  realistic image content with controlled known deformations, not benchmark
  landmark datasets.
- An earlier FIRE transfer was incomplete, but the user subsequently supplied a
  complete `data/downloads/FIRE.7z`. On 2026-08-06, `7z l` verified 405 entries
  (268 images and 134 control-point files) and extraction to `data/raw/fire/FIRE`
  completed. The earlier "not acquired" status was superseded.
- Added resumable FIRE preparation and landmark-evaluation scripts. A 128x128
  phase-initialized pilot completed one pair from each A/P/S stratum. Predictor
  versus the external fixed pair had essentially identical median TRE: A01
  2.718/2.718 px, P01 21.252/21.252 px, and S01 7.157/7.248 px; its inner
  iteration counts were 244/429, 224/472, and 259/345, respectively. This is a
  three-pair pilot only, not a paper-level FIRE result. The full 256x256 protocol
  remains the prescribed run for an unconstrained benchmark machine.
- Completed the controlled full FIRE 128x128 CPU run: all 134 supplied
  landmarked pairs (14 A, 49 P, 71 S), with identical phase initialization, two
  methods, and one BLAS/OMP thread. The four-corner predictor reduced paired
  median total runtime by 33.6% (bootstrap 95% CI 32.5%--34.7%), solver time by
  33.7%, and iterations by 40.7% versus the external fixed pair $(0.1,1)$.
  Median TRE changed by -1.1e-5 px (2.85282 vs 2.85284 px); 27 individual pairs
  were infinitesimally worse in TRE, no subproblem failed, and no final field
  had a nonpositive Jacobian. Raw CSV and derived JSON are retained.
- Began a complete default/over-relaxed/residual/BB FIRE sweep under the same
  protocol. Default-parameter hard cases repeatedly reached the prescribed
  inner-iteration cap, making the all-pair sweep disproportionate to its added
  evidentiary value. It was stopped with separately preserved partial shards
  and is not used in any table, figure, or claim. CIMA remains the full
  multi-baseline comparison; FIRE's complete claim is explicitly limited to the
  external fixed comparator.
- ANHIR download requires an authenticated challenge account and is therefore
  documented but not silently substituted with inaccessible data.

## 2026-08-06: scalable certification

- Implemented a sparse truncated periodic Cayley-kernel comparison rectangle.
  The omitted convolution is bounded by its kernel l1 tail. Tests cover the
  zero-commutator case and validate enclosure against the dense reduced spectrum.
- Certification scaling/tightness measurements are stored only after completion;
  an absent result file means the run did not complete and must not be cited.
- Twenty radius/size cases through 64x64 had zero enclosure violations. Bounds
  were 0.638--0.681 for actual radii near 0.269, giving relative gaps of
  1.38--1.54. The most expensive 64x64 retained-radius case took 81.4 s. A
  relaxed 128x128 Arnoldi/certificate attempt did not complete within the
  allocated diagnostic window and was interrupted without a result file.
  Therefore the present certificate is a small-problem diagnostic, not a
  practical registration-time component; the predictor is the scalable method.

## 2026-08-06: CIMA landmark benchmark

- Acquired the archived public `Borda/dataset-histology-landmarks` repository at
  commit `8413e09e1e53b0e6fc101ae9d7b760c47cc20c77`. Its committed sample has
  five differently stained lung-lesion-3 images and manual annotations, giving
  ten unordered landmark pairs.
- A phase-only initial run succeeded on two pairs but failed catastrophically on
  others. A robust image-only initializer was developed from bounded phase,
  centroid, and clustered SIFT proposals selected by structural-channel NCC.
  Landmarks were never used for initialization or parameter tuning.
- Full-resolution SIFT initialization was correct but consumed about 2.1 s and
  hid solver speedups. Running the identical initialization at 128x128 reduced
  it to about 0.4 s and improved several difficult pairs. Both raw protocols are
  preserved.
- The first full CIMA run exposed folding introduced during pyramid upsampling.
  Those raw results are preserved as `cima_landmarks_folded_baseline.csv` and
  `cima_repeated_timing_folded.csv`. A shared safeguard now damps only the
  non-translational field after interpolation until the Jacobian floor holds.
- The final protocol has zero global/interior folding cases. Over five repeated
  timings and 50 paired runs, one-shot prediction reduced total runtime 20.1%
  (bootstrap 95% CI 19.4%--20.7%), solver time 23.5%, and iterations 30.1%
  versus the external fixed pair. Tuning used 1.16% of runtime. Median TRE was
  7.33 px (2.02% diagonal), unchanged between methods; median landmark
  improvement was 36.5%. One pair remained above 22 px TRE.
- An exact numerical spectral optimizer on 8x8 variable-coefficient surrogates
  used a median 97 objective evaluations and 2.18 s tuning. Its transferred full
  solve used 251 median iterations and 4.39 s total versus 210 and 2.02 s for
  the four-corner predictor. This is recorded as a coarse Song-style diagnostic,
  not full-resolution Song optimization.
- FIRE remained incomplete after repeated official-server disconnects. A later
  wget resume request was blocked by the execution-service download quota. No
  partial archive or retinal number enters the paper.
