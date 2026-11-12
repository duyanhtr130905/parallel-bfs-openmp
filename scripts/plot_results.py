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
    title = f"{meta['kind']} n={meta['vertices']}; source={summary['environment']['source']}; {summary['commit'][:8]}"
    sample_note = f"{min(r['samples'] for r in rows)} samples/config"
    for metric, ylabel in [('median','Runtime (s)'),('speedup','Speedup vs serial'),('efficiency','Efficiency (fraction)')]:
        fig, ax = plt.subplots(figsize=(6.5,4.3))
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
        values = [r[metric] for r in rows if r[metric] is not None]
        if values and min(values)>0 and (max(values)/min(values)>100 or metric=='speedup'):
            ax.set_yscale('log')
            ylabel += ' (log scale)'
        ax.set(xlabel='Actual threads',ylabel=ylabel)
        note = 'runtime band: Q1-Q3' if metric=='median' else 'ratio of medians'
        ax.set_title(title+'\n'+sample_note+'; '+note, fontsize=10, pad=10)
        ax.set_xticks(sorted({r['threads_actual'] for r in rows}))
        ax.legend(fontsize=9);ax.grid(alpha=.3);fig.tight_layout(pad=1.2)
        fig.savefig(out/f'{metric}.pdf');plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.5,4.3))
    groups = scheduling_groups(rows)
    for offset, sched in enumerate(('static','dynamic','guided')):
        positions = [i+(offset-1)*.25 for i,(_,policies) in enumerate(groups) if sched in policies]
        values = [policies[sched]['median'] for _,policies in groups if sched in policies]
        selected = [policies[sched] for _,policies in groups if sched in policies]
        errors = [[r['median']-r['q1'] for r in selected],[r['q3']-r['median'] for r in selected]]
        ax.bar(positions, values, width=.25, label=sched, yerr=errors, capsize=2)
    names={'omp-basic':'Basic','omp-opt':'Opt'}
    ax.set_xticks(range(len(groups)),[f'{names[a]}\np={p}' for (a,p),_ in groups],fontsize=9)
    ax.legend(); ax.grid(axis='y', alpha=.3)
    ax.set(ylabel='Runtime median (s)')
    ax.set_title(title+'\n'+sample_note+'; median; whiskers: Q1-Q3', fontsize=10, pad=10)
    fig.tight_layout(pad=1.2);fig.savefig(out/'scheduling.pdf');plt.close(fig)
    summary['matplotlib_version'] = matplotlib.__version__
    summary['plot_script_sha256'] = sha256(__file__)
    (out/'provenance.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('session');p.add_argument('--out',required=True)
    a=p.parse_args();plot(a.session,a.out)
