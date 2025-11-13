import argparse
import os
import json
import csv
from glob import glob

"""Aggregate metrics script.

This script previously tracked energy in Joules derived from a CPU power
constant. At the user's request, we now express energy-related indicators
using average power (Watts) instead of total Joules. The transformation:

    energy_j_total            -> avg_watts (approx instantaneous average)
    energy_j_per_mb           -> watts_per_mb
    energy_j_per_record       -> watts_per_record

Rationale: Measuring or approximating Watts directly (e.g. via RAPL, powercap,
/proc or a TDP * utilization heuristic) is simpler in the current environment.
Downstream analysis / visualization scripts should be updated to expect the
new column names. Historical CSVs with energy_j_* columns are still readable
but will not be produced going forward.
"""

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
    'avg_watts',          # instantaneous average power (estimated or measured)
    'watts_per_mb',       # power normalized by MB processed
    'watts_per_record',   # power normalized by records trained
    'energy_j_total',     # derived: avg_watts * (time_ms/1000) when available
    'energy_j_per_mb',    # derived from watts_per_mb * (time_ms/1000) if both present
    'energy_j_per_record',# derived from watts_per_record * (time_ms/1000)
    # Resilience metrics (aggregated over FAULT_* events per experiment)
    'fault_injected_count',
    'fault_recovered_count',
    'recovery_success_rate',      # recovered / injected (0-1)
    'recovery_time_ms_mean',      # mean recovery_time_ms from FAULT_RECOVERED events
    'recovery_time_ms_p95',       # p95 recovery time
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


def _derive_energy_j_total(tm: dict):
    try:
        if tm.get('time_ms') and tm.get('avg_watts') is not None:
            return float(tm['avg_watts']) * (float(tm['time_ms']) / 1000.0)
    except Exception:
        return None
    return None


