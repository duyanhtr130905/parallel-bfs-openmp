"""Four figure groups from verified raw; matplotlib is optional, isolated in a venv."""
import argparse
import json
from pathlib import Path
from analyze_results import analyze
from generate_graph import sha256


def plot(session, out):
    summary = analyze(session)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    out = Path(out)
    out.mkdir(parents=True,exist_ok=False)
    rows = summary['rows']
    meta = summary['dataset']
    title = f"{meta['kind']} n={meta['vertices']}; source={summary['environment']['source']}; {summary['commit'][:8]}\nmeasured samples/config: {min(r['samples'] for r in rows)}+; runtime band: Q1-Q3"
    for metric, ylabel in [('median','Runtime (s)'),('speedup','Speedup vs serial'),('efficiency','Efficiency (fraction)')]:
        fig, ax = plt.subplots(figsize=(8,5))
        for algo in ('omp-basic','omp-opt'):
            for sched in ('static','dynamic','guided'):
                selected = sorted((r for r in rows if r['algorithm']==algo and r['schedule']==sched),key=lambda r:r['threads_actual'])
                selected = [r for r in selected if r[metric] is not None]
                if not selected:
                    continue
                x = [r['threads_actual'] for r in selected]
                y = [r[metric] for r in selected]
                ax.plot(x,y,marker='o',label=f'{algo}/{sched}')
                if metric=='median':
                    ax.fill_between(x,[r['q1'] for r in selected],[r['q3'] for r in selected],alpha=.12)
        serial = next(r for r in rows if r['algorithm']=='serial')
        if metric=='median':
            ax.axhline(serial['median'],color='black',linestyle=':',label='Serial median')
        ax.set(xlabel='Actual threads',ylabel=ylabel,title=title)
        ax.legend(fontsize=7);ax.grid(alpha=.3);fig.tight_layout()
        fig.savefig(out/f'{metric}.pdf');plt.close(fig)
    fig, ax = plt.subplots(figsize=(10,5))
    selected = [r for r in rows if r['algorithm']!='serial']
    x = list(range(len(selected)))
    ax.bar(x,[r['median'] for r in selected])
    ax.set_xticks(x,[f"{r['algorithm']}\n{r['schedule']}\np={r['threads_actual']}" for r in selected],rotation=90,fontsize=6)
    ax.set(ylabel='Runtime median (s)',title=title)
    fig.tight_layout();fig.savefig(out/'scheduling.pdf');plt.close(fig)
    summary['matplotlib_version'] = matplotlib.__version__
    summary['plot_script_sha256'] = sha256(__file__)
    (out/'provenance.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('session');p.add_argument('--out',required=True)
    a=p.parse_args();plot(a.session,a.out)
