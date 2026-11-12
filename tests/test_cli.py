"""Real serial CLI integration; smoke timings are not benchmark results."""
import argparse
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchmark import validate
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--binary', required=True)
binary = str(Path(p.parse_args().binary).resolve())
if not Path(binary).is_file():
    raise SystemExit('NOT RUN: build the CLI first')
base = ['--graph', 'datasets/small/disconnected.edgelist', '--vertices', '6',
        '--source', '0', '--algo', 'serial', '--directed']
cases = [(['--help'], 0), ([], 2), (base, 0)]
for algo in ('serial', 'omp-basic', 'omp-opt'):
    for schedule in ('static', 'dynamic', 'guided'):
        args = base.copy()
        args[7] = algo
        cases.append((args + ['--threads', '2', '--schedule', schedule], 0 if algo == 'serial' else 3))
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
cases.append((args, 0))
cases.append((base[:-1], 2))
for args, expected in cases:
    result = subprocess.run([binary, *args], capture_output=True, text=True, timeout=10)
    assert result.returncode == expected, (args, result.returncode, result.stderr)
    if expected != 0:
        assert result.stdout == '', (args, result.stdout)
        assert result.stderr, args
    if expected == 0 and args != ['--help']:
        record = validate(result.stdout)
        assert record['algorithm'] == 'serial'
        assert record['vertices'] == 6 and record['edges'] == (5 if '--directed' in args else 9)
        assert record['reachable'] == 4 and record['source'] == 0
        assert record['threads_requested'] == (2 if '--threads' in args else 1)
        assert result.stderr == ''
    if expected == 3:
        assert 'NOT_IMPLEMENTED' in result.stderr, args
# Temporary edge files are integration fixtures, never research raw data.
extra_count = 0
with tempfile.TemporaryDirectory(prefix='bfs-cli-') as directory:
    path = Path(directory) / 'graph with spaces.txt'
    for data, vertices, source, mode, expected, arcs, reachable in (
        (b'', 1, 0, '--directed', 0, 0, 1),
        (b'', 3, 2, '--undirected', 0, 0, 1),
        (b'# fixture\r\n0 1\r\n1 2', 4, 2, '--directed', 0, 2, 1),
        (b'0 1\n1 2\n2 2\n0 1', 4, 2, '--undirected', 0, 7, 3),
        (b'0 1\x00 2\n', 3, 0, '--directed', 4, None, None),
        (b'4294967296 0', 3, 0, '--directed', 4, None, None),
        (b'0 1 # tail', 3, 0, '--directed', 4, None, None),
        (b'0 3', 3, 0, '--directed', 4, None, None),
        (b'\xef\xbb\xbf0 1', 3, 0, '--directed', 4, None, None),
    ):
        path.write_bytes(data)
        args = ['--graph', str(path), '--vertices', str(vertices), '--source', str(source),
                '--algo', 'serial', mode, '--threads', '4', '--schedule', 'guided']
        result = subprocess.run([binary, *args], capture_output=True, text=True, timeout=10)
        assert result.returncode == expected, (args, result.stderr)
        if expected == 0:
            validate(result.stdout, dict(vertices=vertices, source=source, edges=arcs,
                reachable=reachable, directed=mode == '--directed', threads_requested=4))
            assert not result.stderr
        else:
            assert not result.stdout and result.stderr
        extra_count += 1
    args[1] = str(Path(directory) / 'missing.txt')
    result = subprocess.run([binary, *args], capture_output=True, text=True, timeout=10)
    assert result.returncode == 4 and not result.stdout and result.stderr
    extra_count += 1
print(f'PASS: {len(cases) + extra_count} CLI cases; serial integration only, no comparison benchmark')
