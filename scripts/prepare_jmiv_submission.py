#!/usr/bin/env python3
"""Build the self-contained JMIV/Springer submission package from audited sources."""
from __future__ import annotations
import shutil, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "JMIV"
MAIN = OUT / "main"; SUPP = OUT / "supplement"; FIG = OUT / "figures"; COVER = OUT / "cover_letter"; UP = OUT / "upload"
TEMPLATE = OUT / "template_original" / "sn-article-template"
TITLE = "Four-Corner Spectral Tuning for Search-Free ADMM in Diffeomorphic Image Registration"
ABSTRACT = ("ADMM parameter choice strongly affects variational image-registration runtime. "
"For a well-posed quadratic subproblem, every admissible penalty and relaxation is already contractive; "
"the practical task is to select a rapidly convergent pair without numerical spectral search. "
"The rank-one pixelwise registration Hessian and scalar Sobolev symbol reduce constant-model tuning exactly "
"to four curvature--symbol corners, yielding a finite algebraic one-shot predictor. On 134 FIRE retinal pairs "
"at 256 by 256, the predictor reduced median pairwise runtime by 34.4\% and inner iterations by 39.6\% "
"relative to an externally validation-selected fixed pair, while landmark error and topology were unchanged. "
"It was also 51.7\% faster than a safeguarded BB proxy. On ten CIMA histology pairs, matched-protocol runtime "
"decreased by 20.1\%. Signed variable-coefficient enclosures provide optional rigorous rate bounds but are not "
"used during tuning.")

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)

def main_tex() -> str:
    src = (ROOT / "paper" / "paper.tex").read_text()
    body = src.split("\\end{abstract}", 1)[1].rsplit("\\end{document}", 1)[0]
    body = body.replace("../figures/algebraic_validation.pdf", "Fig1.pdf").replace("../figures/fire256_headline.pdf", "Fig2.pdf")
    # Keep the upload flat and self-contained: JMIV receives one editable source
    # rather than a source that depends on a generated fragment.
    table = (ROOT / "paper" / "generated" / "fire256_table.tex").read_text().strip()
    body = body.replace("\\input{generated/fire256_table.tex}", table)
    preamble = r"""\documentclass[pdflatex,sn-mathphys-num]{sn-jnl}
\usepackage{amsmath,amssymb,amsthm,mathtools,bm,booktabs,array,multirow,float,graphicx,xcolor,microtype,hyperref,enumitem,url,cleveref}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}\newtheorem{assumption}[theorem]{Assumption}
\theoremstyle{definition}\newtheorem{definition}[theorem]{Definition}\newtheorem{remark}[theorem]{Remark}
\newcommand{\R}{\mathbb{R}}\newcommand{\I}{\mathbf{I}}\newcommand{\norm}[1]{\left\lVert #1\right\rVert}
\newcommand{\spec}{\operatorname{spec}}\newcommand{\spr}{\varrho}\newcommand{\diag}{\operatorname{diag}}
\newcommand{\argmin}{\operatorname*{arg\,min}}\newcommand{\argmax}{\operatorname*{arg\,max}}\newcommand{\clip}{\operatorname{clip}}\newcommand{\cay}[2]{\mathcal{C}_{#1}(#2)}
\title[Four-Corner Spectral Tuning]{Four-Corner Spectral Tuning for Search-Free ADMM in Diffeomorphic Image Registration}
\author*[1]{\fnm{Xiaohui} \sur{Xie}}\email{xhx@uci.edu}
\affil*[1]{\orgdiv{Department of Computer Science}, \orgname{University of California, Irvine}, \orgaddress{\city{Irvine}, \state{California}, \country{USA}}}
\abstract{""" + ABSTRACT + r"""}
\keywords{alternating direction method of multipliers, diffeomorphic image registration, parameter selection, spectral analysis, local Fourier analysis}
\begin{document}\maketitle
"""
    return preamble + body + "\n\\end{document}\n"

