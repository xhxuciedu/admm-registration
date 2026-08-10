# Final JMIV upload checklist

## Files

- [ ] Upload `upload/JMIV_main.pdf`.
- [ ] Upload `upload/JMIV_main_source.zip` as editable manuscript source.
- [ ] Upload `upload/ESM_1_Supplementary_Information.pdf` as Online Resource 1.
- [ ] Upload or paste the cover letter in `upload/JMIV_cover_letter.pdf` or
  `upload/JMIV_cover_letter.txt`.
- [ ] Retain `JMIV_submission_metadata.md` and `JMIV_requirements.md` while
  entering portal metadata.

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
- [ ] Extract the source ZIP into a clean directory and compile
  `JMIV_main.tex` with `pdflatex` twice.
- [ ] Open main PDF, supplement, and cover letter at normal viewing size.
- [ ] Confirm all figure labels, citations, tables, and Online Resource 1
  reference are visible.
- [ ] Complete every item in `JMIV_SUBMISSION_TODO.md`.
