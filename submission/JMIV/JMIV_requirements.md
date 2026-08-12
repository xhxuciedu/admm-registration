# JMIV submission requirements audit

Verified against the official JMIV submission guidelines and Springer Nature
LaTeX author support.

| Requirement | Package status |
|---|---|
| Article category | Prepared as a Regular Paper. |
| Title page | Author names, affiliation, city/state/country, and e-mail. |
| Abstract | Taken from `paper/paper.tex` (target 100--150 words). |
| Keywords | Five indexing keywords. |
| Citations | Numbered (`sn-mathphys-num`). |
| Editable sources | Flat `JMIV_main_source.zip` with `.tex`, `.cls`, `.bst`, `.bib`, and figures. |
| PDF | `main/JMIV_main.pdf` compiled with `pdflatex`. |
| Figures | Vector PDF figures with embedded text (`Fig1.pdf`, `Fig2.pdf`). |
| Supplement | `supplement/ESM_1_Supplementary_Information.pdf`; main text cites Online Resource 1. |
| Declarations | Included in the manuscript and mirrored for the submission interface. |

## Template configuration

Official Springer Nature SN Article Template (`sn-jnl.cls`) with
`\documentclass[pdflatex,iicol,sn-mathphys-num]{sn-jnl}`.

## Notes

SNAPP may fail on nested source directories; the upload ZIP is deliberately flat.
