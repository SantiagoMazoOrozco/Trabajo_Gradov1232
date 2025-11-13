#!/usr/bin/env python3
import csv, json, math, statistics as stats
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / 'data/results/aggregate_metrics.csv'
JSON_PATH = ROOT / 'data/results/stats_summary.json'
OUT_PATH_MD = ROOT / 'docs/_auto_results_tables.md'
OUT_PATH_TEX = ROOT / 'docs/_auto_results_tables.tex'

BATCH_PREFIX = 'batch_20251027_145840_'
STAGES = ['TRAIN_RF','TRAIN_SVM']
NUM_FIELDS = ['time_ms','cpu_avg','mem_peak_mb','records_per_s','watts_per_mb']

def fmt(x):
    if x is None:
        return ''
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return ''
        return f"{x:.3f}"
    return str(x)

def load_agg():
    agg = {stage: {'control': {k: [] for k in NUM_FIELDS}, 'treatment': {k: [] for k in NUM_FIELDS}} for stage in STAGES}
    with CSV_PATH.open(newline='') as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            exp = row.get('experimentId') or ''
            if not exp.startswith(BATCH_PREFIX):
                continue
            stage = row.get('stage')
            if stage not in STAGES:
                continue
            grp = row.get('group')
            if grp not in ('control','treatment'):
                continue
            for k in NUM_FIELDS:
                v = row.get(k)
                if not v:
                    continue
                try:
                    agg[stage][grp][k].append(float(v))
                except Exception:
                    pass
    return agg

def make_descriptive_table(agg):
    lines = []
    lines.append('### 4.1 Descriptivos (batch 20251027, medianas y medias)')
    lines.append('| Stage | Group | time_ms (med/mean) | cpu_avg% (med/mean) | mem_peak_mb (med/mean) | records_per_s (med/mean) | watts_per_mb (med/mean) |')
    lines.append('|---|---|---:|---:|---:|---:|---:|')
    for stage in STAGES:
        for grp in ('control','treatment'):
            vals = agg[stage][grp]
            rowout = [stage, grp]
            for k in NUM_FIELDS:
                arr = vals[k]
                if arr:
                    med = stats.median(arr)
                    mean = sum(arr)/len(arr)
                    rowout.append(f"{fmt(med)}/{fmt(mean)}")
                else:
                    rowout.append('')
            lines.append('| ' + ' | '.join(rowout) + ' |')
    return '\n'.join(lines)

def make_pvalues_table():
    with JSON_PATH.open() as jf:
        data = json.load(jf)
    p_lines = []
    p_lines.append('### 5.1.1 Resumen de p-values (permutación)')
    p_lines.append('| Stage | Métrica | p-value | Interpretación |')
    p_lines.append('|---|---|---:|---|')
    for test in data.get('tests', []):
        stage = test.get('stage')
        metric = test.get('metric')
        if stage in STAGES and metric in ('time_ms','energy_j_per_mb','records_per_s'):
            p = test.get('perm_p_value')
            interp = 'No significativo' if (p is None or p >= 0.05) else 'Significativo'
            p_s = '' if p is None else f"{p:.4f}"
            p_lines.append(f"| {stage} | {metric} | {p_s} | {interp} |")
    return '\n'.join(p_lines)

def latex_escape(s: str) -> str:
    # Minimal escaping for LaTeX tables
    return (
        s.replace('\\', '\\textbackslash ')
         .replace('&', '\\&')
         .replace('%', '\\%')
         .replace('_', '\\_')
         .replace('#', '\\#')
         .replace('{', '\\{')
         .replace('}', '\\}')
    )

