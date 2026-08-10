# Codex / AI Agent Prompt: Prepare Complete JMIV Submission Package

## Target Journal

**Journal of Mathematical Imaging and Vision (JMIV)**  
Publisher: Springer Nature  
Submission system: Springer Nature Article Processing Platform (SNAPP)

## Manuscript

**Four-Corner Spectral Tuning for Search-Free ADMM in Diffeomorphic Image Registration**

## Author

**Xiaohui Xie**  
Department of Computer Science  
University of California, Irvine  
Irvine, California, USA  
Email: **xhx@uci.edu**

Xiaohui Xie is the sole author and corresponding author unless the repository/manuscript explicitly indicates otherwise.

---

# 1. Mission

Prepare **all files needed for a professional JMIV Regular Paper submission** from the current repository.

This is a submission-production task, not a new research project.

You must:

1. create and work on a separate git branch named exactly:

```bash
JMIV
```

2. download and use the **current official Springer Nature journal LaTeX template**;
3. verify the current **JMIV Instructions for Authors** from the official Springer Nature website before formatting;
4. convert the current finalized paper into the required JMIV/Springer format;
5. prepare the main manuscript, Supplementary Information, cover letter, declarations, figures, metadata, and source archives;
6. compile all LaTeX successfully with `pdflatex`;
7. perform a visual and technical quality check;
8. package the submission so it can be uploaded to SNAPP with minimal manual work;
9. create a concise checklist of only those items that still require author confirmation.

Do **not** fabricate:
- funding;
- competing interests;
- ORCID;
- phone/fax;
- grants;
- reviewer conflicts;
- repository URLs;
- ethical approvals.

If any such information is unavailable, flag it clearly in a final `JMIV_SUBMISSION_TODO.md`.

---

# 2. First: verify current official JMIV requirements

Before editing, open the current official pages:

- JMIV Submission Guidelines on Springer Nature;
- Springer Nature LaTeX Author Support;
- JMIV Aims and Scope;
- JMIV Fees/Funding page if relevant;
- the current SNAPP submission page if accessible.

Use **only current official Springer Nature/JMIV instructions as formatting authority**.

Record the access date and requirements in:

```text
submission/JMIV/JMIV_requirements.md
```

At minimum verify the following currently published requirements:

### Manuscript category

The current paper is a **Regular Paper**, not a Short Paper.

JMIV describes Short Papers as approximately 10 double-spaced manuscript pages or less; the present work is substantially longer.

### LaTeX

JMIV requests LaTeX manuscripts and recommends the Springer Nature LaTeX template.

The journal specifically recommends choosing the formatting option:

```text
[iicol]
```

Download the **current official Springer Nature journal article template package** from Springer Nature Author Support.

Do not use third-party templates.

Inspect the official template manual and determine the correct numeric Springer reference style consistent with JMIV's numbered square-bracket citations.

Do not guess a class option if the official template documentation can answer it.

### Abstract

JMIV requires:

```text
100–150 words
```

Rewrite the current abstract to this range while preserving:
- the four-corner theorem;
- search-free parameter selection;
- FIRE result;
- CIMA result;
- optional nature of rate certification.

Check the final word count automatically.

### Keywords

JMIV requires:

```text
4–6 keywords
```

Prepare 5 or 6 concise indexing keywords.

Candidate concepts include:
- alternating direction method of multipliers;
- diffeomorphic image registration;
- parameter selection;
- spectral analysis;
- local Fourier analysis;
- numerical optimization.

Choose the most appropriate 4–6.

### Title page

The title page should contain:
- article title;
- author name;
- affiliation and address;
- corresponding-author email.

Use:

```text
Xiaohui Xie
Department of Computer Science
University of California, Irvine
Irvine, California, USA
xhx@uci.edu
```

The JMIV instructions also mention telephone/fax information for the corresponding author.

Do not invent these.

If the submission system actually requires them, place:

```text
TODO_AUTHOR_PHONE
TODO_AUTHOR_FAX_OR_NOT_APPLICABLE
```

only in the author TODO/checklist, not as fake information in the final manuscript.

