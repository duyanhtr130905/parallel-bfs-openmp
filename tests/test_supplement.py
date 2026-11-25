import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_supplement import edges
from summarize_supplement import load_profile, load_samples, summarize, tables, plots

SESSION = ROOT / "results/experiment-20261125"
PLAN = json.loads((SESSION / "plan.json").read_text(encoding="utf-8"))


class SupplementTests(unittest.TestCase):
    def test_generator_without_duplicate_or_loop(self):
        graphs = [
            dict(kind="grid", n=24, width=4),
            dict(kind="random", n=27, degree=6, seed=3),
            dict(kind="layered", n=97, width=32, degree=4, seed=4, overlap=True),
            dict(kind="layered", n=97, width=32, degree=4, seed=4, overlap=False),
        ]
        for graph in graphs:
            with self.subTest(graph=graph):
                rows = list(edges(graph))
                self.assertEqual(rows, list(edges(graph)))
                self.assertEqual(len(rows), len(set(rows)))
                self.assertTrue(all(0 <= u < graph["n"] and 0 <= v < graph["n"] and u != v
                                    for u, v in rows))

    def test_reject_bad_rows(self):
        with (SESSION / "path513.csv").open(newline="", encoding="ascii") as source:
            rows = list(csv.reader(source))
        changes = {"missing": rows[:-1], "duplicate": rows[:-1] + [rows[-2]]}
        for field, value in [("actual", "99"), ("ms", "nan"), ("validated", "0")]:
            altered = [row[:] for row in rows]
            altered[3][rows[0].index(field)] = value
            changes[field] = altered
        wrong_unit = [row[:] for row in rows]
        wrong_unit[0][rows[0].index("ms")] = "seconds"
        changes["unit"] = wrong_unit
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.csv"
            for fault, samples in changes.items():
                with self.subTest(fault=fault), path.open("w", newline="", encoding="ascii") as out:
                    csv.writer(out).writerows(samples)
                    out.flush()
                    with self.assertRaises(ValueError):
                        load_samples(path, PLAN)

    def test_manifest_and_publication(self):
        results = summarize(SESSION)
        self.assertEqual(len(results), 6)
        self.assertEqual(results[2]["reachable"], 16384)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tables(results, root)
            for file in root.glob("*.tex"):
                self.assertEqual(file.read_bytes(), (ROOT / "report/generated" / file.name).read_bytes())
            plots(results, root)
            for name in ("supplement-performance.pdf", "supplement-frontier.pdf"):
                self.assertTrue((root / name).read_bytes().startswith(b"%PDF-"))
            shutil.copytree(SESSION, root / "input")
            path = root / "input" / "plan.json"
            plan = dict(PLAN, source=1)
            path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported protocol"):
                summarize(root / "input")

    def test_small_directed_and_undirected_oracle(self):
        binary = ROOT / "build" / ("benchmark_supplement.exe" if os.name == "nt"
                                    else "benchmark_supplement")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture = root / "diamond.edges"
            fixture.write_text("0 1\n0 2\n1 3\n2 3\n4 3\n", encoding="ascii")
            for mode, width in [("directed", [1, 2, 1]), ("undirected", [1, 2, 1, 1])]:
                with self.subTest(mode=mode):
                    csv_path, profile = root / "raw.csv", root / "graph.profile"
                    with csv_path.open("wb") as samples, profile.open("wb") as shape:
                        subprocess.run([str(binary), str(fixture), "6", mode, "2"],
                                       stdout=samples, stderr=shape, check=True, timeout=30)
                    groups = load_samples(csv_path, dict(PLAN, omp_threads=2))
                    self.assertTrue(all(len(values) == 12 for values in groups.values()))
                    self.assertEqual(load_profile(profile, dict(n=6, direction=mode), 5)[2], width)
