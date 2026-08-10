# JMIV submission package

This directory contains a submission-ready, editable-source package for the
*Journal of Mathematical Imaging and Vision* (JMIV).  It is generated from the
audited manuscript, figures, and result tables in this repository.

## Contents

- `main/`: compilable Springer Nature LaTeX manuscript source and PDF.
- `supplement/`: separately compilable supplementary-information source and PDF.
- `figures/`: the two retained vector PDF figures.
- `cover_letter/`: editable text/LaTeX cover letter and PDF.
- `template_original/`: unmodified official Springer Nature template package.
- `upload/`: flat files intended for SNAPP upload, including
  `JMIV_main_source.zip` and `ESM_1_Supplementary_Information.pdf`.

## Rebuild

From the repository root, after the official template has been downloaded to
`submission/JMIV/template_original/sn-article-template/`, run:

```bash
python scripts/prepare_jmiv_submission.py
```

The command runs `pdflatex` twice for the main article and once each for the
supplement and cover letter.  It then refreshes the flat upload bundle.

Before uploading, complete every author-controlled item in
`JMIV_SUBMISSION_TODO.md` and use `JMIV_submission_checklist.md` as the final
portal checklist.  The source ZIP contains the manuscript `.tex`, the official
class file, and both PDF vector figures at one directory level; this avoids
missing-figure failures in manuscript systems that do not preserve source
subdirectories.