def _derive_energy_norm(tm: dict, watts_key: str):
    try:
        if tm.get('time_ms') and tm.get(watts_key) is not None:
            return float(tm[watts_key]) * (float(tm['time_ms']) / 1000.0)
    except Exception:
        return None
    return None


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

    # --- Resilience aggregation over FAULT_* events ---
    faults_injected = [e for e in events if e.get('event') == 'FAULT_INJECTED']
    faults_recovered = [e for e in events if e.get('event') == 'FAULT_RECOVERED']
    recovery_times = []
    for fr in faults_recovered:
        rt = fr.get('recovery_time_ms')
        try:
            if rt is not None:
                recovery_times.append(float(rt))
        except Exception:
            pass
    fault_injected_count = len(faults_injected)
    fault_recovered_count = len(faults_recovered)
    recovery_success_rate = None
    if fault_injected_count:
        recovery_success_rate = fault_recovered_count / fault_injected_count
    recovery_time_ms_mean = None
    recovery_time_ms_p95 = None
    if recovery_times:
        try:
            recovery_time_ms_mean = sum(recovery_times) / len(recovery_times)
            # p95
            ordered = sorted(recovery_times)
            idx = int(round(0.95 * (len(ordered)-1)))
            recovery_time_ms_p95 = ordered[idx]
        except Exception:
            pass
    # Add a separate summary row even if no faults (counts will be zero)
    out.append({
        'experimentId': exp_id,
        'group': group,
        'stage': 'RESILIENCE',
        'time_ms': None,
        'cpu_avg': None,
        'mem_peak_mb': None,
        'n_train': None,
        'mb_processed': None,
        'records_per_s': None,
        'data_mb_per_s': None,
        'avg_watts': None,
        'watts_per_mb': None,
        'watts_per_record': None,
        'energy_j_total': None,
        'energy_j_per_mb': None,
        'energy_j_per_record': None,
        'fault_injected_count': fault_injected_count,
        'fault_recovered_count': fault_recovered_count,
        'recovery_success_rate': recovery_success_rate,
        'recovery_time_ms_mean': recovery_time_ms_mean,
        'recovery_time_ms_p95': recovery_time_ms_p95,
        'efficiency_cpu_rps_per_pct': None,
        'efficiency_mem_rps_per_mb': None,
        'accuracy': None,
        'f1': None,
    })

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
            'avg_watts': tm.get('avg_watts') or tm.get('energy_j_total'),
            'watts_per_mb': tm.get('watts_per_mb') or tm.get('energy_j_per_mb'),
            'watts_per_record': tm.get('watts_per_record') or tm.get('energy_j_per_record'),
            'fault_injected_count': None,
            'fault_recovered_count': None,
            'recovery_success_rate': None,
            'recovery_time_ms_mean': None,
            'recovery_time_ms_p95': None,
            'efficiency_cpu_rps_per_pct': tm.get('efficiency_cpu_rps_per_pct'),
            'efficiency_mem_rps_per_mb': tm.get('efficiency_mem_rps_per_mb'),
            'accuracy': None,
            'f1': None,
            'energy_j_total': _derive_energy_j_total(tm),
            'energy_j_per_mb': _derive_energy_norm(tm, 'watts_per_mb'),
            'energy_j_per_record': _derive_energy_norm(tm, 'watts_per_record'),
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
            'avg_watts': None,
            'watts_per_mb': None,
            'watts_per_record': None,
            'efficiency_cpu_rps_per_pct': None,
            'efficiency_mem_rps_per_mb': None,
            'fault_injected_count': None,
            'fault_recovered_count': None,
            'recovery_success_rate': None,
            'recovery_time_ms_mean': None,
            'recovery_time_ms_p95': None,
            'accuracy': em.get('accuracy'),
            'f1': em.get('f1'),
            'energy_j_total': None,
            'energy_j_per_mb': None,
            'energy_j_per_record': None,
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
            'avg_watts': tm.get('avg_watts') or tm.get('energy_j_total'),
            'watts_per_mb': tm.get('watts_per_mb') or tm.get('energy_j_per_mb'),
            'watts_per_record': tm.get('watts_per_record') or tm.get('energy_j_per_record'),
            'fault_injected_count': None,
            'fault_recovered_count': None,
            'recovery_success_rate': None,
            'recovery_time_ms_mean': None,
            'recovery_time_ms_p95': None,
            'efficiency_cpu_rps_per_pct': tm.get('efficiency_cpu_rps_per_pct'),
            'efficiency_mem_rps_per_mb': tm.get('efficiency_mem_rps_per_mb'),
            'accuracy': None,
            'f1': None,
            'energy_j_total': _derive_energy_j_total(tm),
            'energy_j_per_mb': _derive_energy_norm(tm, 'watts_per_mb'),
            'energy_j_per_record': _derive_energy_norm(tm, 'watts_per_record'),
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
            'avg_watts': None,
            'watts_per_mb': None,
            'watts_per_record': None,
            'efficiency_cpu_rps_per_pct': None,
            'efficiency_mem_rps_per_mb': None,
            'fault_injected_count': None,
            'fault_recovered_count': None,
            'recovery_success_rate': None,
            'recovery_time_ms_mean': None,
            'recovery_time_ms_p95': None,
            'accuracy': em.get('accuracy'),
            'f1': em.get('f1'),
            'energy_j_total': None,
            'energy_j_per_mb': None,
            'energy_j_per_record': None,
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
        # Accept both standard events.jsonl and JADE-specific events_jade.jsonl produced by the
        # JADE prototype. Prefer events.jsonl when present, otherwise fall back to events_jade.jsonl.
        ev_path = os.path.join(d, 'logs', 'events.jsonl')
        ev_jade = os.path.join(d, 'logs', 'events_jade.jsonl')
        chosen = None
        if os.path.exists(ev_path):
            chosen = ev_path
        elif os.path.exists(ev_jade):
            chosen = ev_jade
        if not chosen:
            if args.verbose:
                print(f"Skip {exp_id}: no events.jsonl or events_jade.jsonl")
            continue
        group = load_group(d)
        if not group:
            # Skip experiments without explicit group assignment
            if args.verbose:
                print(f"Skip {exp_id}: no group in meta.json")
            continue
        # Read chosen events file and extract metrics
        evs = read_events(chosen)
        rows.extend(extract_metrics(exp_id, group, evs))
        if args.verbose:
            print(f"Added metrics for {exp_id} (group={group})")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            # ensure derived Joules values if missing
            if r.get('energy_j_total') is None and r.get('avg_watts') and r.get('time_ms'):
                try:
                    r['energy_j_total'] = float(r.get('avg_watts')) * (float(r.get('time_ms')) / 1000.0)
                except Exception:
                    pass
            if r.get('energy_j_per_mb') is None and r.get('watts_per_mb') and r.get('time_ms'):
                try:
                    r['energy_j_per_mb'] = float(r.get('watts_per_mb')) * (float(r.get('time_ms')) / 1000.0)
                except Exception:
                    pass
            if r.get('energy_j_per_record') is None and r.get('watts_per_record') and r.get('time_ms'):
                try:
                    r['energy_j_per_record'] = float(r.get('watts_per_record')) * (float(r.get('time_ms')) / 1000.0)
                except Exception:
                    pass
            w.writerow({k: r.get(k) for k in FIELDS})

    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == '__main__':
    main()
