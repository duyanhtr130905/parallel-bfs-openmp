"""Read-only acceptance audit; independent of analyzer/publisher/plotter imports.

Run at repository root: python scripts/audit_final_evidence.py --out NEW_JSON
The backup is read only. No benchmark is executed and no raw is rewritten.
"""
import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def quantile(values, fraction):
    # Linear interpolation at (n-1)*q, implemented with decimal arithmetic.
    x = sorted(Decimal(str(v)) for v in values)
    pos = Decimal(len(x) - 1) * Decimal(str(fraction))
    lo = int(pos)
    return x[lo] + (x[min(lo + 1, len(x) - 1)] - x[lo]) * (pos - lo)


def same(a, b):
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-15)


def tex_number(value):
    if value is None:
        return '--'
    digits = format(float(value), '.4g')
    if 'e' in digits:
        mantissa, exponent = digits.split('e')
        return '$' + mantissa.replace('.', ',') + r'\times10^{' + str(int(exponent)) + '}$'
    return digits.replace('.', ',')


def audit(backup):
    entries = load('results/experiment-20261112/sessions.json')
    matrix = load('docs/experiment-20261112-matrix.json')
    jobs = {j['id']: j for j in matrix['jobs']}
    csv_rows = list(csv.DictReader(Path('results/experiment-20261112/summary.csv').open(encoding='utf-8', newline='')))
    json_rows = load('results/experiment-20261112/summary.json')
    require(len(entries) == 9 and len(csv_rows) == len(json_rows) == 225, 'matrix size')
    expected = {('serial', 1, 'none')} | {(a, p, s) for a in ('omp-basic', 'omp-opt') for p in (1, 2, 4, 8) for s in ('static', 'dynamic', 'guided')}
    table_lines = [line.strip().removesuffix(r'\\').strip() for line in Path('report/chapters/experiment_tables.tex').read_text(encoding='utf-8').splitlines() if re.match(r'^(Serial|Basic|Optimized) &', line)]
    report = {'status': 'PASS', 'method': 'Independent stdlib/Decimal audit; no imports from production experiment tools; linear quantiles at (n-1)q; tolerance rel=1e-12 abs=1e-15.', 'sessions': [], 'figures': [], 'backup': str(backup), 'rows_checked': 0, 'static_table_rows_checked': 0}
    calculated = []
    table_index = 0
    for entry in entries:
        root = Path(entry['session']); mirror = backup / root.name
        manifest = load(root / 'manifest.json'); job = jobs[entry['id']]
        require(digest(root / 'manifest.json') == entry['manifest_sha256'], 'manifest hash ' + entry['id'])
        require(manifest['complete'] and not manifest['dirty'] and manifest['commit'] == entry['commit'], 'session complete/commit')
        require(len(manifest['samples']) == 275 and manifest['repeats'] == 10 and manifest['warmups'] == 1, 'sample count')
        require({(c['algorithm'], c['threads_requested'], c['schedule']) for c in manifest['configurations']} == expected, 'registered configurations')
        files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        require(files == {p.relative_to(mirror).as_posix() for p in mirror.rglob('*') if p.is_file()}, 'backup file inventory')
        for name in files:
            actual = digest(root / name)
            require(actual == digest(mirror / name), 'backup mismatch ' + name)
            if name != 'manifest.json':
                require(actual == manifest['hashes'][name], 'raw/log hash ' + name)
        require(digest(root / 'raw.jsonl') == entry['raw_sha256'], 'raw index hash')
        dataset = Path(job['dataset'].replace('\\', '/'))
        graph = dataset.parent / manifest['dataset']['file']
        backup_graph = backup / 'datasets' / graph.parent.name / graph.name
        require(load(dataset) == manifest['dataset'], 'dataset metadata')
        require(digest(graph) == digest(backup_graph) == entry['dataset']['sha256'] == job['sha256'], 'dataset hash')
        require(digest(dataset) == digest(backup_graph.parent / dataset.name), 'dataset JSON backup')
        require(digest(backup / 'build-evidence/bfs.exe') == manifest['binary_sha256'] == entry['binary_sha256'], 'binary hash')
        require(digest(backup / 'build-evidence/correctness-ab588fb.log') == manifest['evidence']['log_sha256'], 'correctness proof hash')
        require(manifest['evidence']['binary_sha256'] == manifest['binary_sha256'] and manifest['evidence']['commit'] == manifest['commit'], 'proof binary/commit')
        warm = Counter(); measured = defaultdict(list); repeats = defaultdict(set)
        raw = [json.loads(line) for line in (root / 'raw.jsonl').read_text().splitlines()]
        require(len(raw) == 250 and len({r['index'] for r in raw}) == 250, 'unique raw index')
        raw_by_index = {r['index']: r['result'] for r in raw}
        for index, sample in enumerate(manifest['samples']):
            require(sample['index'] == index and sample['valid'] and sample['exit'] == 0, 'valid ordered sample')
            result = json.loads((root / f'{index:05}.stdout').read_text())
            require(result == sample['result'] and not (root / f'{index:05}.stderr').read_bytes(), 'stdout/stderr equality')
            key = (result['algorithm'], result['threads_requested'], result['schedule'])
            require(key in expected and result['threads_actual'] == result['threads_requested'], 'team/config')
            require(result['source'] == job['source'] and result['vertices'] == job['vertices'] and result['edges'] == job['edges'] and result['reachable'] == job['vertices'] and result['directed'] is False and result['status'] == 'ok' and result['schema_version'] == 1, 'result metadata')
            require(math.isfinite(result['runtime_seconds']) and result['runtime_seconds'] > 0, 'positive finite timing')
            if sample['warmup']:
                require(sample['repeat'] == -1 and index not in raw_by_index, 'warmup exclusion')
                warm[key] += 1
            else:
                require(raw_by_index[index] == result and sample['repeat'] not in repeats[key], 'raw sample/repetition duplicate')
                repeats[key].add(sample['repeat']); measured[key].append(result['runtime_seconds'])
        require(set(warm) == set(measured) == expected and all(v == 1 for v in warm.values()) and all(v == set(range(10)) for v in repeats.values()), 'complete 25x11 matrix')
        stats = {}
        for key, values in measured.items():
            stats[key] = dict(median=quantile(values, .5), min=Decimal(str(min(values))), max=Decimal(str(max(values))), q1=quantile(values, .25), q3=quantile(values, .75))
            stats[key]['iqr'] = stats[key]['q3'] - stats[key]['q1']
        for (algo, team, sched), values in stats.items():
            values['speedup'] = stats[('serial', 1, 'none')]['median'] / values['median']
            values['efficiency'] = values['speedup'] / team
            values['scaling_vs_omp1'] = None if algo == 'serial' else stats[(algo, 1, sched)]['median'] / values['median']
            key = (algo, team, sched)
            for published in (csv_rows, json_rows):
                matches = [r for r in published if r['id'] == entry['id'] and r['algorithm'] == algo and int(r['threads_requested']) == team and r['schedule'] == sched]
                require(len(matches) == 1, 'unique published row')
                row = matches[0]
                require(int(row['samples']) == 10 and int(row['threads_actual']) == team and int(row['source']) == job['source'], 'published row metadata')
                for field, value in values.items():
                    require(row[field] in (None, '') if value is None else same(row[field], value), f'{entry["id"]} {key} {field}')
            calculated.append({'id': entry['id'], 'algorithm': algo, 'threads_actual': team, 'schedule': sched, **{k: float(v) if v is not None else None for k, v in values.items()}})
            report['rows_checked'] += 1
        selected = [('serial', 1, 'none')] + [(a, p, 'static') for a in ('omp-basic', 'omp-opt') for p in (1, 2, 4, 8)]
        for key in selected:
            s = stats[key]; name = {'serial': 'Serial', 'omp-basic': 'Basic', 'omp-opt': 'Optimized'}[key[0]]
            cells = [name, str(key[1]), tex_number(s['median'] * 1000), tex_number(s['iqr'] * 1000), tex_number(s['speedup']), tex_number(s['efficiency'] * 100), tex_number(s['scaling_vs_omp1'])]
            # Match published binary-float rounding at decimal half ties as well.
            got = table_lines[table_index].split(' & ')
            require(got[:2] == cells[:2], 'table identity')
            for cell, actual in zip(got[2:], [s['median']*1000, s['iqr']*1000, s['speedup'], s['efficiency']*100, s['scaling_vs_omp1']]):
                if actual is None:
                    require(cell == '--', 'table null')
                else:
                    numeric = re.sub(r'\$([^$]+)\\times10\^\{(-?\d+)\}\$', r'\1e\2', cell).replace(',', '.')
                    require(abs(Decimal(numeric) - actual) <= max(abs(actual)*Decimal('0.00051'), Decimal('1e-15')), 'table rounding ' + cell)
            table_index += 1
        figroot = Path('report/figures/experiment-20261112') / entry['id']
        provenance = load(figroot / 'provenance.json')
        require(provenance['manifest_sha256'] == entry['manifest_sha256'] and provenance['plot_script_sha256'] == digest('scripts/plot_results.py') and provenance['dataset'] == manifest['dataset'], 'figure provenance')
        for row in provenance['rows']:
            key = (row['algorithm'], row['threads_actual'], row['schedule'])
            for field, value in stats[key].items():
                require(row[field] is None if value is None else same(row[field], value), 'figure data')
        for pdf in sorted(figroot.glob('*.pdf')):
            report['figures'].append({'path': pdf.as_posix(), 'sha256': digest(pdf)})
        report['sessions'].append({'id': entry['id'], 'manifest_sha256': entry['manifest_sha256'], 'raw_sha256': entry['raw_sha256'], 'dataset_sha256': entry['dataset']['sha256'], 'binary_sha256': entry['binary_sha256'], 'warmups': 25, 'measured': 250, 'files_compared_to_backup': len(files)})
    report['static_table_rows_checked'] = table_index
    require(table_index == len(table_lines) == 81 and len(report['figures']) == 36, 'tables/figures count')
    used = re.findall(r'\\includegraphics\[[^\]]*\]\{(figures/experiment-20261112/[^}]+)\}', Path('report/chapters/chapter5.tex').read_text(encoding='utf-8'))
    require(len(set(used)) == len(used) == 12 and all((Path('report') / p).is_file() for p in used), '12 report figures')
    report['report_figures'] = used
    provenance = load('results/experiment-20261112/provenance.json')
    for field, path in {'index_sha256': backup / 'batch-index.json', 'publisher_sha256': 'scripts/publish_experiment.py', 'analyzer_sha256': 'scripts/analyze_results.py', 'plotter_sha256': 'scripts/plot_results.py', 'matrix_sha256': 'docs/experiment-20261112-matrix.json', 'summary_csv_sha256': 'results/experiment-20261112/summary.csv', 'tables_sha256': 'report/chapters/experiment_tables.tex'}.items():
        require(digest(path) == provenance[field], 'publication provenance ' + field)
    for item in load(backup / 'build-evidence-hashes.json'):
        path = backup / 'build-evidence' / Path(item['Path'].replace('\\', '/')).name
        require(digest(path).lower() == item['Hash'].lower(), 'backup build evidence ' + path.name)
    report['max_speedup'] = max((r for r in calculated if r['algorithm'] != 'serial'), key=lambda r: r['speedup'])
    report['openmp_speedups_below_one'] = sum(r['algorithm'] != 'serial' and r['speedup'] < 1 for r in calculated)
    report['multithread_scaling_below_one'] = sum(r['threads_actual'] > 1 and r['scaling_vs_omp1'] < 1 for r in calculated)
    require(report['openmp_speedups_below_one'] == 216 and report['multithread_scaling_below_one'] == 162, 'published headline counts')
    return report, calculated


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup', type=Path, default=Path('D:/Code/parallel-bfs-evidence/20261112-1616/official-ab588fb'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report, calculated = audit(args.backup)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    with args.out.with_suffix('.rows.json').open('x', encoding='utf-8') as stream:
        json.dump(calculated, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k not in ('sessions', 'figures', 'report_figures')}, ensure_ascii=False, indent=2))
