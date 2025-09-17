import os
import json
import argparse
from datetime import datetime
import base64


def read_jsonl(path):
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


def embed_image(path):
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    ext = os.path.splitext(path)[1].lower().lstrip('.')
    mime = 'image/png' if ext == 'png' else 'image/jpeg'
    return f"data:{mime};base64,{b64}"


def html_escape(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('experiment_id')
    args = p.parse_args()

    exp = args.experiment_id
    base = os.path.join('data', 'results', exp)
    logs = os.path.join(base, 'logs', 'events.jsonl')
    timeline_png = os.path.join(base, 'monitor', 'timeline.png')

    events = read_jsonl(logs)
    events_sorted = sorted(events, key=lambda e: e.get('timestamp', ''))

    # Extract stage summaries
    stages = [
        ("PREPROCESS", "PREPROCESS_START", "PREPROCESS_DONE"),
        ("TRAIN_RF", "TRAIN_RF_START", "MODEL_TRAINED_RF"),
        ("EVAL_RF", "EVAL_RF_START", "EVAL_DONE_RF"),
        ("TRAIN_SVM", "TRAIN_SVM_START", "MODEL_TRAINED_SVM"),
        ("EVAL_SVM", "EVAL_SVM_START", "EVAL_DONE_SVM"),
    ]

    def find_event(name):
        return next((e for e in events_sorted if e.get('event') == name), None)

    stage_rows = []
    for label, start_ev, end_ev in stages:
        s = find_event(start_ev)
        e = find_event(end_ev)
        metrics = ''
        if end_ev.startswith('MODEL_TRAINED') and e:
            tm = e.get('train_metrics') or {}
            metrics = f"tiempo={tm.get('time_ms')} ms, cpu_prom={tm.get('cpu_avg')} %, mem_pico={tm.get('mem_peak_mb')} MB"
        if end_ev.startswith('EVAL_DONE') and e:
            em = e.get('eval_metrics') or {}
            metrics = f"accuracy={em.get('accuracy')}, f1={em.get('f1')}"
        stage_rows.append({
            'stage': label,
            'start': s.get('timestamp') if s else None,
            'end': e.get('timestamp') if e else None,
            'metrics': metrics,
        })

    # Build HTML
    os.makedirs(os.path.join(base, 'report'), exist_ok=True)
    report_path = os.path.join(base, 'report', 'report.html')

    timeline_data = embed_image(timeline_png)

    css = (
        "body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,sans-serif;margin:24px;}"
        "h1,h2{margin:8px 0;} .card{border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:12px 0;}"
        "table{border-collapse:collapse;width:100%;} th,td{border:1px solid #e5e7eb;padding:8px;text-align:left;}"
        ".muted{color:#6b7280;font-size:12px}"
    )

    html = [
        "<!doctype html>",
        '<html lang="es">',
        '<head>',
        '<meta charset="utf-8"/>',
        f'<title>Reporte Experimento {html_escape(exp)}</title>',
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>',
        f'<style>{css}</style>',
        '</head>',
        '<body>',
        f'<h1>Reporte del Experimento: {html_escape(exp)}</h1>',
        f'<div class="muted">Generado: {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")} (UTC)</div>',
        '<div class="card">',
        '<h2>Resumen por etapa</h2>',
        '<table><thead><tr><th>Etapa</th><th>Inicio</th><th>Fin</th><th>Métricas</th></tr></thead><tbody>'
    ]

    for r in stage_rows:
        html.append('<tr>'
                    f'<td>{html_escape(r["stage"])}</td>'
                    f'<td>{html_escape(r["start"]) if r["start"] else ""}</td>'
                    f'<td>{html_escape(r["end"]) if r["end"] else ""}</td>'
                    f'<td>{html_escape(r["metrics"])}</td>'
                    '</tr>')

    html += ['</tbody></table>', '</div>']

    if timeline_data:
        html += ['<div class="card">', '<h2>CPU/Memoria con eventos</h2>',
                 f'<img alt="timeline" style="max-width:100%" src="{timeline_data}"/>', '</div>']
    else:
        html += ['<div class="card muted">No se encontró timeline.png. Ejecuta en modo monitoreado.</div>']

    html += ['</body>', '</html>']

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html))

    print(json.dumps({'report': report_path}))


if __name__ == '__main__':
    main()
