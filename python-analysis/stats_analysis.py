import argparse
import os
import json
import pandas as pd
import numpy as np


def permutation_pvalue(x, y, n=10000, metric='mean', seed=42):
    rng = np.random.default_rng(seed)
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    if len(x) == 0 or len(y) == 0:
        return None
    if metric == 'mean':
        observed = np.mean(x) - np.mean(y)
    else:
        observed = np.median(x) - np.median(y)
    pooled = np.concatenate([x, y])
    nx = len(x)
    cnt = 0
    for _ in range(n):
        rng.shuffle(pooled)
        x_ = pooled[:nx]
        y_ = pooled[nx:]
        stat = (np.mean(x_) - np.mean(y_)) if metric == 'mean' else (np.median(x_) - np.median(y_))
        if abs(stat) >= abs(observed):
            cnt += 1
    return (cnt + 1) / (n + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='data/results/aggregate_metrics.csv')
    ap.add_argument('--outdir', default='data/results')
    ap.add_argument('--permutations', type=int, default=10000)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    # Expect columns: experimentId, group, stage, time_ms, cpu_avg, mem_peak_mb, energy_j_total, energy_j_per_mb, accuracy, f1
    groups = df['group'].dropna().unique().tolist()
    if not groups or len(groups) < 2:
        print(json.dumps({'error': 'Need at least two groups in aggregate CSV'}))
        return
    gA, gB = groups[:2]

    # Focus on stages and metrics of interest
    results = []
    tests = [
        ('TRAIN_RF', 'time_ms'),
        ('TRAIN_SVM', 'time_ms'),
        ('TRAIN_RF', 'records_per_s'),
        ('TRAIN_SVM', 'records_per_s'),
        ('TRAIN_RF', 'energy_j_per_mb'),
        ('TRAIN_SVM', 'energy_j_per_mb'),
        ('EVAL_RF', 'accuracy'),
        ('EVAL_SVM', 'accuracy'),
        ('EVAL_RF', 'f1'),
        ('EVAL_SVM', 'f1'),
    ]
    for stage, col in tests:
        a = df[(df['group'] == gA) & (df['stage'] == stage)][col].astype(float).values
        b = df[(df['group'] == gB) & (df['stage'] == stage)][col].astype(float).values
        if len(a) == 0 or len(b) == 0:
            p = None
        else:
            p = permutation_pvalue(a, b, n=args.permutations, metric='mean', seed=42)
        results.append({'stage': stage, 'metric': col, 'groupA': gA, 'groupB': gB,
                        'meanA': float(np.nanmean(a)) if len(a) else None,
                        'meanB': float(np.nanmean(b)) if len(b) else None,
                        'p_value': p})

    os.makedirs(args.outdir, exist_ok=True)
    json_path = os.path.join(args.outdir, 'stats_summary.json')
    md_path = os.path.join(args.outdir, 'stats_summary.md')

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'tests': results}, f, indent=2)

    lines = [
        '# Resumen estadístico (permutation test)',
        '',
        f'Comparación: {gA} vs {gB} — N permutaciones={args.permutations}',
        '',
        '| Etapa | Métrica | media(A) | media(B) | p-value |',
        '|---|---|---:|---:|---:|',
    ]
    for r in results:
        lines.append(f"| {r['stage']} | {r['metric']} | {r['meanA']} | {r['meanB']} | {r['p_value']} |")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(json.dumps({'summary_json': json_path, 'summary_md': md_path}))


if __name__ == '__main__':
    main()
