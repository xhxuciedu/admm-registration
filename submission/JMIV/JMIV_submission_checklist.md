# Final JMIV upload checklist

## Files

- [ ] Upload `main/JMIV_main.pdf`.
- [ ] Upload `JMIV_main_source.zip` as editable manuscript source.
- [ ] Upload `supplement/ESM_1_Supplementary_Information.pdf` as Online Resource 1.
- [ ] Upload or paste the cover letter in `cover_letter/JMIV_cover_letter.pdf`
  or `cover_letter/JMIV_cover_letter.txt`.
- [ ] Use `JMIV_submission_metadata.md` and `JMIV_requirements.md` when entering
  portal metadata.

## Portal metadata

- [ ] Select **Regular Paper**.
- [ ] Verify 100--150-word abstract and five keywords.
- [ ] Enter author, affiliation, e-mail, and required contact fields.
- [ ] Add the supplementary file caption: “Supplementary Information containing
  extended methods, proofs, and additional experiments.”
- [ ] Complete author-contribution and competing-interest declarations.
- [ ] Complete originality/exclusivity, permissions, funding, and ethics fields.
- [ ] Confirm any conference-extension disclosure.

## Pre-submit quality control

- [ ] Rebuild with `python scripts/prepare_jmiv_submission.py`.
- [ ] Extract `JMIV_main_source.zip` into a clean directory and compile
  `JMIV_main.tex` with `pdflatex` / `bibtex` / `pdflatex`×2.
- [ ] Open main PDF, supplement, and cover letter at normal viewing size.
- [ ] Confirm figure labels, citations, tables, and Online Resource 1 references.
- [ ] Complete every item in `JMIV_SUBMISSION_TODO.md`.
