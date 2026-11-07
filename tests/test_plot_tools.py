"""Optional matplotlib smoke test: SYNTHETIC ONLY, never report data."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from plot_results import plot
from analyze_results import aggregate
from test_experiment_tools import synthetic


class PlotTest(unittest.TestCase):
    def test_four_figures(self):
        records=[synthetic() for _ in range(10)]
        for algo in ('omp-basic','omp-opt'):
            for p in (1,2):
                for schedule in ('static','dynamic','guided'):
                    records.extend(synthetic(algorithm=algo,threads_requested=p,threads_actual=p,schedule=schedule) for _ in range(10))
        summary=dict(dataset=dict(kind='SYNTHETIC TEST ONLY',vertices=4),environment=dict(source=0),commit='test-only',rows=aggregate(records))
        with tempfile.TemporaryDirectory() as t,patch('plot_results.analyze',return_value=summary):
            out=Path(t)/'figures'
            plot('unused test input',out)
            self.assertEqual(len(list(out.glob('*.pdf'))),4)
            for f in out.glob('*.pdf'):
                self.assertTrue(f.read_bytes().startswith(b'%PDF'))
            self.assertEqual(json.loads((out/'provenance.json').read_text())['commit'],'test-only')
            with self.assertRaises(FileExistsError):plot('unused',out)


if __name__=='__main__':unittest.main()
