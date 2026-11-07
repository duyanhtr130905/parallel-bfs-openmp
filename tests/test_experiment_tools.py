"""SYNTHETIC TEST DATA ONLY. Not experimental measurements or report results."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import subprocess
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from benchmark import validate, run
from generate_graph import generate, sha256
from analyze_results import summarize, aggregate, analyze


def synthetic(**changes):
    r=dict(schema_version=1,status='ok',algorithm='serial',runtime_seconds=2.,
           threads_requested=1,threads_actual=1,schedule='none',vertices=4,edges=3,
           source=0,reachable=4,directed=True)
    r.update(changes)
    return r


class ToolsTests(unittest.TestCase):
    def test_schema_rejections(self):
        for key,value in [('schema_version',True),('status','error'),('algorithm','x'),
                          ('runtime_seconds',-1),('runtime_seconds',float('nan')),
                          ('runtime_seconds',float('inf')),('runtime_seconds',True),('runtime_seconds',10**400),
                          ('threads_actual',0),('threads_requested',False),('vertices',0),
                          ('edges',-1),('source',4),('reachable',5),('directed',1),('schedule','static')]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                validate(json.dumps(synthetic(**{key:value})))
        r=synthetic();del r['edges']
        for text in [json.dumps(r),'{}','[]','not json',json.dumps(synthetic())+'\n{}',
                     json.dumps(synthetic())[:-1]+',"status":"ok"}']:
            with self.assertRaises(ValueError):validate(text)
        with self.assertRaises(ValueError):validate(json.dumps(synthetic()),{'source':1})
        self.assertEqual(validate(json.dumps(synthetic()))['reachable'],4)

    def test_generator(self):
        with tempfile.TemporaryDirectory() as t:
            for kind,kw,n,edges in [('path',dict(n=4),4,3),('star',dict(n=4),4,3),('grid',dict(rows=2,cols=3),6,7)]:
                a=generate(Path(t)/kind,kind,**kw)
                b=generate(Path(t)/(kind+'copy'),kind,**kw)
                self.assertEqual(a,b);self.assertEqual(a['vertices'],n)
                self.assertEqual(a['input_edges'],edges);self.assertEqual(a['edges'],2*edges)
                text=(Path(t)/kind/'graph.edges').read_text()
                self.assertTrue(all(len(x.split())==2 for x in text.splitlines()))
                expected={'path':'0 1\n1 2\n2 3\n','star':'0 1\n0 2\n0 3\n',
                          'grid':'0 1\n0 3\n1 2\n1 4\n2 5\n3 4\n4 5\n'}
                self.assertEqual(text,expected[kind])
                with self.assertRaises(FileExistsError):generate(Path(t)/kind,kind,**kw)
            self.assertEqual(generate(Path(t)/'one','path',n=1,directed=True)['edges'],0)
            for n in [0,-1,1000001]:
                with self.assertRaises(ValueError):generate(Path(t)/'bad','path',n=n)
            with self.assertRaises(ValueError):generate(Path(t)/'bad','grid',rows=0,cols=2)

    def test_statistics(self):
        s=summarize(list(range(1,11)))
        self.assertEqual((s['median'],s['q1'],s['q3'],s['iqr']),(5.5,3.25,7.75,4.5))
        records=[synthetic() for _ in range(10)]+[synthetic(algorithm='omp-basic',schedule='static',threads_requested=4,threads_actual=2,runtime_seconds=1.) for _ in range(10)]
        r=aggregate(records)[0]
        self.assertEqual((r['speedup'],r['efficiency']),(2.,1.))
        zero=[synthetic(runtime_seconds=0) for _ in range(10)]
        self.assertIsNone(aggregate(zero)[0]['speedup'])
        mixed=copy.deepcopy(records);mixed[-1]['source']=1
        with self.assertRaises(ValueError):aggregate(mixed)
        records[-1]['threads_actual']=3
        with self.assertRaises(ValueError):aggregate(records)
        for x in [[],[1]*9,[float('inf')]*10]:
            with self.assertRaises(ValueError):summarize(x)

    def test_runner_and_provenance(self):
        # Fake subprocess exists only in this unit test and only uses tmp dirs.
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);generate(root/'data','path',n=4,directed=True)
            binary=root/'fake';binary.write_bytes(b'test only')
            environment=dict(cpu='test',physical_cores=2,logical_cores=2,ram_bytes=1000,
                             os='test',compiler='test',flags='test',openmp='test',runtime='test',
                             power='test',background_load='test',source=0,reachable=4)
            (root/'env.json').write_text(json.dumps(environment))
            (root/'correctness.log').write_text('synthetic test log only')
            (root/'evidence.json').write_text(json.dumps(dict(commit='test-sha',status='PASS',command='synthetic test only',log=str(root/'correctness.log'))))
            def fake(cmd,**kw):
                algo=cmd[cmd.index('--algo')+1];p=int(cmd[cmd.index('--threads')+1]);schedule=cmd[cmd.index('--schedule')+1]
                r=synthetic(algorithm=algo,threads_requested=p,threads_actual=p,
                            schedule='none' if algo=='serial' else schedule)
                return subprocess.CompletedProcess(cmd,0,json.dumps(r).encode(),b'')
            args=(binary,root/'data/dataset.json',root/'env.json',root/'evidence.json',root/'raw',[1,2])
            with patch('benchmark.git',side_effect=lambda *a: 'test-sha' if a[0]=='rev-parse' else ''),patch('benchmark.execute_binary',side_effect=fake):
                out,errors=run(*args)
            self.assertEqual(errors,0)
            summary=analyze(out);self.assertEqual(len(summary['rows']),13)
            self.assertTrue(all(r['samples']==10 for r in summary['rows']))
            with (out/'raw.jsonl').open('a') as f:f.write('{}\n')
            with self.assertRaises(ValueError):analyze(out)
            with patch('benchmark.git',side_effect=lambda *a: 'test-sha' if a[0]=='rev-parse' else ''),patch('benchmark.execute_binary',return_value=subprocess.CompletedProcess([],3,b'',b'not implemented')):
                out,errors=run(*args)
            self.assertEqual(errors,143)
            self.assertTrue(all(not s['valid'] for s in json.loads((out/'manifest.json').read_text())['samples']))
            self.assertEqual((out/'raw.jsonl').read_text(),'')
            with self.assertRaises(ValueError):analyze(out)
            with patch('benchmark.git',side_effect=lambda *a: 'test-sha' if a[0]=='rev-parse' else ''),patch('benchmark.execute_binary',side_effect=subprocess.TimeoutExpired('test',.01,output=b'partial',stderr=b'timeout')):
                out,errors=run(*args)
            self.assertEqual(errors,143)
            self.assertEqual((out/'00000.stdout').read_bytes(),b'partial')


if __name__=='__main__':unittest.main()
