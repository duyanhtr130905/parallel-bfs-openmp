"""Remove only known build outputs; preserve all PDFs and report sources."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
names = [
    'build/bfs', 'build/bfs.exe',
    'build/test_graph', 'build/test_graph.exe',
    'build/test_serial', 'build/test_serial.exe',
    'build/openmp_probe', 'build/openmp_probe.exe',
]
suffixes = ('aux', 'log', 'toc', 'lof', 'lot', 'out', 'bbl', 'blg',
            'fls', 'fdb_latexmk', 'synctex.gz')
names += ['report/main.' + suffix for suffix in suffixes]
names += [f'report/chapters/chapter{i}.' + suffix
          for i in range(1, 7) for suffix in suffixes]
for name in names:
    target = root / name
    # Reject junction/symlink ancestors and keep deletion within the exact root.
    if any(p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction())
           for p in (target, *target.parents) if p != root):
        continue
    if target.resolve().is_relative_to(root) and target.is_file():
        target.unlink()
