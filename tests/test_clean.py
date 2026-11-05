"""Exercise bounded cleanup in an isolated temporary tree, preserving sources/PDF."""
from pathlib import Path
import runpy
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(dir=root / 'build') as directory:
    sandbox = Path(directory)
    (sandbox / 'scripts').mkdir()
    (sandbox / 'report/chapters').mkdir(parents=True)
    (sandbox / 'build').mkdir()
    script = sandbox / 'scripts/clean.py'
    script.write_bytes((root / 'scripts/clean.py').read_bytes())
    deleted = ['report/main.aux', 'report/chapters/chapter1.log',
               'report/chapters/chapter6.aux', 'build/openmp_probe.exe']
    kept = ['report/main.pdf', 'report/main.tex', 'report/references.bib',
            'report/chapters/chapter1.tex', 'report/chapters/custom.aux']
    for name in deleted + kept:
        (sandbox / name).write_text('cleanup fixture', encoding='utf-8')
    runpy.run_path(str(script), run_name='__main__')
    assert all(not (sandbox / p).exists() for p in deleted)
    assert all((sandbox / p).read_text(encoding='utf-8') == 'cleanup fixture'
               for p in kept)
print('PASS: named auxiliary cleanup preserves PDF, TeX, BibTeX and unknown files')
