#!/usr/bin/env python3
"""Generate standardized thesis figures from aggregate_metrics.csv.

Usage:
  python python-analysis/generate_thesis_figures.py \
      --input data/results/aggregate_metrics.csv \
      --out docs/figures

Figures generated (PNG):
  - train_time_ms_<algo>.png : Distribution (boxplot + swarm) of TRAIN_<ALGO> time_ms by group
  - train_energy_j_per_mb_<algo>.png : Distribution of energy_j_per_mb
  - train_records_per_s_<algo>.png : Distribution of records_per_s
  - summary_table_metrics.png : Table-like image summarizing medians (optional)

Requirements: pandas, matplotlib, numpy.
"""
import argparse
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ALGO_NAMES = ["RF", "SVM"]  # Extend if more algorithms added
TRAIN_PREFIX = "TRAIN_"

# Metrics to plot (now watts-first). Each tuple: (column, title, filename slug)
PLOT_METRICS = [
    ("time_ms", "Tiempo de entrenamiento (ms)", "train_time_ms"),
    ("records_per_s", "Registros por segundo (records/s)", "train_records_per_s"),
    ("cpu_avg", "Uso promedio de CPU (%)", "train_cpu_avg"),
    ("mem_peak_mb", "Pico de memoria (MB)", "train_mem_peak_mb"),
    ("avg_watts", "Potencia promedio (W)", "train_avg_watts"),
    ("watts_per_mb", "Potencia normalizada (W/MB)", "train_watts_per_mb"),
]


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Filter only TRAIN_* rows with algo-specific stage
    return df


def filter_algo(df: pd.DataFrame, algo: str) -> pd.DataFrame:
    stage = f"{TRAIN_PREFIX}{algo}".upper()
    return df[df["stage"].str.upper() == stage].copy()


def ensure_out_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def _group_stats(data: pd.DataFrame, metric: str):
    """Return per-group median and 95% CI (approx using 1.96 * std/sqrt(n))."""
    groups = sorted(data["group"].dropna().unique())
    stats = []
    for g in groups:
        vals = data[data["group"] == g][metric].dropna().astype(float).values
        if len(vals) == 0:
            stats.append((g, np.nan, np.nan))
            continue
        med = float(np.median(vals))
        # 95% CI around the mean for error bar; still fine for quick viz.
        sem = (np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else 0.0
        ci95 = 1.96 * sem
        stats.append((g, med, ci95))
    return stats


def bar_with_error(ax, data: pd.DataFrame, metric: str, title: str):
    stats = _group_stats(data, metric)
    labels = [g for g, _, _ in stats]
    medians = [m for _, m, _ in stats]
    ci95 = [e for _, _, e in stats]
    x = np.arange(len(labels))
    colors = ["#1976d2" if "control" in l.lower() else "#43a047" for l in labels]
    ax.bar(x, medians, yerr=ci95, color=colors, alpha=0.9, capsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)


def trend_line(ax, data: pd.DataFrame, metric: str, title: str):
    groups = sorted(data["group"].dropna().unique())
    palette = ["#1976d2", "#43a047", "#fb8c00", "#8e24aa"]
    cmap = {g: palette[i % len(palette)] for i, g in enumerate(groups)}
    for g in groups:
        vals = data[data["group"] == g][metric].dropna().astype(float).values
        if len(vals) == 0:
            continue
        vals_sorted = np.sort(vals)
        ax.plot(np.arange(1, len(vals_sorted) + 1), vals_sorted, marker="o", linewidth=2, markersize=4, label=g, color=cmap[g], alpha=0.9)
    ax.set_xlabel("muestras ordenadas")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)


def save_metric_plot(df: pd.DataFrame, algo: str, metric: str, title: str, fname_slug: str, out_dir: Path):
    # Default: bar chart with 95% CI error bars
    fig, ax = plt.subplots(figsize=(6.5, 4))
    bar_with_error(ax, df, metric, f"{title} - {algo}")
    fig.tight_layout()
    out_path = out_dir / f"{fname_slug}_{algo.lower()}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def save_trend_plot(df: pd.DataFrame, algo: str, metric: str, title: str, fname_slug: str, out_dir: Path):
    fig, ax = plt.subplots(figsize=(6.5, 4))
    trend_line(ax, df, metric, f"{title} (tendencia) - {algo}")
    fig.tight_layout()
    out_path = out_dir / f"{fname_slug}_{algo.lower()}_trend.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def build_summary_table(df: pd.DataFrame, out_dir: Path):
    # Compute medians for each algo-group metric (watts-first)
    records = []
    for algo in ALGO_NAMES:
        adf = filter_algo(df, algo)
        for g in sorted(adf["group"].dropna().unique()):
            row = adf[adf["group"] == g]
            if row.empty:
                continue
            rec = {
                "Algo": algo,
                "Grupo": g,
                "time_ms_med": np.median(row["time_ms"].dropna()),
                "records_per_s_med": np.median(row["records_per_s"].dropna()),
                "avg_watts_med": np.median(row["avg_watts"].dropna()) if "avg_watts" in row.columns else np.nan,
                "watts_per_mb_med": np.median(row["watts_per_mb"].dropna()) if "watts_per_mb" in row.columns else np.nan,
            }
            records.append(rec)
    if not records:
        return None
    tdf = pd.DataFrame(records)
    fig, ax = plt.subplots(figsize=(7, 2 + 0.3 * len(tdf)))
    ax.axis("off")
    table_data = []
    for _, r in tdf.iterrows():
        table_data.append([
            r["Algo"],
            r["Grupo"],
            f"{r['time_ms_med']:.1f}",
            f"{r['records_per_s_med']:.2f}",
            f"{r['avg_watts_med']:.2f}",
            f"{r['watts_per_mb_med']:.3f}",
        ])
    col_labels = ["Algoritmo", "Grupo", "time_ms (med)", "records_per_s (med)", "avg_watts (med, W)", "watts_per_mb (med, W/MB)"]
    tbl = ax.table(cellText=table_data, colLabels=col_labels, loc="center")
    tbl.scale(1, 1.3)
    fig.tight_layout()
    out_path = out_dir / "summary_table_metrics.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to aggregate_metrics.csv")
    ap.add_argument("--out", required=True, help="Output directory for figures")
    args = ap.parse_args()
    in_path = Path(args.input)
    out_dir = Path(args.out)
    if not in_path.exists():
        raise SystemExit(f"Input file not found: {in_path}")
    ensure_out_dir(out_dir)

    df = load_data(in_path)
    generated = []
    for algo in ALGO_NAMES:
        adf = filter_algo(df, algo)
        if adf.empty:
            print(f"[warn] No rows for algo {algo}; skipping")
            continue
        for metric, title, slug in PLOT_METRICS:
            if metric not in adf.columns:
                print(f"[warn] Metric {metric} missing for algo {algo}")
                continue
            p = save_metric_plot(adf, algo, metric, title, slug, out_dir)
            generated.append(p)
            # Add trend variant for watts-focused metrics
            if metric in ("avg_watts", "watts_per_mb"):
                pt = save_trend_plot(adf, algo, metric, title, slug, out_dir)
                generated.append(pt)
    summary = build_summary_table(df, out_dir)
    if summary:
        generated.append(summary)

    print("Generated figures:")
    for p in generated:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
