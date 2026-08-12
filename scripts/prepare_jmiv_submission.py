#!/usr/bin/env python3
"""Sync paper/ into a Springer Nature JMIV (iicol) submission package.

Content is taken from paper/paper.tex and paper/supplementary.tex.
Only formatting/packaging transforms are applied for two-column submission.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "JMIV"
MAIN = OUT / "main"
SUPP = OUT / "supplement"
FIG = OUT / "figures"
COVER = OUT / "cover_letter"
TEMPLATE = OUT / "template_original" / "sn-article-template"
TITLE = (
    "Four-Corner Spectral Tuning for Quadratic ADMM "
    "with Application to Diffeomorphic Image Registration"
)
SHORT_TITLE = "Four-Corner Spectral Tuning"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def extract_between(text: str, start: str, end: str) -> str:
    a = text.index(start) + len(start)
    b = text.index(end, a)
    return text[a:b].strip()


def run_latex(cwd: Path, tex_name: str, runs: int = 2, bibtex: bool = False) -> None:
    import os

    texbin = Path("/usr/local/texlive/2026basic/bin/universal-darwin")
    if texbin.exists():
        os.environ["PATH"] = f"{texbin}:{os.environ.get('PATH', '')}"
    # Prefer TeX Live's array.sty over a broken personal copy that shadows it.
    system_array = Path(
        "/usr/local/texlive/2026basic/texmf-dist/tex/latex/tools/array.sty"
    )
    if system_array.exists():
        shutil.copy2(system_array, cwd / "array.sty")
    cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_name]
    for _ in range(1 if bibtex else runs):
        subprocess.run(cmd, cwd=cwd, check=True)
    if bibtex:
        stem = Path(tex_name).stem
        subprocess.run(["bibtex", stem], cwd=cwd, check=True)
        for _ in range(2):
            subprocess.run(cmd, cwd=cwd, check=True)


def adapt_main_body(body: str) -> str:
    """Two-column formatting transforms; scientific text unchanged."""
    # Flat figure names for SNAPP (no subdirectories).
    body = body.replace("../figures/algebraic_validation.pdf", "Fig1.pdf")
    body = body.replace("../figures/fire256_headline.pdf", "Fig2.pdf")

    # Inline generated table fragment if present.
    gen = ROOT / "paper" / "generated" / "fire256_table.tex"
    if gen.exists() and "\\input{generated/fire256_table.tex}" in body:
        body = body.replace("\\input{generated/fire256_table.tex}", gen.read_text().strip())

    # Supplementary cross-references for Online Resource 1.
    body = re.sub(
        r"Supplementary Sections?\s*~?\s*",
        "Online Resource~1, Section~",
        body,
    )
    body = body.replace(
        "Online Resource~1, Section~2--7",
        "Online Resource~1, Sections~2--7",
    )
    body = body.replace(
        "Online Resource~1, Section~10 and 9",
        "Online Resource~1, Sections~10 and~9",
    )
    body = body.replace(
        "Online Resource~1, Section~10 and~9",
        "Online Resource~1, Sections~10 and~9",
    )
    # Collapse accidental double ties from "Section~9" sources.
    body = body.replace("Section~~", "Section~")

    # Floats: multipanel figures and wide tables span both columns.
    body = body.replace("\\begin{figure}[H]", "\\begin{figure*}[t]")
    body = body.replace("\\end{figure}", "\\end{figure*}")
    body = body.replace("width=.98\\linewidth", "width=\\textwidth")

    # Convert remaining float-[H] tables to [t].
    body = body.replace("\\begin{table}[H]", "\\begin{table}[t]")

    # Wide tables with long method names span both columns.
    for caption_start in (
        "FIRE retinal registration:",
        "CIMA histology registration",
    ):
        m_tab = re.search(
            rf"\\begin\{{table\}}\[t\]\n\\centering\n(?:\\footnotesize\n|\\small\n)?"
            rf"\\caption\{{{re.escape(caption_start)}.*?\\end\{{table\}}",
            body,
            flags=re.S,
        )
        if not m_tab:
            continue
        block = m_tab.group(0)
        block = block.replace("\\begin{table}[t]", "\\begin{table*}[t]", 1)
        block = block.replace("\\end{table}", "\\end{table*}", 1)
        if "\\footnotesize" not in block[: block.index("\\caption")]:
            block = block.replace("\\centering\n\\small\n", "\\centering\n\\footnotesize\n", 1)
            block = block.replace("\\centering\n", "\\centering\n\\footnotesize\n", 1)
        body = body[: m_tab.start()] + block + body[m_tab.end() :]

    # footnotesize for remaining single-column tables.
    body = re.sub(
        r"(\\begin\{table\}\[t\]\n\\centering\n)(?!\\footnotesize)",
        r"\1\\footnotesize\n",
        body,
    )

    # Algorithm box → ruled algorithm float (single column).
    alg_pat = re.compile(
        r"\\begin\{center\}\s*"
        r"\\fbox\{\\begin\{minipage\}\{0\.92\\linewidth\}\s*"
        r"\\textbf\{Algorithm 1: One-Shot Four-Corner oADMM Tuning\}\s*"
        r"(.*?)"
        r"\\end\{minipage\}\}\s*"
        r"\\end\{center\}",
        re.S,
    )

    def alg_repl(m: re.Match[str]) -> str:
        inner = m.group(1).strip()
        # Drop emph Inputs/Output lines' leading markup into caption body.
        return (
            "\\begin{algorithm}[t]\n"
            "\\caption{One-Shot Four-Corner oADMM Tuning}\n"
            "\\label{alg:oneshot}\n"
            "\\footnotesize\n"
            f"{inner}\n"
            "\\end{algorithm}"
        )

    body = alg_pat.sub(alg_repl, body)

    # Declarations / SI heading for Springer backmatter.
    body = body.replace(
        "\\section*{Declarations}",
        "\\backmatter\n"
        "\\bmhead{Supplementary information}\n"
        "Extended methods, proofs, certificate constructions, and additional "
        "experiments are provided in Online Resource~1.\n\n"
        "\\section*{Declarations}",
    )

    # Bibliography: keep BibTeX; class sets sn-mathphys-num.
    body = body.replace("\\bibliographystyle{abbrv}\n", "")
    body = body.replace("\\bibliography{references}", "\\bibliography{references}")

    # Strip leftover Keywords block already handled in preamble.
    body = re.sub(
        r"\\noindent\\textbf\{Keywords:\}.*?local Fourier analysis\n",
        "",
        body,
        flags=re.S,
    )
    # Strip article-style title/author if present after abstract split.
    body = re.sub(r"^\\maketitle\n+", "", body)

    # Tighten display math that tends to overflow two columns.
    body = body.replace(
        "\\begin{align*}\n"
        "\\text{quadratic ADMM}&\\longrightarrow\\text{modal factor}\n"
        "\\longrightarrow\\text{four corners}\\\\\n"
        "&\\longrightarrow\\text{finite parameter selection}\n"
        "\\longrightarrow\\text{noncommuting registration}.\n"
        "\\end{align*}",
        "\\begin{align*}\n"
        "\\text{quadratic ADMM}&\\longrightarrow\\text{modal factor}"
        "\\longrightarrow\\text{four corners}\\\\\n"
        "&\\longrightarrow\\text{finite selection}"
        "\\longrightarrow\\text{registration}.\n"
        "\\end{align*}",
    )

    # Break wide one-line displays into multiline (math unchanged).
    wide_repls = [
        (
            "\\[\n"
            "C_H(\\rho)=(H-\\rho\\Id)(H+\\rho\\Id)^{-1},\\qquad\n"
            "C_G(\\rho)=(G-\\rho\\Id)(G+\\rho\\Id)^{-1}.\n"
            "\\]",
            "\\begin{align}\n"
            "C_H(\\rho)&=(H-\\rho\\Id)(H+\\rho\\Id)^{-1},\\nonumber\\\\\n"
            "C_G(\\rho)&=(G-\\rho\\Id)(G+\\rho\\Id)^{-1}.\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "\\{(h,g): Hx=hx,\\ Gx=gx\\text{ for a common mode }x\\ne0\\}\n"
            "=\\mathcal H\\times\\mathcal G.\n"
            "\\]",
            "\\begin{equation}\n"
            "\\begin{aligned}\n"
            "&\\{(h,g): Hx=hx,\\ Gx=gx\\text{ for a common mode }x\\ne0\\}\\\\\n"
            "&\\qquad=\\mathcal H\\times\\mathcal G.\n"
            "\\end{aligned}\n"
            "\\end{equation}",
        ),
        (
            "\\[\n"
            "F_{ij}^{(1)}(\\rho)=\n"
            "\\frac{\\theta_j(\\rho)-\\theta_i(\\rho)}\n"
            "{2-\\theta_i(\\rho)-\\theta_j(\\rho)}\n"
            "\\quad\\text{and}\\quad\n"
            "F_j^{(2)}(\\rho)=2\\theta_j(\\rho)-1\n"
            "\\]",
            "\\begin{align}\n"
            "F_{ij}^{(1)}(\\rho)&=\n"
            "\\frac{\\theta_j(\\rho)-\\theta_i(\\rho)}\n"
            "{2-\\theta_i(\\rho)-\\theta_j(\\rho)},\\nonumber\\\\\n"
            "F_j^{(2)}(\\rho)&=2\\theta_j(\\rho)-1.\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "\\widetilde v^{k+1}=P_H(\\widetilde w^k-\\widetilde u^k),\\qquad\n"
            "\\widehat{\\widetilde v}^{k+1}\n"
            "=[\\alpha P_H+(1-\\alpha)\\Id]\\widetilde w^k\n"
            "-\\alpha P_H\\widetilde u^k.\n"
            "\\]",
            "\\begin{align}\n"
            "\\widetilde v^{k+1}&=P_H(\\widetilde w^k-\\widetilde u^k),\\nonumber\\\\\n"
            "\\widehat{\\widetilde v}^{k+1}\n"
            "&=[\\alpha P_H+(1-\\alpha)\\Id]\\widetilde w^k\n"
            "-\\alpha P_H\\widetilde u^k.\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "s^{k+1}=AB_\\alpha s^k,\\qquad\n"
            "A=\\begin{bmatrix}P_G\\\\\\Id-P_G\\end{bmatrix},\\qquad\n"
            "B_\\alpha=\n"
            "\\begin{bmatrix}\n"
            "\\alpha P_H+(1-\\alpha)\\Id&\\Id-\\alpha P_H\n"
            "\\end{bmatrix}.\n"
            "\\]",
            "\\begin{align}\n"
            "s^{k+1}&=AB_\\alpha s^k,\\nonumber\\\\\n"
            "A&=\\begin{bmatrix}P_G\\\\\\Id-P_G\\end{bmatrix},\\nonumber\\\\\n"
            "B_\\alpha&=\n"
            "\\begin{bmatrix}\n"
            "\\alpha P_H+(1-\\alpha)\\Id&\\Id-\\alpha P_H\n"
            "\\end{bmatrix}.\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "z^k=\\widehat{\\widetilde v}^{k+1}+\\widetilde u^k\n"
            "=[\\alpha P_H+(1-\\alpha)\\Id]\\widetilde w^k\n"
            "+(\\Id-\\alpha P_H)\\widetilde u^k.\n"
            "\\]",
            "\\begin{align}\n"
            "z^k&=\\widehat{\\widetilde v}^{k+1}+\\widetilde u^k\\nonumber\\\\\n"
            "&=[\\alpha P_H+(1-\\alpha)\\Id]\\widetilde w^k\n"
            "+(\\Id-\\alpha P_H)\\widetilde u^k.\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "\\theta_{\\min}:=\\min_{\\mathcal R}\\theta\n"
            "=\\min_{c\\in\\operatorname{corners}(\\mathcal R)}\\theta_c,\\qquad\n"
            "\\theta_{\\max}:=\\max_{\\mathcal R}\\theta\n"
            "=\\max_{c\\in\\operatorname{corners}(\\mathcal R)}\\theta_c.\n"
            "\\]",
            "\\begin{align}\n"
            "\\theta_{\\min}&:=\\min_{\\mathcal R}\\theta\n"
            "=\\min_{c\\in\\operatorname{corners}(\\mathcal R)}\\theta_c,\\nonumber\\\\\n"
            "\\theta_{\\max}&:=\\max_{\\mathcal R}\\theta\n"
            "=\\max_{c\\in\\operatorname{corners}(\\mathcal R)}\\theta_c.\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "\\theta_c(\\rho)=\\frac{N_c(\\rho)}{D_c(\\rho)},\\qquad\n"
            "N_c(\\rho)=\\rho^2+p_c,\\quad\n"
            "D_c(\\rho)=\\rho^2+s_c\\rho+p_c,\n"
            "\\]",
            "\\begin{align}\n"
            "\\theta_c(\\rho)&=\\frac{N_c(\\rho)}{D_c(\\rho)},\\nonumber\\\\\n"
            "N_c(\\rho)&=\\rho^2+p_c,\\qquad\n"
            "D_c(\\rho)=\\rho^2+s_c\\rho+p_c.\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "\\phi(t)\\le\n"
            "\\lambda\\phi(\\theta_{\\min})+(1-\\lambda)\\phi(\\theta_{\\max})\n"
            "\\le\\max\\{\\phi(\\theta_{\\min}),\\phi(\\theta_{\\max})\\}.\n"
            "\\]",
            "\\begin{align}\n"
            "\\phi(t)&\\le\n"
            "\\lambda\\phi(\\theta_{\\min})+(1-\\lambda)\\phi(\\theta_{\\max})\\nonumber\\\\\n"
            "&\\le\\max\\{\\phi(\\theta_{\\min}),\\phi(\\theta_{\\max})\\}.\n"
            "\\end{align}",
        ),
        (
            "\\begin{equation}\n"
            "\\frac{\\partial\\theta}{\\partial h}\n"
            "=\\frac{\\rho(g-\\rho)}{(g+\\rho)(h+\\rho)^2},\\qquad\n"
            "\\frac{\\partial\\theta}{\\partial g}\n"
            "=\\frac{\\rho(h-\\rho)}{(h+\\rho)(g+\\rho)^2}.\n"
            "\\label{eq:theta_derivatives}\n"
            "\\end{equation}",
            "\\begin{align}\n"
            "\\frac{\\partial\\theta}{\\partial h}\n"
            "&=\\frac{\\rho(g-\\rho)}{(g+\\rho)(h+\\rho)^2},\\nonumber\\\\\n"
            "\\frac{\\partial\\theta}{\\partial g}\n"
            "&=\\frac{\\rho(h-\\rho)}{(h+\\rho)(g+\\rho)^2}.\n"
            "\\label{eq:theta_derivatives}\n"
            "\\end{align}",
        ),
        (
            "\\[\n"
            "F(\\alpha)=\n"
            "\\max\\{|1-\\alpha(1-a)|,\\ |1-\\alpha(1-b)|\\},\n"
            "\\qquad 0<\\alpha\\le2.\n"
            "\\]",
            "\\begin{equation}\n"
            "F(\\alpha)=\n"
            "\\max\\{|1-\\alpha(1-a)|,\\ |1-\\alpha(1-b)|\\},\n"
            "\\quad 0<\\alpha\\le2.\n"
            "\\end{equation}",
        ),
    ]
    for old, new in wide_repls:
        body = body.replace(old, new)

    return body


def build_main_tex() -> str:
    src = (ROOT / "paper" / "paper.tex").read_text()
    abstract = extract_between(src, "\\begin{abstract}", "\\end{abstract}")
    # Body starts after abstract environment and optional keywords.
    after = src.split("\\end{abstract}", 1)[1]
    after = re.sub(
        r"^\s*\\noindent\\textbf\{Keywords:\}.*?local Fourier analysis\s*",
        "",
        after,
        count=1,
        flags=re.S,
    )
    body = after.rsplit("\\end{document}", 1)[0]
    body = adapt_main_body(body)

    preamble = r"""\documentclass[pdflatex,iicol,sn-mathphys-num]{sn-jnl}