def make_descriptive_table_tex(agg: dict) -> str:
    header = [
        '% Auto-generated: Descriptive stats',
        '\\begin{table}[ht]',
        '\\centering',
        '\\small',
        '\\begin{tabular}{llrrrrr}',
        'Stage & Group & time\\_ms (med/mean) & cpu\\_avg\\% (med/mean) & mem\\_peak\\_mb (med/mean) & records\\_per\\_s (med/mean) & watts\\_per\\_mb (med/mean) \\',
        '\\hline'
    ]
    rows = []
    for stage in STAGES:
        for grp in ('control','treatment'):
            vals = agg[stage][grp]
            cells = [stage, grp]
            for k in NUM_FIELDS:
                arr = vals[k]
                if arr:
                    med = stats.median(arr)
                    mean = sum(arr)/len(arr)
                    cells.append(f"{fmt(med)}/{fmt(mean)}")
                else:
                    cells.append('')
            rows.append(' ' + ' & '.join(latex_escape(c) for c in cells) + ' \\')
    footer = [
        '\\end{tabular}',
        '\\caption{Descriptivos (medianas/medias) del batch balanceado 2025-10-27 por etapa y grupo.}',
        '\\label{tab:descriptive_batch_20251027}',
        '\\end{table}'
    ]
    return '\n'.join(header + rows + footer)

def make_pvalues_table_tex() -> str:
    with JSON_PATH.open() as jf:
        data = json.load(jf)
    header = [
        '% Auto-generated: Permutation p-values',
        '\\begin{table}[ht]',
        '\\centering',
        '\\small',
        '\\begin{tabular}{llrl}',
        'Stage & Metrica & p-value & Interpretacion \\',
        '\\hline'
    ]
    rows = []
    for test in data.get('tests', []):
        stage = test.get('stage')
        metric = test.get('metric')
        if stage in STAGES and metric in ('time_ms','energy_j_per_mb','records_per_s'):
            p = test.get('perm_p_value')
            interp = 'No significativo' if (p is None or p >= 0.05) else 'Significativo'
            p_s = '' if p is None else f"{p:.4f}"
            rows.append(f"{latex_escape(stage)} & {latex_escape(metric)} & {latex_escape(p_s)} & {latex_escape(interp)} \\")
    footer = [
        '\\end{tabular}',
        '\\caption{p-values por permutacion (control vs treatment) en el batch balanceado 2025-10-27.}',
        '\\label{tab:pvalues_batch_20251027}',
        '\\end{table}'
    ]
    return '\n'.join(header + rows + footer)

def make_cliffs_delta_table_tex() -> str:
    cd_path = ROOT / 'data/results/batch_20251027_145840/figures/cliffs_delta.csv'
    if not cd_path.exists():
        return '% cliffs_delta.csv not found.'
    import csv as _csv
    header = [
        '% Auto-generated: Cliff\'s delta',
        '\\begin{table}[ht]',
        '\\centering',
        '\\small',
        '\\begin{tabular}{llrl}',
        'Stage & Metrica & Cliff\'s $\\delta$ & Magnitud \\',
        '\\hline'
    ]
    rows = []
    def magnitude(delta_abs: float) -> str:
        if delta_abs < 0.147: return 'Despreciable'
        if delta_abs < 0.33: return 'Pequeno'
        if delta_abs < 0.474: return 'Medio'
        return 'Grande'
    with cd_path.open(newline='') as f:
        rdr = _csv.DictReader(f)
        for row in rdr:
            stage = row['stage']
            metric = row['metric']
            try:
                d = float(row['cliffs_delta'])
            except Exception:
                continue
            mag = magnitude(abs(d))
            rows.append(f"{latex_escape(stage)} & {latex_escape(metric)} & {d:.2f} & {mag} \\")
    footer = [
        '\\end{tabular}',
        '\\caption{Cliff\'s $\\delta$ por etapa/metricas (batch 2025-10-27).}',
        '\\label{tab:cliffs_batch_20251027}',
        '\\end{table}'
    ]
    return '\n'.join(header + rows + footer)

def main():
    agg = load_agg()
    # Markdown output (for quick preview in repo)
    desc_md = make_descriptive_table(agg)
    ptab_md = make_pvalues_table()
    OUT_PATH_MD.write_text(desc_md + '\n\n' + ptab_md + '\n', encoding='utf-8')
    print(f"Wrote {OUT_PATH_MD}")

    # LaTeX output (for thesis integration)
    tex_parts = [
        '% Auto-generated tables (do not edit manually) ',
        make_descriptive_table_tex(agg),
        '',
        make_pvalues_table_tex(),
        '',
        make_cliffs_delta_table_tex()
    ]
    OUT_PATH_TEX.write_text('\n'.join(tex_parts) + '\n', encoding='utf-8')
    print(f"Wrote {OUT_PATH_TEX}")

if __name__ == '__main__':
    main()
