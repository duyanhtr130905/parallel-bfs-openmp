"""Check report dependencies and fixture oracle without claiming BFS execution."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
required = ['include/graph.h', 'include/bfs.h', 'include/status.h', 'src/main.c',
            'docs/CONTRACT.md', 'docs/ARCHITECTURE.md', 'docs/CONTRIBUTING.md',
            'docs/EXPERIMENT_PROTOCOL.md', 'report/references.bib', 'Makefile']
for name in required:
    assert (root / name).is_file(), name
main = (root / 'report/main.tex').read_text(encoding='utf-8')
includes = re.findall(r'\\include\{([^}]+)\}', main)
assert len(includes) == 6
for name in includes:
    assert (root / 'report' / (name + '.tex')).is_file(), name
bib = (root / 'report/references.bib').read_text(encoding='utf-8')
keys = set(re.findall(r'@\w+\{([^,]+),', bib))
for tex in (root / 'report').rglob('*.tex'):
    for group in re.findall(r'\\(?:cite|nocite)\{([^}]+)\}', tex.read_text(encoding='utf-8')):
        assert set(group.split(',')) <= keys, (tex, group)
oracle = (root / 'datasets/small/disconnected.expected.txt').read_text().split()
assert oracle == ['0', '1', '1', '2', '-1', '-1']
print('PASS: scaffold dependencies and hand-specified fixture checked; C/BFS/LaTeX NOT executed')

header = (root / 'include/bfs.h').read_text(encoding='utf-8')
contract = (root / 'docs/CONTRACT.md').read_text(encoding='utf-8')
pattern = r'BFSStatus\s+(bfs_\w+)\s*\(([^;]+)\);'
normalize = lambda value: re.sub(r'\s+', '', value)
header_api = {name: normalize(args) for name, args in re.findall(pattern, header)}
contract_api = {name: normalize(args) for name, args in re.findall(pattern, contract)}
assert len(header_api) == 3 and header_api == contract_api, 'BFS signatures differ'
assert all(args.endswith('BFSMetrics*metrics') for args in header_api.values())
print('PASS: header/CONTRACT metrics signatures agree; no BFS executed')
