"""Optional matplotlib smoke test: SYNTHETIC ONLY, never report data."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from plot_results import plot, scheduling_groups
from analyze_results import aggregate
from test_experiment_tools import synthetic


class PlotTest(unittest.TestCase):
    def test_scheduling_uses_actual_team(self):
        rows = [synthetic(algorithm='omp-basic', threads_requested=p,
                          threads_actual=2, schedule=s)
                for p,s in ((2,'static'),(4,'dynamic'),(8,'guided'))]
        groups = scheduling_groups(rows)
        self.assertEqual(groups[0][0], ('omp-basic', 2))
        self.assertEqual(set(groups[0][1]), {'static','dynamic','guided'})
        with self.assertRaises(ValueError): scheduling_groups(rows+[rows[0]])

    def test_four_figures(self):
        records=[synthetic() for _ in range(10)]
        for algo in ('omp-basic','omp-opt'):
            for p in (1,2):
                for schedule in ('static','dynamic','guided'):
                    records.extend(synthetic(algorithm=algo,threads_requested=p,threads_actual=p,schedule=schedule) for _ in range(10))
        summary=dict(dataset=dict(kind='SYNTHETIC TEST ONLY',vertices=4),environment=dict(source=0),commit='test-only',rows=aggregate(records))
        with tempfile.TemporaryDirectory() as t,patch('plot_results.analyze',return_value=summary):
            out=Path(t)/'figures'
            from matplotlib.axes import Axes
            original_plot = Axes.plot
            calls = []
            def capture(ax, *args, **kwargs):
                calls.append((args, kwargs))
                return original_plot(ax, *args, **kwargs)
            with patch.object(Axes, 'plot', capture):
                plot('unused test input',out)
            ideal = [args for args,kw in calls if kw.get('label') == 'Ideal S=p']
            self.assertEqual(len(ideal), 1)
            self.assertEqual(ideal[0][0], [1,2])
            self.assertEqual(ideal[0][0], ideal[0][1])
            self.assertEqual(len(list(out.glob('*.pdf'))),4)
            for f in out.glob('*.pdf'):
                self.assertTrue(f.read_bytes().startswith(b'%PDF'))
            self.assertEqual(json.loads((out/'provenance.json').read_text())['commit'],'test-only')
            with self.assertRaises(FileExistsError):plot('unused',out)


if __name__=='__main__':unittest.main()
