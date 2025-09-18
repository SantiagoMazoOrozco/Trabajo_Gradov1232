import argparse
import os
import json
import csv
from glob import glob

FIELDS = [
    'experimentId',
    'group',
    'stage',
    'time_ms',
    'cpu_avg',
    'mem_peak_mb',
    'accuracy',
    'f1',
]


def read_events(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def load_group(exp_dir):
    meta_path = os.path.join(exp_dir, 'meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                return (json.load(f) or {}).get('group')
        except Exception:
            return None
    return None


def extract_metrics(exp_id, group, events):
    out = []
    by_event = {e.get('event'): e for e in events}

    # Train RF
    rf = by_event.get('MODEL_TRAINED_RF')
    if rf:
        tm = rf.get('train_metrics') or {}
        out.append({
            'experimentId': exp_id,
            'group': group,
            'stage': 'TRAIN_RF',
            'time_ms': tm.get('time_ms'),
            'cpu_avg': tm.get('cpu_avg'),
            'mem_peak_mb': tm.get('mem_peak_mb'),
            'accuracy': None,
            'f1': None,
        })
    # Eval RF
    er = by_event.get('EVAL_DONE_RF')
    if er:
        em = er.get('eval_metrics') or {}
        out.append({
            'experimentId': exp_id,
            'group': group,
            'stage': 'EVAL_RF',
            'time_ms': None,
            'cpu_avg': None,
            'mem_peak_mb': None,
            'accuracy': em.get('accuracy'),
            'f1': em.get('f1'),
        })
    # Train SVM
    svm = by_event.get('MODEL_TRAINED_SVM')
    if svm:
        tm = svm.get('train_metrics') or {}
        out.append({
            'experimentId': exp_id,
            'group': group,
            'stage': 'TRAIN_SVM',
            'time_ms': tm.get('time_ms'),
            'cpu_avg': tm.get('cpu_avg'),
            'mem_peak_mb': tm.get('mem_peak_mb'),
            'accuracy': None,
            'f1': None,
        })
    # Eval SVM
    es = by_event.get('EVAL_DONE_SVM')
    if es:
        em = es.get('eval_metrics') or {}
        out.append({
            'experimentId': exp_id,
            'group': group,
            'stage': 'EVAL_SVM',
            'time_ms': None,
            'cpu_avg': None,
            'mem_peak_mb': None,
            'accuracy': em.get('accuracy'),
            'f1': em.get('f1'),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='data/results', help='Root folder containing experiment dirs')
    ap.add_argument('--output', default='data/results/aggregate_metrics.csv', help='CSV output path')
    args = ap.parse_args()

    rows = []
    exp_dirs = [d for d in glob(os.path.join(args.root, '*')) if os.path.isdir(d)]
    for d in exp_dirs:
        exp_id = os.path.basename(d)
        ev_path = os.path.join(d, 'logs', 'events.jsonl')
    evs = read_events(ev_path)
    group = load_group(d)
    rows.extend(extract_metrics(exp_id, group, evs))

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in FIELDS})

    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == '__main__':
    main()
