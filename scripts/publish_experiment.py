"""Recreate public summaries, report tables and plots from the nine verified sessions."""
import argparse
import csv
import datetime
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_results import analyze
from plot_results import plot
from generate_graph import sha256

def publish(index_path, output, figures, tables):
    index=json.loads(Path(index_path).read_text(encoding='utf-8'))
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    figroot=Path(figures);figroot.mkdir(parents=True,exist_ok=False)
    rows=[];sessions=[];tex=[]
    def num(x):
        if x is None:return '--'
        digits=f'{x:.4g}'
        if 'e' in digits:
            mantissa,exponent=digits.split('e')
            return '$'+mantissa.replace('.',',')+r'\times10^{'+str(int(exponent))+'}$'
        return digits.replace('.',',')
    for entry in index:
        session=Path(entry['session']);s=analyze(session)
        manifest=json.loads((session/'manifest.json').read_text())
        duration=(datetime.datetime.fromisoformat(manifest['finished_at_utc'])-datetime.datetime.fromisoformat(manifest['started_at_utc'])).total_seconds()
        sessions.append(dict(id=entry['id'],session=str(session).replace('\\','/'),
             manifest_sha256=sha256(session/'manifest.json'),raw_sha256=manifest['hashes']['raw.jsonl'],
             commit=s['commit'],binary_sha256=manifest['binary_sha256'],dataset=s['dataset'],
             source=s['environment']['source'],started_at_utc=manifest['started_at_utc'],
             finished_at_utc=manifest['finished_at_utc'],wall_seconds=duration,
             samples=len(manifest['samples']),errors=sum(not a['valid'] for a in manifest['samples']),
             timer=s['environment']['timer'],timer_frequency_hz=s['environment']['timer_frequency_hz'],
             background=s['environment']['background_load']))
        for row in s['rows']:
            rows.append(dict(id=entry['id'],kind=s['dataset']['kind'],vertices=s['dataset']['vertices'],
                             edges=s['dataset']['edges'],source=s['environment']['source'],**row))
        plot(session,figroot/entry['id'])
        tex.extend([r'\begin{table}[htbp]',r'\centering\small',
          '\\caption['+entry['id']+': thống kê static]{'+entry['id']+': median và IQR theo ms, static; 10 mẫu/cấu hình. '+
          r'$S$ so Serial, $E$ theo team thực, $C$ so OpenMP một luồng.}',
          '\\label{tab:'+entry['id']+'}',r'\begin{tabular}{lrrrrrr}',r'\toprule',
          r'Phiên bản & $p$ & Median & IQR & $S$ & $E$ (\%) & $C$ \\',r'\midrule'])
        selected=[r for r in s['rows'] if r['algorithm']=='serial']+[
          r for r in s['rows'] if r['algorithm']!='serial' and r['schedule']=='static']
        for row in selected:
            label={'serial':'Serial','omp-basic':'Basic','omp-opt':'Optimized'}[row['algorithm']]
            tex.append(' & '.join([label,str(row['threads_actual']),num(row['median']*1000),
               num(row['iqr']*1000),num(row['speedup']),num(row['efficiency']*100 if row['efficiency'] is not None else None),
               num(row['scaling_vs_omp1'])])+r' \\')
        tex.extend([r'\bottomrule',r'\end{tabular}',r'\end{table}',''])
    with (out/'summary.csv').open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'summary.json').write_text(json.dumps(rows,indent=2))
    (out/'sessions.json').write_text(json.dumps(sessions,indent=2))
    Path(tables).parent.mkdir(parents=True,exist_ok=True)
    with Path(tables).open('x',encoding='utf-8') as f:f.write('\n'.join(tex).rstrip()+'\n')
    (out/'provenance.json').write_text(json.dumps(dict(index_sha256=sha256(index_path),
        publisher_sha256=sha256(__file__),analyzer_sha256=sha256('scripts/analyze_results.py'),
        plotter_sha256=sha256('scripts/plot_results.py'),matrix_sha256=sha256('docs/experiment-20261112-matrix.json'),
        summary_csv_sha256=sha256(out/'summary.csv'),tables_sha256=sha256(tables)),indent=2))
    print(len(sessions),'sessions;',len(rows),'configuration summaries; no samples dropped')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('index');p.add_argument('--out',required=True);p.add_argument('--figures',required=True);p.add_argument('--tables',required=True)
    a=p.parse_args();publish(a.index,a.out,a.figures,a.tables)
