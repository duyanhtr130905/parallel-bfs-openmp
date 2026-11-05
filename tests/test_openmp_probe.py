"""Verify real probe success and constrained-runtime rejection in subprocesses."""
import os
from pathlib import Path
import subprocess
import sys

binary = str(Path(sys.argv[1]).resolve())
for mode, limit, expected in [("--strict", "2", 0), ("--strict", "1", 1),
                              ("--basic", "1", 0), ("--invalid", "2", 2)]:
    env = dict(os.environ, OMP_THREAD_LIMIT=limit, OMP_DYNAMIC="FALSE")
    result = subprocess.run([binary, mode], env=env, capture_output=True, text=True)
    assert result.returncode == expected, (mode, limit, result)
    if expected == 0:
        assert f"team={limit} " in result.stdout, result.stdout
print("PASS: strict two-thread probe; one-thread strict rejection; basic; invalid mode")
