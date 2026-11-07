"""Analyze one hash-verified session; never pool machines/builds/sources."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics
from benchmark import strict_json, validate
from generate_graph import sha256


def summarize(values):
    if len(values) < 10 or any(type(v) not in (int,float) or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("need >=10 finite nonnegative samples")
    x = sorted(values)
    def quantile(q):
        pos = (len(x)-1)*q
        lo = int(pos)
        return x[lo] + (x[min(lo+1,len(x)-1)]-x[lo])*(pos-lo)
    q1, q3 = quantile(.25), quantile(.75)
    return dict(samples=len(x), median=statistics.median(x), min=min(x), max=max(x),
                q1=q1, q3=q3, iqr=q3-q1)


def aggregate(records):
    if not records:
        raise ValueError("no records")
    identity = tuple(records[0][k] for k in ('vertices','edges','source','reachable','directed'))
    groups = defaultdict(list)
    actual = defaultdict(set)
    for r in records:
        validate(json.dumps(r, allow_nan=False))
        if tuple(r[k] for k in ('vertices','edges','source','reachable','directed')) != identity:
            raise ValueError("mixed graph/source")
        key = (r['algorithm'], r['threads_requested'], r['schedule'])
        actual[key].add(r['threads_actual'])
        groups[key].append(r['runtime_seconds'])
    baseline = groups.get(('serial',1,'none'))
    if baseline is None:
        raise ValueError("serial baseline missing")
    serial = summarize(baseline)['median']
    result = []
    for (a,p,s), values in sorted(groups.items()):
        if len(actual[a,p,s]) != 1:
            raise ValueError("unstable actual team; rerun or explicitly split groups")
        team = next(iter(actual[a,p,s]))
        row = dict(algorithm=a, threads_requested=p, threads_actual=team, schedule=s, **summarize(values))
        speed = serial/row['median'] if serial > 0 and row['median'] > 0 else None
        row.update(speedup=speed, efficiency=speed/team if speed is not None else None)
        result.append(row)
    return result


def analyze(session):
    session = Path(session)
    m = strict_json((session/'manifest.json').read_text(encoding='utf-8'))
    if not m['complete'] or m['dirty'] or m['repeats'] < 10:
        raise ValueError("incomplete/dirty session")
    if m['evidence']['status'] != 'PASS' or m['evidence']['commit'] != m['commit']:
        raise ValueError("correctness evidence mismatch")
    for name, digest in m['hashes'].items():
        if Path(name).name != name or sha256(session/name) != digest:
            raise ValueError("raw hash mismatch")
    if 'raw.jsonl' not in m['hashes']:
        raise ValueError("unhashed raw")
    records = []
    samples = {s['index']:s for s in m['samples']}
    seen = set()
    for line in (session/'raw.jsonl').read_text(encoding='utf-8').splitlines():
        entry = strict_json(line)
        index = entry['index']
        sample = samples[index]
        if index in seen or sample['warmup'] or not sample['valid'] or entry['result'] != sample['result']:
            raise ValueError("raw/manifest sample mismatch")
        seen.add(index)
        r = entry['result']
        expected = {k:m['dataset'][k] for k in ('vertices','edges','directed')}
        expected.update(source=m['environment']['source'], reachable=m['environment']['reachable'])
        records.append(validate(json.dumps(r),expected))
    expected_indices = {s['index'] for s in m['samples'] if s['valid'] and not s['warmup']}
    if seen != expected_indices or any(not s['valid'] for s in m['samples']):
        raise ValueError("missing/error samples")
    return dict(manifest_sha256=sha256(session/'manifest.json'), commit=m['commit'],
                dataset=m['dataset'], environment=m['environment'], rows=aggregate(records))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('session')
    p.add_argument('--out',required=True)
    a = p.parse_args()
    summary = analyze(a.session)
    with Path(a.out).open('x',encoding='utf-8') as f:
        json.dump(summary,f,indent=2,allow_nan=False)
