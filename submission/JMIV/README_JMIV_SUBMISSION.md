# JMIV submission package

Self-contained Springer Nature package for the
*Journal of Mathematical Imaging and Vision* (JMIV), synced from `paper/`.

## Layout

- `main/`: compilable two-column (`iicol`) manuscript source, class file,
  bibliography, figures, and PDF.
- `supplement/`: Online Resource 1 (Supplementary Information) source and PDF.
- `figures/`: vector PDF figures used by the main manuscript.
- `cover_letter/`: cover letter (`.txt`, `.tex`, `.pdf`).
- `template_original/`: unmodified official Springer Nature template.
- `JMIV_main_source.zip`: flat editable manuscript source for SNAPP.
- `ESM_1_source.zip`: flat Online Resource 1 source (optional companion).

Rebuild from the repository root:

```bash
python scripts/prepare_jmiv_submission.py
```

## Upload files

| SNAPP field | File |
|---|---|
| Manuscript PDF | `main/JMIV_main.pdf` |
| Editable source | `JMIV_main_source.zip` |
| Online Resource 1 | `supplement/ESM_1_Supplementary_Information.pdf` |
| Cover letter | `cover_letter/JMIV_cover_letter.pdf` or `.txt` |

**Note.** The abstract is kept identical to `paper/paper.tex` (~241 words).
JMIV asks for 100--150 words in the portal; condense only if required by SNAPP.

Complete `JMIV_SUBMISSION_TODO.md` and `JMIV_submission_checklist.md` before
portal submission.
