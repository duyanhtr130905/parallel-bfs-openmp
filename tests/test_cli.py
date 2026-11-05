"""Real CLI contract checks; never BFS correctness/performance evidence."""
import argparse
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--binary', required=True)
binary = str(Path(p.parse_args().binary).resolve())
if not Path(binary).is_file():
    raise SystemExit('NOT RUN: build the CLI first')
base = ['--graph', 'datasets/small/disconnected.edgelist', '--vertices', '6',
        '--source', '0', '--algo', 'serial', '--directed']
cases = [(['--help'], 0), ([], 2), (base, 3)]
for algo in ('serial', 'omp-basic', 'omp-opt'):
    for schedule in ('static', 'dynamic', 'guided'):
        args = base.copy()
        args[7] = algo
        cases.append((args + ['--threads', '2', '--schedule', schedule], 3))
for extra in (['--directed'], ['--undirected'], ['--unknown'], ['--help'],
              ['--threads', '0'], ['--threads', '-1'], ['--threads', '2147483648'],
              ['--threads', '2x'], ['--schedule', 'auto'], ['--threads']):
    cases.append((base + extra, 2))
for index, value in ((3, '0'), (3, '2147483648'), (3, '-1'), (5, '6'),
                     (5, '4294967296'), (7, 'unknown'), (1, '')):
    args = base.copy()
    args[index] = value
    cases.append((args, 2))
args = base.copy()
args[-1] = '--undirected'
cases.append((args, 3))
cases.append((base[:-1], 2))
for args, expected in cases:
    result = subprocess.run([binary, *args], capture_output=True, text=True, timeout=10)
    assert result.returncode == expected, (args, result.returncode, result.stderr)
    if expected != 0:
        assert result.stdout == '', (args, result.stdout)
        assert result.stderr, args
    if expected == 3:
        assert 'NOT_IMPLEMENTED' in result.stderr, args
print(f'PASS: {len(cases)} CLI cases; BFS correctness/performance NOT TESTED')