### References

JMIV uses:
- numbered references;
- square-bracket citations;
- consecutively numbered reference list.

Where available, include DOI links in the form requested by Springer.

Audit all references against official publisher metadata.

### Figures

Verify and follow current JMIV artwork instructions.

Current JMIV guidance includes:
- vector graphics preferred as EPS;
- fonts embedded;
- figure parts labeled by lowercase letters `(a), (b), ...`;
- figure captions belong in the manuscript text, not inside figure files;
- figures cited consecutively;
- readable final lettering, typically approximately 8–12 pt;
- minimum line width approximately 0.3 pt;
- color should remain interpretable in grayscale;
- accessibility considerations should be respected.

Generate publication-quality vector versions.

If the pdflatex source needs PDF figure files for reliable compilation, retain vector PDF versions for compilation and also generate EPS versions where appropriate for journal upload.

Do not compromise source compilation merely to force EPS.

### Supplementary Information

JMIV supplementary text should be supplied in durable form, preferably PDF.

The supplementary PDF must include:
- article title;
- journal name;
- author;
- affiliation;
- corresponding-author email.

JMIV asks supplementary resources to be cited from the manuscript using language such as:

```text
Online Resource 1
```

Follow the current journal convention exactly.

Supplementary files are published as received, so proofread them carefully.

### Data Availability

JMIV requires a **Data Availability Statement for original research**.

The statement must identify how the supporting data can be accessed and cite public datasets/repositories where appropriate.

Do not invent a code/data URL.

Inspect:
- `git remote -v`;
- repository README;
- existing manuscript statements;
- FIRE source;
- CIMA source;
- generated result files.

Prepare a precise Data Availability Statement.

### Declarations

JMIV/Springer requires appropriate declarations.

Prepare a `Declarations` section before the references containing, as applicable:

- Funding;
- Competing interests;
- Ethics approval;
- Consent to participate;
- Consent for publication;
- Data availability;
- Code availability;
- Author contributions.

Only include scientifically applicable declarations.

Do not fabricate funding or conflicts.

For a single-author paper, an appropriate author-contribution draft may state that Xiaohui Xie conceived the study, developed the theory and methodology, implemented/analyzed the experiments, and wrote the manuscript **only if the repository/project record supports this**.

If uncertain, flag for confirmation.

### Source files

JMIV requires complete editable source files at submission and revision.

Prepare:
- `.tex`;
- `.bib` and/or `.bbl`;
- Springer class/style files required by the source;
- figures;
- any additional LaTeX source files.

### SNAPP source packaging

The current Springer Nature LaTeX guidance says SNAPP expects LaTeX source that compiles with:

```bash
pdflatex
```

and should be uploaded as a compressed ZIP.

Use a **flat submission source directory** wherever possible.

Do not use figure subdirectories if this can cause missing-figure problems during Springer conversion.

---

# 3. Git workflow

From the repository root:

```bash
git status
git branch --show-current
```

Preserve all current work.

Create the target branch:

```bash
git checkout -b JMIV
```

If it already exists:

```bash
git checkout JMIV
```

Do not delete or overwrite previous branches.

At the end:

```bash
git status
git add <JMIV submission files and manuscript changes>
git commit -m "Prepare JMIV submission package"
```

If a remote is configured and authentication works:

```bash
git push -u origin JMIV
```

Do not force-push.

If push fails, record the failure but keep the local commit.

---

# 4. Submission directory structure

Create:

```text
submission/
└── JMIV/
    ├── README_JMIV_SUBMISSION.md
    ├── JMIV_requirements.md
    ├── JMIV_submission_checklist.md
    ├── JMIV_SUBMISSION_TODO.md
    ├── JMIV_submission_metadata.md
    ├── main/
    ├── supplement/
    ├── figures/
    ├── cover_letter/
    └── upload/
```

The `upload/` directory should contain the final files in the form intended for SNAPP.

---

# 5. Download and preserve the official Springer template

Download the current official Springer Nature journal-article LaTeX template package.

Store an untouched copy under:

