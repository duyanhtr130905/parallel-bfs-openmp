"""Delete only explicitly named generated files; no recursive deletion."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
names = ['build/bfs', 'build/bfs.exe', 'build/openmp_probe', 'build/openmp_probe.exe']
names += ['report/main.' + suffix for suffix in
          ('aux', 'log', 'toc', 'lof', 'lot', 'out', 'bbl', 'blg', 'pdf')]
for name in names:
    target = root / name
    if target.is_file() and not target.is_symlink():
        target.unlink()
