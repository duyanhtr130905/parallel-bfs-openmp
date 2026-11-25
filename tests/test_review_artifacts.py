import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from review_artifacts import comparison, scaling, scaling_samples, scaling_artifacts

SESSION = ROOT / "results/experiment-scaling-20261125"


class ReviewTests(unittest.TestCase):
    def test_old_and_new_table_totals(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            self.assertEqual(comparison(out), {"serial": 7, "omp-opt": 5})
            for day in ("24", "25"):
                self.assertEqual(len((out / f"statistics-{day}.tex").read_text(
                    encoding="utf-8").splitlines()), 19)
            self.assertEqual((out / "comparison.tex").read_bytes(),
                             (ROOT / "report/generated/comparison.tex").read_bytes())

    def test_scaling_data_and_ratios(self):
        data = scaling(SESSION)
        self.assertEqual(sum(len(graph) for graph in data.values()), 33)
        self.assertTrue(all(item["n"] == 12 for graph in data.values() for item in graph.values()))
        graph = data["layered-permuted"]
        item = graph["omp-opt", 12]
        self.assertAlmostEqual(item["speedup"], graph["serial", 1]["median"] / item["median"])
        self.assertAlmostEqual(item["efficiency"], item["speedup"] / 12)
        self.assertAlmostEqual(item["internal"], graph["omp-opt", 1]["median"] / item["median"])
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            scaling_artifacts(data, target, target)
            self.assertTrue((target / "thread-scaling.pdf").read_bytes().startswith(b"%PDF-"))
            for index in range(1, 4):
                self.assertEqual(len((target / f"scaling-detail-{index}.tex").read_text().splitlines()), 12)

    def test_bad_scaling_samples(self):
        with (SESSION / "path513.csv").open(newline="", encoding="ascii") as stream:
            rows = list(csv.reader(stream))
        bad = {"missing": rows[:-1], "duplicate": rows[:-1] + [rows[-2]]}
        for field, value in [("actual", "99"), ("ms", "NaN"), ("validated", "0")]:
            altered = [row[:] for row in rows]
            altered[-1][rows[0].index(field)] = value
            bad[field] = altered
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "raw.csv"
            for fault, data in bad.items():
                with self.subTest(fault=fault):
                    with path.open("w", newline="", encoding="ascii") as stream:
                        csv.writer(stream).writerows(data)
                    with self.assertRaises(ValueError):
                        scaling_samples(path)

    def test_scaling_driver_on_small_graph(self):
        exe = ROOT / "build" / ("benchmark_scaling.exe" if os.name == "nt" else "benchmark_scaling")
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            graph = directory / "fixture.edges"
            graph.write_text("0 1\n0 2\n1 3\n2 3\n", encoding="ascii")
            raw = directory / "raw.csv"
            with raw.open("wb") as stream:
                subprocess.run([str(exe), str(graph), "5", "directed"],
                               stdout=stream, stderr=subprocess.PIPE, check=True, timeout=45)
            self.assertEqual(len(scaling_samples(raw)), 11)
