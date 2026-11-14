"""Test-only fault backend verifies that failed BFS never publishes JSONL."""
import os
from pathlib import Path
import subprocess
import sys

binary = str(Path(sys.argv[1]).resolve())
for algo in ('serial', 'omp-basic', 'omp-opt'):
    for fault in ('memory', 'runtime', 'unimplemented', 'metrics', 'distance'):
        env = dict(os.environ, BFS_TEST_FAULT=fault)
        result = subprocess.run([binary, '--graph', 'datasets/small/disconnected.edgelist',
            '--vertices', '6', '--source', '0', '--algo', algo, '--directed'],
            capture_output=True, env=env, timeout=10)
        assert result.returncode == (3 if fault == 'unimplemented' else 4), (algo, fault, result)
        assert not result.stdout and result.stderr, (algo, fault, result)
print('PASS: 15 fault cases; BFS errors, invalid metrics/distance emit no result')