```text
submission/JMIV/template_original/
```

if appropriate, or outside the git repository if licensing/size considerations make that preferable.

Create the working manuscript from the official template.

Do not distribute unnecessary template documentation in the upload package.

Document:
- template version/date;
- official download source;
- class options used;
- bibliography style used.

---

# 6. Convert the finalized paper to JMIV format

The current manuscript is scientifically finalized or nearly finalized.

Do not undo the recent editorial improvements.

The main scientific hierarchy must remain:

1. well-posed quadratic ADMM/oADMM is already contractive;
2. four-corner spectral tuning selects a rapidly convergent parameter pair;
3. FIRE and CIMA demonstrate practical utility;
4. variable-coefficient rate certification is secondary and optional.

Maintain the reduced prominence of certification.

Do not reintroduce old internal-research-report prose.

---

# 7. Main manuscript requirements

Prepare:

```text
submission/JMIV/main/JMIV_main.tex
submission/JMIV/main/JMIV_main.pdf
```

and any required `.bib`/`.bbl`.

## Title

Use:

**Four-Corner Spectral Tuning for Search-Free ADMM in Diffeomorphic Image Registration**

unless a scientifically necessary title change has already been approved in the current manuscript.

## Author

Use:

```text
Xiaohui Xie
Department of Computer Science
University of California, Irvine
Irvine, California, USA
xhx@uci.edu
```

Corresponding author:
**Xiaohui Xie**

## Abstract

100–150 words.

Automatically print/check word count in the build audit.

## Keywords

4–6.

## Main-text length

JMIV does not impose the Short Paper limit on a Regular Paper.

Do not unnecessarily compress mathematical proofs that are important to the main contribution.

However, preserve the current editorial decision:
- four-corner theory in main text;
- FIRE/CIMA main results in main text;
- certification details, implementation minutiae, and secondary diagnostics in Supplementary Information.

---

# 8. Supplementary Information

Prepare:

```text
submission/JMIV/supplement/ESM_1_Supplementary_Information.tex
submission/JMIV/supplement/ESM_1_Supplementary_Information.pdf
```

The first page must include:

```text
Supplementary Information for

Four-Corner Spectral Tuning for Search-Free ADMM in Diffeomorphic Image Registration

Journal of Mathematical Imaging and Vision

Xiaohui Xie
Department of Computer Science
University of California, Irvine
Irvine, California, USA
xhx@uci.edu
```

Organize supplement professionally, for example:

### S1 Reproducibility environment
- software versions;
- random seed;
- hardware;
- BLAS/OMP configuration;
- commands.

### S2 Registration implementation details
- multiresolution details;
- interpolation;
- line search;
- Jacobian safeguards;
- deformation composition.

### S3 Baseline implementations
- residual balancing;
- BB adaptive proxy;
- fixed oADMM;
- Song-style diagnostic;
- exact update/safeguard parameters.

### S4 Dataset preprocessing
- FIRE;
- CIMA;
- controlled pilot.

### S5 Additional theory
- legacy global perturbation bound;
- detailed signed certificates;
- Perron comparison;
- truncated kernel;
- long proofs not needed in main text.

### S6 Additional synthetic results
- structured stress tests;
- certificate scaling;
- parameter-quality diagnostics.

### S7 Controlled validation pilot
- external fixed-baseline selection;
- case indexing;
- detailed timing.

### S8 Additional FIRE analyses
- A/P/S subgroup statistics;
- parameter distributions;
- one-shot/per-level ablation;
- bootstrap details.

Use supplementary figure/table numbering consistently:

```text
Fig. S1
Fig. S2
Table S1
Table S2
```

Also ensure the main manuscript refers to this file according to the current JMIV `Online Resource` convention.

---

# 9. Figure preparation

Create final journal-quality figure files.

At minimum prepare:

```text
Fig1.pdf
Fig1.eps
Fig2.pdf
Fig2.eps
```

and any additional main-text figures.

For combination/raster artwork, create TIFF only if needed.

## Main Figure 1

Should communicate the central theory/predictor validation.