def build() -> None:
    for d in (MAIN, SUPP, FIG, COVER, UP): d.mkdir(parents=True, exist_ok=True)
    write(MAIN / "JMIV_main.tex", main_tex())
    for src, dst in [(ROOT / "figures" / "algebraic_validation.pdf", "Fig1.pdf"), (ROOT / "figures" / "fire256_headline.pdf", "Fig2.pdf")]: shutil.copy2(src, MAIN / dst); shutil.copy2(src, FIG / dst)
    shutil.copy2(TEMPLATE / "sn-jnl.cls", MAIN / "sn-jnl.cls")
    # The package uses an in-file bibliography, so no .bib/.bst dependency is needed.
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "JMIV_main.tex"], cwd=MAIN, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "JMIV_main.tex"], cwd=MAIN, check=True, stdout=subprocess.DEVNULL)
    shutil.copy2(MAIN / "JMIV_main.pdf", UP / "JMIV_main.pdf")
    supp = (ROOT / "paper" / "supplementary.tex").read_text().replace("Supplementary Information:", "Supplementary Information for")
    supp = supp.replace("\\author{Anonymous}", "\\author{Xiaohui Xie\\\\Department of Computer Science, University of California, Irvine\\\\Irvine, California, USA\\\\xhx@uci.edu}")
    supp = supp.replace("\\date{}", "\\date{Journal of Mathematical Imaging and Vision}")
    write(SUPP / "ESM_1_Supplementary_Information.tex", supp)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "ESM_1_Supplementary_Information.tex"], cwd=SUPP, check=True, stdout=subprocess.DEVNULL)
    shutil.copy2(SUPP / "ESM_1_Supplementary_Information.pdf", UP / "ESM_1_Supplementary_Information.pdf")
    letter = f"""Dear Editors,

Please consider the enclosed Regular Paper, \"{TITLE},\" for publication in the Journal of Mathematical Imaging and Vision. The manuscript develops a registration-specific ADMM/oADMM parameter-selection method. Rank-one pixelwise data Hessians and a scalar regularizer reduce the constant-model spectral problem to four curvature--symbol corners, giving a finite algebraic predictor without numerical spectral search.

On all 134 FIRE pairs at 256 by 256, the one-shot predictor reduced median pairwise runtime by 34.4% and inner iterations by 39.6% relative to an externally validation-selected fixed pair, with unchanged landmark error and no nonpositive discrete Jacobians. It was also faster than residual balancing, fixed oADMM, and a safeguarded BB proxy. A CIMA histology study independently showed a 20.1% matched-protocol runtime reduction.

The work fits JMIV through its combination of operator-splitting analysis, variational registration, and reproducible imaging experiments. In contrast with the general numerical spectral optimization of Song et al., this method uses registration structure to avoid iterative spectral search. Detailed code, processed result tables, and data-preparation instructions accompany the manuscript.

The author will complete the required submission-interface declarations concerning originality, exclusivity, author contributions, competing interests, and contact details.

Sincerely,
Xiaohui Xie
"""
    letter_tex = ("\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n"
                  "\\begin{document}\n\\noindent\n" +
                  letter.replace("%", "\\%").replace("\n\n", "\\par\n\n") +
                  "\\end{document}\n")
    write(COVER / "JMIV_cover_letter.txt", letter)
    write(COVER / "JMIV_cover_letter.tex", letter_tex)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "JMIV_cover_letter.tex"], cwd=COVER, check=True, stdout=subprocess.DEVNULL); shutil.copy2(COVER / "JMIV_cover_letter.pdf", UP / "JMIV_cover_letter.pdf"); shutil.copy2(COVER / "JMIV_cover_letter.txt", UP / "JMIV_cover_letter.txt")
    source = UP / "main_source"
    source.mkdir(exist_ok=True)
    for name in ("JMIV_main.tex", "sn-jnl.cls", "Fig1.pdf", "Fig2.pdf"):
        shutil.copy2(MAIN / name, source / name)
    # A previous generator version emitted this intermediate fragment. It is
    # intentionally absent from the self-contained current source.
    stale_table = source / "fire256_table.tex"
    if stale_table.exists():
        stale_table.unlink()
    for name in ("README_JMIV_SUBMISSION.md", "JMIV_requirements.md", "JMIV_submission_checklist.md", "JMIV_submission_metadata.md", "JMIV_SUBMISSION_TODO.md", "CONSISTENCY_CHECK_REPORT.md"):
        shutil.copy2(OUT / name, UP / name)
    with zipfile.ZipFile(UP / "JMIV_main_source.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("JMIV_main.tex", "sn-jnl.cls", "Fig1.pdf", "Fig2.pdf"):
            z.write(source / name, name)

if __name__ == "__main__": build()
