# JMIV submission requirements audit

Verified 2026-08-10 against the official [JMIV submission guidelines](https://link.springer.com/journal/10851/submission-guidelines) and [Springer Nature LaTeX author support](https://www.springernature.com/la/authors/campaigns/latex-author-support).

| Requirement | Package status |
|---|---|
| Article category | Prepared as a Regular Paper. |
| Title page | Contains author name, affiliation, city/state/country, and e-mail. Corresponding-author telephone/fax must be completed in the submission interface; see TODO. |
| Abstract | 128 words; JMIV requires 100--150 words. |
| Keywords | Five indexing keywords are supplied; JMIV requests four to six. |
| Citations | Numbered citations are used in the manuscript. |
| Editable sources | `upload/JMIV_main_source.zip` includes `.tex`, `.cls`, and figures. |
| PDF | `upload/JMIV_main.pdf` is compiled with `pdflatex`. |
| Figures | `Fig1.pdf` and `Fig2.pdf` are vector PDFs with embedded text.  The journal prefers EPS for vector art; PDF is `pdflatex`-native and included with the source. |
| Supplement | `upload/ESM_1_Supplementary_Information.pdf` contains title, journal, author, affiliation, and e-mail, and the main text cites it as Online Resource 1. |
| Declarations | Author-contribution and competing-interest information must be supplied through the submission interface. |

## Template and `iicol` compatibility

The original official template downloaded for this package is Springer Nature
SN Article Template v3.1 (December 2024), preserved unchanged in
`template_original/sn-article-template/`.  Its supplied `sn-jnl.cls` and
example source provide the `sn-mathphys-num` numbered mathematical-physical
science style but do **not** define the legacy `iicol` class option.  The JMIV
guideline page still recommends `[iicol]`.  The submitted source therefore
uses the current official, compiling configuration
`\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}` rather than inventing an
unsupported option.  Confirm this template-option transition with JMIV/SNAPP
at upload if the portal rejects the current official class configuration.

## Submission-system notes

Springer Nature's author-support page requests a `pdflatex`-compatible ZIP for
SNAPP and warns that subdirectories can cause missing-figure errors.  The
upload ZIP is deliberately flat.  The official JMIV guideline page requires
that submission imply originality, exclusive consideration, required approvals,
and permissions for previously published material.  Those are author
attestations, not claims this package can make automatically.