Prefer panels such as:
- (a) constant-coefficient exactness;
- (b) predictor-vs-oracle quality;
- (c) only a high-value third result.

Do not give certification disproportionate visual prominence.

If certificate behavior is secondary, move it to Supplementary Fig. S1.

## Main Figure 2 — FIRE

This must be publication quality.

Use lowercase journal panel labels:

```text
(a)
(b)
(c)
(d)
```

All axes must have:
- numbered ticks;
- explicit units;
- legible labels;
- consistent type size.

Recommended panels:

### (a) Runtime improvement
Pairwise four-corner runtime improvement relative to the externally validation-selected fixed comparator, stratified by A/P/S.

### (b) Iteration improvement
Paired ADMM iteration improvement by A/P/S.

### (c) TRE agreement
Prefer:
\[
\mathrm{TRE}_{\text{fixed}}
\quad\text{vs}\quad
\mathrm{TRE}_{\text{four-corner}}
\]
with identity line.

### (d) Image-dependent tuning
Prefer:
\[
h_+
\quad\text{vs}\quad
\rho_p
\]
or another scientifically informative visualization of parameter adaptation.

If the raw data do not permit this, show a well-labeled distribution of \(\rho_p\) and \(\alpha_p\).

The caption must define every panel and state:

```text
n = 134
```

and explain that percentage reductions are computed pairwise.

## Figure style

- vector output;
- embedded fonts;
- no plot title duplicated inside the figure if the caption already explains it;
- approximately 8–12 pt final lettering;
- sufficiently thick lines;
- colorblind-safe palette;
- understandable in grayscale;
- no notebook/default Matplotlib appearance;
- no low-resolution screenshots.

---

# 10. Tables

Ensure main tables match JMIV style and are cited consecutively.

Main FIRE table should include only informative columns, such as:

```text
Method
Median iterations
Median total time (s)
TRE (px)
TRE / image diagonal (%)
```

Include:
- external validation-selected fixed;
- residual balancing;
- BB adaptive proxy;
- fixed oADMM;
- four-corner one-shot.

Explain pairwise percentage reductions in text/caption.

Avoid meaningless decimal precision.

Move extensive implementation details and subgroup tables to Online Resource 1.

---

# 11. Data and Code Availability Statement

Prepare a publication-ready statement based on actual repository/data status.

Requirements:

1. identify FIRE as a public dataset and cite it properly;
2. identify CIMA/public histology resources properly;
3. state where code and generated experiment outputs are accessible;
4. use persistent/public URLs only if actually available;
5. do not expose private credentials or local filesystem paths;
6. if code repository is not yet public, flag this in `JMIV_SUBMISSION_TODO.md`.

If there is a public GitHub repository, verify it is accessible without authentication.

If appropriate, create a tagged release on the JMIV branch only if the user has already authorized repository publication.

Do not make a private repository public without explicit authorization.

---

# 12. Declarations section

Create a JMIV/Springer-compatible `Declarations` section.

Prepare fields:

```text
Funding
Competing interests
Ethics approval
Consent to participate
Consent for publication
Data availability
Code availability
Author contributions
```

For non-applicable categories, use concise `Not applicable.` only when scientifically and ethically correct.

Do not invent Funding or Competing Interests.

If absent from source materials, place them in:

```text
JMIV_SUBMISSION_TODO.md
```

for author confirmation before upload.

### Single-author contribution draft

If supported by the project record, draft:

> Xiaohui Xie conceived the study, developed the theoretical and computational methodology, implemented and analyzed the experiments, and wrote the manuscript.

Flag for author confirmation.

---

# 13. Cover letter

Prepare:

```text
submission/JMIV/cover_letter/JMIV_cover_letter.tex
submission/JMIV/cover_letter/JMIV_cover_letter.pdf
submission/JMIV/cover_letter/JMIV_cover_letter.txt
```

Use a professional letter addressed generically:

```text
Dear Editors,
```

unless the current Editor-in-Chief is verified from the official JMIV site and naming the editor adds value.

The cover letter should be concise, approximately one page.

It should state:

