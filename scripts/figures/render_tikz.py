"""Build the TikZ diagrams as standalone vector PDFs."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parents[1] / "report/figures"
DIAGRAMS = ("bfs-example", "csr-example", "frontier-design")
PREAMBLE = r"""\documentclass[tikz,border=3pt,12pt]{standalone}
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\usetikzlibrary{arrows.meta,positioning,calc}
\begin{document}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xelatex", default="xelatex", help="XeLaTeX executable")
    parser.add_argument("--tectonic", help="use the Tectonic XeTeX-based engine instead")
    parser.add_argument("--bundle", type=Path, help="local Tectonic resource bundle")
    args = parser.parse_args()
    if args.bundle and not args.tectonic:
        parser.error("--bundle requires --tectonic")
    if args.tectonic:
        compiler = [str(Path(args.tectonic).resolve()), "--untrusted"]
        if args.bundle:
            compiler += ["-b", args.bundle.resolve().as_uri()]
    else:
        xelatex = shutil.which(args.xelatex)
        if not xelatex:
            parser.error(f"Cannot locate XeLaTeX executable: {args.xelatex}")
        compiler = [xelatex, "-halt-on-error", "-interaction=nonstopmode", "-file-line-error"]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bfs-tikz-", dir=os.getenv("TMP")) as temp:
        directory = Path(temp)
        for diagram in DIAGRAMS:
            tex = directory / f"{diagram}.tex"
            body = (HERE / tex.name).read_text(encoding="utf-8")
            tex.write_text(PREAMBLE + body + r"\end{document}" + "\n", encoding="utf-8")
            subprocess.run([*compiler, tex.name], cwd=directory, check=True)
            shutil.copyfile(tex.with_suffix(".pdf"), OUTPUT / tex.with_suffix(".pdf").name)


if __name__ == "__main__":
    main()