\usepackage{amsmath,amssymb,amsthm,mathtools}
\usepackage{booktabs,array,multirow}
\usepackage{float}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{microtype}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{url}
\usepackage[title]{appendix}

\setlength{\tabcolsep}{3.5pt}
\emergencystretch=2em
\raggedbottom

%% Numbered algorithm floats.
\floatstyle{ruled}
\newfloat{algorithm}{tbp}{loa}
\floatname{algorithm}{Algorithm}

\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{remark}[theorem]{Remark}

\newcommand{\R}{\mathbb{R}}
\newcommand{\norm}[1]{\left\lVert #1\right\rVert}
\newcommand{\spec}{\operatorname{spec}}
\newcommand{\spr}{\varrho}
\newcommand{\diag}{\operatorname{diag}}
\newcommand{\argmin}{\operatorname*{arg\,min}}
\newcommand{\Id}{\mathrm{I}}
\newcommand{\Ufour}{U_{\mathrm{4C}}}
\newcommand{\Ufrozen}{U_{\mathrm{frozen}}}

\title[SHORT_TITLE_PLACEHOLDER]{TITLE_PLACEHOLDER}

\author[1]{\fnm{Katherine} \sur{Xie}}
\author[1]{\fnm{Jie} \sur{Wu}}
\author*[1]{\fnm{Xiaohui} \sur{Xie}}\email{xhx@uci.edu}

\affil*[1]{\orgdiv{Department of Computer Science}, \orgname{University of California, Irvine}, \orgaddress{\city{Irvine}, \state{California}, \country{USA}}}

\abstract{ABSTRACT_PLACEHOLDER}

\keywords{alternating direction method of multipliers, diffeomorphic image registration, parameter selection, spectral analysis, local Fourier analysis}

\pacs[MSC Classification]{65K10, 65F10, 68U10, 90C25, 65T50}

\begin{document}
\maketitle
"""
    preamble = (
        preamble.replace("SHORT_TITLE_PLACEHOLDER", SHORT_TITLE)
        .replace("TITLE_PLACEHOLDER", TITLE)
        .replace("ABSTRACT_PLACEHOLDER", abstract)
    )
    return preamble + body + "\n\\end{document}\n"


def build_supplement_tex() -> str:
    src = (ROOT / "paper" / "supplementary.tex").read_text()
    title = "Supplementary Information for\\\\ " + TITLE
    author = (
        "Katherine Xie\\\\ Jie Wu\\\\ Xiaohui Xie\\\\"
        "Department of Computer Science, University of California, Irvine\\\\"
        "Irvine, California, USA\\\\ Corresponding author: xhx@uci.edu"
    )
    # Use callables so re.sub does not reinterpret \\t / \\a escapes.
    src = re.sub(
        r"\\title\{(?:[^{}]|\{[^{}]*\})*\}",
        lambda _m: "\\title{" + title + "}",
        src,
        count=1,
    )
    src = re.sub(
        r"\\author\{(?:[^{}]|\{[^{}]*\})*\}",
        lambda _m: "\\author{" + author + "}",
        src,
        count=1,
    )
    src = src.replace("\\date{}", "\\date{Journal of Mathematical Imaging and Vision}")
    src = src.replace(
        "../figures/certificate_behavior.pdf",
        "FigS1_certificate_behavior.pdf",
    )
    return src


def build_cover_letter() -> tuple[str, str]:
    letter = (
        "Dear Editors,\n\n"
        f"Please consider our manuscript, “{TITLE},” for publication as a "
        "Regular Paper in the Journal of Mathematical Imaging and Vision.\n\n"
        "Selecting the penalty and relaxation parameters of over-relaxed ADMM "
        "(oADMM) can require repeated spectral-radius evaluation of a large "
        "iteration operator. For quadratic splits whose attained joint modal "
        "spectrum is a Cartesian product of data and regularizer curvatures, "
        "we show that the worst modal contraction is attained among only four "
        "endpoint combinations. Analytic relaxation and a finite algebraic "
        "candidate set then replace grid-based or iterative penalty search.\n\n"
        "Diffeomorphic image registration provides the motivating noncommuting "
        "application: the assembled optical-flow Hessian varies spatially, while "
        "the Sobolev regularizer couples neighboring pixels. The exact "
        "four-corner theorem therefore does not apply to the full operator. A "
        "family of globally coefficient-frozen surrogates indexed by the local "
        "optical-flow Hessian blocks, together with the rank-one data Hessian, "
        "nevertheless yields an inexpensive one-shot predictor determined by "
        "four endpoint curvatures.\n\n"
        "On all 134 FIRE retinal pairs at 256×256, one-shot four-corner tuning "
        "reduced median pairwise runtime by 34.4% and inner iterations by 39.6% "
        "relative to a validation-selected fixed comparator chosen on separate "
        "images, while landmark accuracy was essentially unchanged and no "
        "nonpositive discrete Jacobian was observed. On ten CIMA histology "
        "pairs, matched-protocol runtime decreased by 20.1%. Supplementary "
        "Information contains certificate constructions, implementation "
        "details, and additional diagnostics.\n\n"
        "We believe the manuscript is well suited to JMIV. It combines a "
        "structural spectral analysis of operator splitting with a concrete "
        "variational imaging application and reproducible evaluation on public "
        "registration benchmarks. The approach is complementary to general "
        "numerical spectral ADMM optimization: stronger modal assumptions "
        "yield an exact four-corner reduction and a practical predictor for "
        "spatially varying registration.\n\n"
        "Source code, processed outputs, and preparation and evaluation "
        "scripts are available at https://github.com/xhxuciedu/admm.\n\n"
        "The authors confirm that this work is original, unpublished, and not "
        "under consideration elsewhere, and that it does not extend a prior "
        "conference paper. There is no specific funding and no competing "
        "interest.\n\n"
        "Thank you for considering our manuscript.\n\n"
        "Sincerely,\n\n"
        "Xiaohui Xie\n"
        "Department of Computer Science\n"
        "University of California, Irvine\n"
        "Irvine, California, USA\n"
        "xhx@uci.edu\n"
    )
    letter_tex = r"""\documentclass[11pt]{letter}
\usepackage[margin=1in]{geometry}
\usepackage[hidelinks]{hyperref}
\usepackage{url}
\setlength{\parskip}{0.85em}
\setlength{\parindent}{0pt}
\begin{document}

Dear Editors,

Please consider our manuscript, ``TITLE_PLACEHOLDER,'' for publication as a Regular Paper in the \emph{Journal of Mathematical Imaging and Vision}.

Selecting the penalty and relaxation parameters of over-relaxed ADMM (oADMM) can require repeated spectral-radius evaluation of a large iteration operator. For quadratic splits whose attained joint modal spectrum is a Cartesian product of data and regularizer curvatures, we show that the worst modal contraction is attained among only four endpoint combinations. Analytic relaxation and a finite algebraic candidate set then replace grid-based or iterative penalty search.

Diffeomorphic image registration provides the motivating noncommuting application: the assembled optical-flow Hessian varies spatially, while the Sobolev regularizer couples neighboring pixels. The exact four-corner theorem therefore does not apply to the full operator. A family of globally coefficient-frozen surrogates indexed by the local optical-flow Hessian blocks, together with the rank-one data Hessian, nevertheless yields an inexpensive one-shot predictor determined by four endpoint curvatures.

On all 134 FIRE retinal pairs at $256\times256$, one-shot four-corner tuning reduced median pairwise runtime by 34.4\% and inner iterations by 39.6\% relative to a validation-selected fixed comparator chosen on separate images, while landmark accuracy was essentially unchanged and no nonpositive discrete Jacobian was observed. On ten CIMA histology pairs, matched-protocol runtime decreased by 20.1\%. Supplementary Information contains certificate constructions, implementation details, and additional diagnostics.

We believe the manuscript is well suited to JMIV. It combines a structural spectral analysis of operator splitting with a concrete variational imaging application and reproducible evaluation on public registration benchmarks. The approach is complementary to general numerical spectral ADMM optimization: stronger modal assumptions yield an exact four-corner reduction and a practical predictor for spatially varying registration.

Source code, processed outputs, and preparation and evaluation scripts are available at \url{https://github.com/xhxuciedu/admm}.

The authors confirm that this work is original, unpublished, and not under consideration elsewhere, and that it does not extend a prior conference paper. There is no specific funding and no competing interest.

Thank you for considering our manuscript.

Sincerely,\\[1.25em]
Xiaohui Xie\\
Department of Computer Science\\
University of California, Irvine\\
Irvine, California, USA\\
\href{mailto:xhx@uci.edu}{xhx@uci.edu}

\end{document}
""".replace("TITLE_PLACEHOLDER", TITLE)
    return letter, letter_tex


def update_docs(abstract_words: int) -> None:
    readme = f"""# JMIV submission package

Self-contained Springer Nature package for the
*Journal of Mathematical Imaging and Vision* (JMIV), synced from `paper/`.

## Layout

- `main/`: compilable two-column (`iicol`) manuscript source, class file,
  bibliography, figures, and PDF.
- `supplement/`: Online Resource 1 (Supplementary Information) source and PDF.
- `figures/`: vector PDF figures used by the main manuscript.
- `cover_letter/`: cover letter (`.txt`, `.tex`, `.pdf`).
- `template_original/`: unmodified official Springer Nature template.
- `JMIV_main_source.zip`: flat editable-source archive for SNAPP upload.

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

Complete `JMIV_SUBMISSION_TODO.md` and `JMIV_submission_checklist.md` before
portal submission.
"""
    write(OUT / "README_JMIV_SUBMISSION.md", readme)

    meta = f"""# JMIV submission metadata

| Field | Value |
|---|---|
| Journal | *Journal of Mathematical Imaging and Vision* |
| Article type | Regular Paper |
| Title | {TITLE} |
| Authors | Katherine Xie, Jie Wu, Xiaohui Xie (corresponding) |
| Affiliation | Department of Computer Science, University of California, Irvine, Irvine, California, USA |
| Corresponding e-mail | xhx@uci.edu |
| Corresponding telephone | Enter privately in SNAPP; not stored in this repository. |
| Fax | Not applicable |
| ORCID | Enter privately in SNAPP; not stored in this repository. |
| Abstract word count | {abstract_words} (JMIV guideline is 100--150; current abstract matches `paper/paper.tex` verbatim and may need a portal-length condensation) |
| MSC classification | 65K10, 65F10, 68U10, 90C25, 65T50 |
| Keywords | alternating direction method of multipliers; diffeomorphic image registration; parameter selection; spectral analysis; local Fourier analysis |
| Main manuscript | `main/JMIV_main.pdf` |
| Supplement | `supplement/ESM_1_Supplementary_Information.pdf` (Online Resource 1) |
| Source archive | `JMIV_main_source.zip` |
| Data/code statement | https://github.com/xhxuciedu/admm |
| Funding | No specific funding. |
| Competing interests | The authors declare no competing interests. |
| Author contributions | Katherine Xie and Jie Wu conducted the research and wrote and edited the manuscript. Xiaohui Xie conceived the work and edited the manuscript. |
| Originality/exclusivity | Confirmed: original, unpublished, and not under review elsewhere. |
| Third-party permissions | Confirmed: none required. |
| Prior conference paper | None. |
| Reviewer suggestions | None. |

Enter these confirmed values in SNAPP. Remaining portal-only checks are listed
in `JMIV_SUBMISSION_TODO.md`.
"""
    write(OUT / "JMIV_submission_metadata.md", meta)

    checklist = """# Final JMIV upload checklist

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
"""
    write(OUT / "JMIV_submission_checklist.md", checklist)

    requirements = """# JMIV submission requirements audit

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
`\\documentclass[pdflatex,iicol,sn-mathphys-num]{sn-jnl}`.

## Notes

SNAPP may fail on nested source directories; the upload ZIP is deliberately flat.
"""
    write(OUT / "JMIV_requirements.md", requirements)


def build() -> None:
    # Remove redundant upload/ tree if present.
    upload = OUT / "upload"
    if upload.exists():
        shutil.rmtree(upload)

    for d in (MAIN, SUPP, FIG, COVER):
        d.mkdir(parents=True, exist_ok=True)

    # Clean stale aux from previous divergent manuscript if needed.
    for pat in ("JMIV_main.*",):
        for p in MAIN.glob(pat):
            if p.suffix in {".tex", ".pdf", ".cls"}:
                continue
            if p.name.startswith("Fig"):
                continue
            p.unlink(missing_ok=True)

    abstract = extract_between(
        (ROOT / "paper" / "paper.tex").read_text(),
        "\\begin{abstract}",
        "\\end{abstract}",
    )
    abstract_words = len(re.findall(r"[A-Za-z0-9']+", abstract))

    write(MAIN / "JMIV_main.tex", build_main_tex())
    shutil.copy2(ROOT / "figures" / "algebraic_validation.pdf", MAIN / "Fig1.pdf")
    shutil.copy2(ROOT / "figures" / "fire256_headline.pdf", MAIN / "Fig2.pdf")
    shutil.copy2(MAIN / "Fig1.pdf", FIG / "Fig1.pdf")
    shutil.copy2(MAIN / "Fig2.pdf", FIG / "Fig2.pdf")
    shutil.copy2(TEMPLATE / "sn-jnl.cls", MAIN / "sn-jnl.cls")
    shutil.copy2(
        TEMPLATE / "bst" / "sn-mathphys-num.bst",
        MAIN / "sn-mathphys-num.bst",
    )
    shutil.copy2(ROOT / "paper" / "references.bib", MAIN / "references.bib")

    # Supplement
    write(SUPP / "ESM_1_Supplementary_Information.tex", build_supplement_tex())
    shutil.copy2(
        ROOT / "figures" / "certificate_behavior.pdf",
        SUPP / "FigS1_certificate_behavior.pdf",
    )

    # Cover letter
    letter, letter_tex = build_cover_letter()
    write(COVER / "JMIV_cover_letter.txt", letter)
    write(COVER / "JMIV_cover_letter.tex", letter_tex)

    update_docs(abstract_words)

    # Compile
    run_latex(MAIN, "JMIV_main.tex", bibtex=True)
    run_latex(SUPP, "ESM_1_Supplementary_Information.tex", runs=2)
    run_latex(COVER, "JMIV_cover_letter.tex", runs=1)

    # Flat source ZIP at JMIV root (no upload/ mirror).
    zip_path = OUT / "JMIV_main_source.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in (
            "JMIV_main.tex",
            "sn-jnl.cls",
            "sn-mathphys-num.bst",
            "references.bib",
            "Fig1.pdf",
            "Fig2.pdf",
        ):
            zf.write(MAIN / name, name)

    esm_zip = OUT / "ESM_1_source.zip"
    if esm_zip.exists():
        esm_zip.unlink()
    with zipfile.ZipFile(esm_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(SUPP / "ESM_1_Supplementary_Information.tex", "ESM_1_Supplementary_Information.tex")
        zf.write(
            SUPP / "FigS1_certificate_behavior.pdf",
            "FigS1_certificate_behavior.pdf",
        )

    # Local build helper only; do not leave in the submission tree.
    (MAIN / "array.sty").unlink(missing_ok=True)
    (SUPP / "array.sty").unlink(missing_ok=True)

    print(f"Built {OUT}")
    print(f"Abstract words: {abstract_words}")
    print(f"Source zip: {zip_path}")
    print(f"ESM source zip: {esm_zip}")


if __name__ == "__main__":
    build()
