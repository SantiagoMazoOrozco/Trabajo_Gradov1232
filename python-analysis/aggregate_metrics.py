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
    'n_train',
    'mb_processed',
    'records_per_s',
    'data_mb_per_s',
    'energy_j_total',
    'energy_j_per_mb',
    'energy_j_per_record',
    'efficiency_cpu_rps_per_pct',
    'efficiency_mem_rps_per_mb',
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
            # Use utf-8-sig to support BOM-prefixed JSON files written by some tools
            with open(meta_path, 'r', encoding='utf-8-sig') as f:
                meta = json.load(f) or {}
                g = meta.get('group')
                if isinstance(g, str) and g.strip():
                    return g.strip()
                return None
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
            'n_train': tm.get('n_train'),
            'mb_processed': tm.get('mb_processed'),
            'records_per_s': tm.get('records_per_s'),
            'data_mb_per_s': tm.get('data_mb_per_s'),
            'energy_j_total': tm.get('energy_j_total'),
            'energy_j_per_mb': tm.get('energy_j_per_mb'),
            'energy_j_per_record': tm.get('energy_j_per_record'),
            'efficiency_cpu_rps_per_pct': tm.get('efficiency_cpu_rps_per_pct'),
            'efficiency_mem_rps_per_mb': tm.get('efficiency_mem_rps_per_mb'),
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
            'n_train': None,
            'mb_processed': None,
            'records_per_s': None,
            'data_mb_per_s': None,
            'energy_j_total': None,
            'energy_j_per_mb': None,
            'energy_j_per_record': None,
            'efficiency_cpu_rps_per_pct': None,
            'efficiency_mem_rps_per_mb': None,
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
            'n_train': tm.get('n_train'),
            'mb_processed': tm.get('mb_processed'),
            'records_per_s': tm.get('records_per_s'),
            'data_mb_per_s': tm.get('data_mb_per_s'),
            'energy_j_total': tm.get('energy_j_total'),
            'energy_j_per_mb': tm.get('energy_j_per_mb'),
            'energy_j_per_record': tm.get('energy_j_per_record'),
            'efficiency_cpu_rps_per_pct': tm.get('efficiency_cpu_rps_per_pct'),
            'efficiency_mem_rps_per_mb': tm.get('efficiency_mem_rps_per_mb'),
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
            'n_train': None,
            'mb_processed': None,
            'records_per_s': None,
            'data_mb_per_s': None,
            'energy_j_total': None,
            'energy_j_per_mb': None,
            'energy_j_per_record': None,
            'efficiency_cpu_rps_per_pct': None,
            'efficiency_mem_rps_per_mb': None,
            'accuracy': em.get('accuracy'),
            'f1': em.get('f1'),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='data/results', help='Root folder containing experiment dirs')
    ap.add_argument('--output', default='data/results/aggregate_metrics.csv', help='CSV output path')
    ap.add_argument('--verbose', action='store_true', help='Print debug info while aggregating')
    args = ap.parse_args()

    rows = []
    exp_dirs = [d for d in glob(os.path.join(args.root, '*')) if os.path.isdir(d)]
    if args.verbose:
        print(f"Found {len(exp_dirs)} candidate dirs under {args.root}")
    for d in exp_dirs:
        exp_id = os.path.basename(d)
        # Skip internal or server log folders
        if exp_id.startswith('_'):
            if args.verbose:
                print(f"Skip {exp_id}: internal folder")
            continue
        ev_path = os.path.join(d, 'logs', 'events.jsonl')
        if not os.path.exists(ev_path):
            if args.verbose:
                print(f"Skip {exp_id}: no events.jsonl")
            continue
        group = load_group(d)
        if not group:
            # Skip experiments without explicit group assignment
            if args.verbose:
                print(f"Skip {exp_id}: no group in meta.json")
            continue
        evs = read_events(ev_path)
        rows.extend(extract_metrics(exp_id, group, evs))
        if args.verbose:
            print(f"Added metrics for {exp_id} (group={group})")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in FIELDS})

    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == '__main__':
    main()
