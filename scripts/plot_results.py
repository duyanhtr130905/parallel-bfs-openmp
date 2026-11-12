"""Four figure groups from verified raw; matplotlib is optional, isolated in a venv."""
import argparse
import json
from pathlib import Path
from analyze_results import analyze
from generate_graph import sha256


def scheduling_groups(rows):
    """Compare policies only at the same measured team size, per algorithm."""
    groups = {}
    for row in rows:
        if row['algorithm'] != 'serial':
            key = (row['algorithm'], row['threads_actual'])
            policies = groups.setdefault(key, {})
            if row['schedule'] in policies:
                raise ValueError('ambiguous scheduling comparison at actual team size')
            policies[row['schedule']] = row
    return sorted(groups.items())


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
        if metric=='speedup':
            teams = sorted({r['threads_actual'] for r in rows})
            ax.plot(teams, teams, color='black', linestyle='--', label='Ideal S=p')
        ax.set(xlabel='Actual threads',ylabel=ylabel,title=title)
        ax.legend(fontsize=7);ax.grid(alpha=.3);fig.tight_layout()
        fig.savefig(out/f'{metric}.pdf');plt.close(fig)
    fig, ax = plt.subplots(figsize=(10,5))
    groups = scheduling_groups(rows)
    for offset, sched in enumerate(('static','dynamic','guided')):
        positions = [i+(offset-1)*.25 for i,(_,policies) in enumerate(groups) if sched in policies]
        values = [policies[sched]['median'] for _,policies in groups if sched in policies]
        ax.bar(positions, values, width=.25, label=sched)
    ax.set_xticks(range(len(groups)),[f'{a}\np={p}' for (a,p),_ in groups],fontsize=8)
    ax.legend(); ax.grid(axis='y', alpha=.3)
    ax.set(ylabel='Runtime median (s)',title=title)
    fig.tight_layout();fig.savefig(out/'scheduling.pdf');plt.close(fig)
    summary['matplotlib_version'] = matplotlib.__version__
    summary['plot_script_sha256'] = sha256(__file__)
    (out/'provenance.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('session');p.add_argument('--out',required=True)
    a=p.parse_args();plot(a.session,a.out)