1. manuscript title;
2. article type: Regular Paper;
3. why the work fits JMIV;
4. main theoretical contribution:
   - rank-one registration structure;
   - exact four-corner spectral reduction;
   - finite search-free ADMM/oADMM parameter predictor;
5. main practical evidence:
   - FIRE \(256\times256\), all 134 pairs;
   - matched registration accuracy;
   - substantial runtime/iteration improvement;
   - CIMA independent result;
6. distinction from Song et al.:
   - Song is general and uses numerical spectral optimization;
   - this work is registration-specific and replaces numerical spectral search with four algebraic branches;
7. availability of code/data/reproducibility materials;
8. originality/exclusivity statement **only after confirming it is true**.

Do not overstate:
- variable-coefficient global optimality;
- superiority over all adaptive ADMM;
- global convergence of the nonlinear outer registration.

---

# 14. Submission metadata file

Create:

```text
submission/JMIV/JMIV_submission_metadata.md
```

Include copy-paste-ready fields:

```text
Journal:
Article type:
Title:
Running title:
Author:
Corresponding author:
Affiliation:
Email:
Abstract:
Keywords:
Funding:
Competing interests:
Data availability:
Code availability:
Author contributions:
Ethics approval:
Consent:
Cover letter:
Suggested reviewers:
Excluded reviewers:
```

For unresolved items, clearly mark:

```text
AUTHOR CONFIRMATION REQUIRED
```

Do not silently guess.

---

# 15. Suggested reviewers

JMIV welcomes reviewer suggestions, but suggestions must be independent.

Prepare:

```text
submission/JMIV/reviewer_suggestions_DRAFT.md
```

only if sufficient conflict information is available.

If generating candidates:

- suggest 4–6 researchers;
- use different institutions;
- preferably different countries;
- use institutional emails;
- include official faculty/homepage or publication-profile verification;
- choose researchers with expertise in:
  - ADMM/operator splitting;
  - mathematical imaging;
  - variational image registration;
  - numerical optimization.

Exclude:
- University of California, Irvine colleagues;
- known recent collaborators;
- recent coauthors;
- advisors/advisees if known;
- anyone with an obvious conflict.

Because conflict information may be incomplete, label the entire file:

```text
DRAFT — AUTHOR MUST REVIEW FOR CONFLICTS BEFORE SUBMISSION
```

Do not contact reviewers.

If conflict checking cannot be done reliably, leave reviewer suggestions as a TODO rather than guessing.

---

# 16. ORCID and contact details

Search the repository for an existing ORCID.

Do not infer or guess an ORCID from a name match.

If none is explicitly verified, add:

```text
ORCID: AUTHOR CONFIRMATION REQUIRED
```

to the TODO file.

Similarly do not invent:
- telephone number;
- fax number.

---

# 17. Reference audit

Audit every reference against authoritative metadata.

Check:
- author names;
- title;
- journal/conference;
- year;
- volume;
- issue;
- pages;
- DOI.

Retain the corrected Song et al. citation:

```text
J. Song, W. Lu, Y. Lei, Y. Tang, Z. Pan, and J. Duan,
"Optimizing ADMM and Over-Relaxed ADMM Parameters for Linear Quadratic Problems,"
Proceedings of the AAAI Conference on Artificial Intelligence,
38(8), 8117–8125 (2024).
```

Convert bibliography to the correct JMIV/Springer numeric style.

Where DOI links are available, format them according to current Springer instructions.

---

# 18. Main-paper final scientific audit

Before packaging, verify the manuscript does not contain contradictory older language.

Search for:

```text
predict-then-certify
CERTIFIED USEFUL
convergence audit
128^2
1282
first idea
decision gate
passes the gate
central lesson
catalogue of implementations
LLM
AI assistant
```

Review every hit.

The final paper must clearly state:

- basic convergence follows from well-posedness;
- four-corner tuning optimizes speed;
- certification is optional rate analysis;
- deployed FIRE/CIMA method does not compute certificates.

