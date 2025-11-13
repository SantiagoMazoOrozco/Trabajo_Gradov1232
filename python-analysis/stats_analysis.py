import argparse
import os
import json
import pandas as pd
import numpy as np
from scipy import stats


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
    # Expect columns: experimentId, group, stage, time_ms, cpu_avg, mem_peak_mb, avg_watts, watts_per_mb, accuracy, f1
    # Backward compatibility: if watts_per_mb is missing, try energy_j_per_mb
    watts_col = 'watts_per_mb' if 'watts_per_mb' in df.columns else ('energy_j_per_mb' if 'energy_j_per_mb' in df.columns else None)
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
        ('TRAIN_RF', watts_col),
        ('TRAIN_SVM', watts_col),
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
            t_p = None
            d = None
        else:
            p = permutation_pvalue(a, b, n=args.permutations, metric='mean', seed=42)
            # Welch's t-test (unequal variances)
            try:
                t_stat, t_p = stats.ttest_ind(a, b, equal_var=False, nan_policy='omit')
            except Exception:
                t_p = None
            # Cohen's d (pooled)
            try:
                mean_a, mean_b = float(np.nanmean(a)), float(np.nanmean(b))
                sd_a, sd_b = float(np.nanstd(a, ddof=1)), float(np.nanstd(b, ddof=1))
                n_a, n_b = len(a), len(b)
                s_pooled = np.sqrt(((n_a - 1) * sd_a ** 2 + (n_b - 1) * sd_b ** 2) / (n_a + n_b - 2)) if (n_a + n_b - 2) > 0 else np.nan
                d = (mean_a - mean_b) / s_pooled if s_pooled and not np.isnan(s_pooled) and s_pooled != 0 else None
            except Exception:
                d = None
        results.append({'stage': stage, 'metric': col, 'groupA': gA, 'groupB': gB,
                        'meanA': float(np.nanmean(a)) if len(a) else None,
                        'meanB': float(np.nanmean(b)) if len(b) else None,
                        'perm_p_value': p,
                        't_p_value': t_p,
                        'cohens_d': None if d is None else float(d)})

    os.makedirs(args.outdir, exist_ok=True)
    json_path = os.path.join(args.outdir, 'stats_summary.json')
    md_path = os.path.join(args.outdir, 'stats_summary.md')

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'tests': results}, f, indent=2)

    lines = [
        '# Resumen estadístico',
        '',
        f'Comparación: {gA} vs {gB} — N permutaciones={args.permutations}',
        '',
        '| Etapa | Métrica | media(A) | media(B) | perm p | t-test p | Cohen d |',
        '|---|---|---:|---:|---:|---:|---:|',
    ]
    for r in results:
        lines.append(f"| {r['stage']} | {r['metric']} | {r['meanA']} | {r['meanB']} | {r['perm_p_value']} | {r['t_p_value']} | {r['cohens_d']} |")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(json.dumps({'summary_json': json_path, 'summary_md': md_path}))

    # Also write a copy under docs/ for reporting
    try:
        docs_dir = os.path.join('docs')
        os.makedirs(docs_dir, exist_ok=True)
        with open(os.path.join(docs_dir, 'stats_report.md'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    except Exception:
        pass


if __name__ == '__main__':
    main()