Also verify:
- controlled pilot case numbering;
- Theorem 5.3 uses attained regularizer extrema when claiming exactness;
- diffeomorphic/topology language accurately matches implementation;
- residual-balancing and BB descriptions are reproducible.

---

# 19. Main source packaging

Create a flat source directory:

```text
submission/JMIV/upload/main_source/
```

It should contain only files needed to compile the main manuscript, for example:

```text
JMIV_main.tex
JMIV_references.bib
JMIV_references.bbl
sn-jnl.cls
<required Springer .bst/style files>
Fig1.pdf
Fig1.eps
Fig2.pdf
Fig2.eps
...
```

Avoid nested figure paths.

Test from this exact directory:

```bash
pdflatex JMIV_main.tex
bibtex JMIV_main
pdflatex JMIV_main.tex
pdflatex JMIV_main.tex
```

or the exact bibliography sequence required by the official template.

Then test a clean build after deleting auxiliary files.

No:
- missing citations;
- `??`;
- undefined references;
- missing figures;
- compilation errors.

Create:

```text
submission/JMIV/upload/JMIV_main_source.zip
```

The ZIP should unpack to a flat set of submission source files, not an unnecessary nested project hierarchy.

---

# 20. Supplement packaging

Create:

```text
submission/JMIV/upload/ESM_1_Supplementary_Information.pdf
```

Also preserve editable supplement source in the repository.

If Springer/SNAPP accepts supplementary source as well, optionally prepare:

```text
ESM_1_source.zip
```

but the key upload file should be the final proofread supplementary PDF.

Ensure the main manuscript explicitly cites:

```text
Online Resource 1
```

according to current JMIV style.

---

# 21. Cover-letter packaging

Place the final cover letter at:

```text
submission/JMIV/upload/JMIV_cover_letter.pdf
```

Also prepare plain text for easy copy/paste into SNAPP.

---

# 22. Final upload directory

The final:

```text
submission/JMIV/upload/
```

should contain, at minimum:

```text
JMIV_main.pdf
JMIV_main_source.zip
JMIV_cover_letter.pdf
JMIV_cover_letter.txt
ESM_1_Supplementary_Information.pdf
JMIV_submission_metadata.md
JMIV_submission_checklist.md
```

If SNAPP requests separate figure uploads, prepare the final figure files there as well.

Do not include internal research logs or unnecessary working files in the upload directory.

---

# 23. JMIV submission checklist

Create:

```text
JMIV_submission_checklist.md
```

Include checkboxes for:

## Manuscript
- [ ] Regular Paper selected
- [ ] Springer Nature official template used
- [ ] `[iicol]` formatting verified
- [ ] abstract 100–150 words
- [ ] 4–6 keywords
- [ ] author name correct
- [ ] affiliation correct
- [ ] corresponding email correct
- [ ] declarations included
- [ ] Data Availability included
- [ ] references numbered and audited
- [ ] DOI formatting checked

## Figures
- [ ] all figures cited
- [ ] lowercase panel labels
- [ ] captions in manuscript
- [ ] axes numbered
- [ ] vector files created
- [ ] fonts embedded
- [ ] legible at final size
- [ ] grayscale/colorblind readability checked

## Supplement
- [ ] article title included
- [ ] journal name included
- [ ] author/affiliation/email included
- [ ] main manuscript cites Online Resource 1
- [ ] PDF proofread

## Source
- [ ] clean pdflatex compile
- [ ] no missing references
- [ ] no missing images
- [ ] source ZIP tested after extraction
- [ ] flat source structure

## Submission metadata
- [ ] Funding confirmed
- [ ] Competing interests confirmed
- [ ] author contribution confirmed
- [ ] ORCID confirmed if used
- [ ] phone/contact completed if portal requires
- [ ] reviewer suggestions reviewed for conflicts
- [ ] originality/exclusivity confirmed

---

# 24. Author-confirmation TODO file

Create:

```text
JMIV_SUBMISSION_TODO.md
```

This should be very short.

Only list actual unresolved items, for example:

```text
1. Confirm funding statement.
2. Confirm competing-interests statement.
3. Confirm ORCID.
4. Provide telephone number if SNAPP requires it.
5. Confirm author-contribution wording.
6. Confirm public code repository/release URL.
7. Review suggested reviewers for conflicts.
8. Confirm originality and that the paper is not under consideration elsewhere.
```

Do not bury unresolved author decisions in the manuscript source.

---

# 25. Submission README

Create:

```text
README_JMIV_SUBMISSION.md
```

Include:

- what each upload file is;
- exact build command;
- template version;
- abstract word count;
- keyword count;
- supplement citation;
- git commit hash;
- how to reproduce figures;
- unresolved TODO count;
- exact SNAPP upload order if it can be determined from the interface.

---

# 26. Visual quality check

Render the final main PDF and supplementary PDF page by page.

Inspect:

- title/author block;
- abstract;
- equations;
- theorem formatting;
- tables;
- figure captions;
- Fig. 1;
- Fig. 2;
- references;
- Online Resource citations;
- Declarations.

Specifically verify Fig. 2:
- `(a)–(d)` labels visible;
- axis ticks numerically labeled;
- fonts readable;
- no clipped labels;
- identity/reference lines visible;
- caption self-contained;
- plots informative rather than decorative.

Do not accept a figure simply because it compiles.

---

# 27. Professional language pass

Perform one final prose edit.

Remove:
- internal planning language;
- AI-like meta commentary;
- unnecessary explanation of manuscript organization;
- repetitive caveats;
- conversational phrasing.

The paper should read as a conventional JMIV research article.

Do not rewrite established mathematical claims in a way that changes meaning.

---

# 28. Final scientific consistency check

Cross-check headline numbers against raw data:

### FIRE
- 134 pairs;
- \(256\times256\);
- median iterations;
- median times;
- paired runtime improvement;
- bootstrap CI;
- BB comparison;
- residual balancing;
- fixed oADMM;
- TRE;
- normalized TRE;
- Jacobian results;
- one-shot/per-level ablation.

### CIMA
- ten pairs;
- runtime improvement;
- TRE;
- baseline comparisons.

### Theory
- basic contraction theorem;
- four-corner theorem;
- finite candidate theorem;
- no false claim of variable-coefficient global optimality.

Ensure Abstract, Results, Tables, Figures, Discussion, Conclusion, and Cover Letter use the same numbers.

---

# 29. Final git state

At completion:

```bash
git status
git diff --stat
git log -1 --oneline
```

Commit all intended JMIV changes.

Push branch if possible:

```bash
git push -u origin JMIV
```

Report:
- branch;
- commit hash;
- push status.

---

# 30. Final completion report

Output a concise report with:

```text
Branch: JMIV
Commit:
Push status:

JMIV article type: Regular Paper
Official Springer template version:
JMIV formatting option:
Reference style:

Main PDF:
Main source ZIP:
Supplement PDF:
Cover letter:
Submission metadata:
Submission checklist:

Abstract word count:
Keyword count:

Figures in main paper:
Tables in main paper:
Online Resources:

Data Availability present: yes/no
Declarations present: yes/no
Author contribution present: yes/no
Funding confirmed: yes/no
Competing interests confirmed: yes/no
ORCID confirmed: yes/no
Reviewer suggestions prepared: yes/no

Clean pdflatex build: yes/no
Clean build after ZIP extraction: yes/no
Visual inspection passed: yes/no
All references resolved: yes/no
All figures resolved: yes/no

Remaining author confirmations:
1. ...
2. ...

Submission readiness:
GO / GO AFTER AUTHOR CONFIRMATIONS / NO-GO
```

---

# 31. Scope discipline

Do not:
- add new experiments unless required to fix an inconsistency;
- re-expand certification in the main text;
- change the four-corner theory without evidence of an error;
- make the repository public without explicit authorization;
- invent reviewer conflicts;
- invent funding/conflict/ORCID/contact information;
- contact editors/reviewers;
- submit the manuscript automatically.

The goal is to prepare a complete, professional **JMIV upload package** on the `JMIV` branch so that the author can review the remaining confirmations and submit through SNAPP.
