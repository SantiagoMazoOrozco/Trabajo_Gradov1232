#!/usr/bin/env python3
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi import Query
import subprocess
import threading
from io import StringIO
from threading import Lock

import csv


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "results"

# Optional direct energy reading (Linux RAPL). If unavailable, fallback proxy is used.
RAPL_ENERGY_PATHS = [
    Path("/sys/class/powercap/intel-rapl:0/energy_uj"),  # package 0
]
RAPL_LAST_READ: Optional[float] = None  # micro Joules last read
RAPL_LAST_TS: Optional[float] = None    # timestamp seconds
RAPL_DELTA_J: float = 0.0               # accumulated Joules since process start
RAPL_LAST_POWER_W: Optional[float] = None  # instantaneous power (W) computed from last delta

CPU_POWER_W = float(os.environ.get("CPU_POWER_W", "65"))  # fallback nominal TDP (user can export)

def _read_package_energy_j() -> Optional[float]:
    """Attempt to read CPU package energy in Joules via RAPL. Returns None if not available."""
    for p in RAPL_ENERGY_PATHS:
        try:
            if p.exists():
                micro_j = float(p.read_text().strip())  # energy in micro Joules
                return micro_j / 1e6
        except Exception:
            continue
    return None

def update_energy_accumulator():
    """Update accumulated energy delta if RAPL is available (called each /metrics scrape).
    Also derives instantaneous package power (W) from energy delta / time delta.
    """
    global RAPL_LAST_READ, RAPL_LAST_TS, RAPL_DELTA_J, RAPL_LAST_POWER_W
    current = _read_package_energy_j()
    now_ts = time.time()
    if current is None:
        return False  # hardware reading not available
    if RAPL_LAST_READ is None:
        RAPL_LAST_READ = current
        RAPL_LAST_TS = now_ts
        RAPL_LAST_POWER_W = None
        return True
    # Compute deltas (handle counter wrap gracefully)
    if current >= RAPL_LAST_READ:
        delta_j = current - RAPL_LAST_READ
    else:
        delta_j = 0.0
    dt = max(1e-6, now_ts - (RAPL_LAST_TS or now_ts))
    RAPL_DELTA_J += delta_j
    # Instantaneous average power over last interval
    RAPL_LAST_POWER_W = delta_j / dt if delta_j >= 0.0 else None
    RAPL_LAST_READ = current
    RAPL_LAST_TS = now_ts
    return True

app = FastAPI(title="SMA Experiments Dashboard")

# Static mount to serve data files (e.g., report HTMLs and figures)
app.mount("/data", StaticFiles(directory=str(ROOT / "data")), name="data")

templates = Jinja2Templates(directory=str(ROOT / "backend" / "web" / "templates"))

# --- Live experiment state (for near real-time Grafana panels) ---
LIVE_STATE: Dict[str, Any] = {
    "active": False,
    "start_ts": 0.0,
    "end_ts": 0.0,
    "last_ts": 0.0,
    "duration": 0,  # seconds planned
    "counter": 0,
    "watts": 0.0,
    "rps": 0.0,
    "manual_stop": False,
}
LIVE_LOCK: Lock = Lock()

def _compute_live_values(now_ts: float) -> None:
    """Compute demo live values from timestamps; no background thread required."""
    import math
    with LIVE_LOCK:
        start = float(LIVE_STATE.get("start_ts") or 0.0)
        end = float(LIVE_STATE.get("end_ts") or 0.0)
        manual_stop = bool(LIVE_STATE.get("manual_stop"))
        active = (start > 0.0) and (now_ts < end) and (not manual_stop)
        LIVE_STATE["active"] = active
        if active:
            elapsed = now_ts - start
            phase = elapsed / 5.0
            watts = CPU_POWER_W * (0.6 + 0.3 * math.sin(phase))
            rps = 1000.0 + 500.0 * math.sin(phase + 1.2)
            LIVE_STATE["last_ts"] = now_ts
            LIVE_STATE["counter"] = int(LIVE_STATE.get("counter") or 0) + 1
            LIVE_STATE["watts"] = max(0.0, float(watts))
            LIVE_STATE["rps"] = max(0.0, float(rps))


def _read_aggregate_csv() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    csv_path = DATA_DIR / "aggregate_metrics.csv"
    if not csv_path.exists():
        return rows
    with csv_path.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)
    return rows


def _list_experiment_ids(rows: List[Dict[str, Any]]) -> List[str]:
    ids = []
    seen = set()
    for r in rows:
        exp = r.get("experimentId") or ""
        if exp and exp not in seen:
            seen.add(exp)
            ids.append(exp)
    # If CSV empty, try filesystem
    if not ids and DATA_DIR.exists():
        for p in DATA_DIR.iterdir():
            if p.is_dir() and (p / "report" / "report.html").exists():
                ids.append(p.name)
    return sorted(ids)


def _group_for_experiment(rows: List[Dict[str, Any]], exp_id: str) -> str:
    for r in rows:
        if r.get("experimentId") == exp_id:
            return r.get("group") or ""
    # Heuristic from name
    name = exp_id.lower()
    if "control" in name:
        return "control"
    if "treatment" in name:
        return "treatment"
    return ""


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}

LAST_OUTPUT_BUFFER: StringIO = StringIO()
LAST_OUTPUT_LOCK = threading.Lock()

def _append_output(text: str):
    with LAST_OUTPUT_LOCK:
        LAST_OUTPUT_BUFFER.write(text + "\n")

def _get_last_output() -> str:
    with LAST_OUTPUT_LOCK:
        return LAST_OUTPUT_BUFFER.getvalue()[-8000:]  # limit size

def _run_script(args: list):
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            _append_output(line.rstrip())
        proc.wait()
        _append_output(f"[exit code {proc.returncode}] {'OK' if proc.returncode==0 else 'FAIL'}")
    except Exception as e:
        _append_output(f"[error] {e}")

@app.post("/control/run-single")
def control_run_single(request: Request, group: str = Form(...), seed: int = Form(42)):
    exp_id = f"exp_{int(time.time())}_{group}"
    args = ["bash", "scripts/run_experiment.sh", "--group", group, "--id", exp_id, "--monitor-seconds", "0", "--report"]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return templates.TemplateResponse("control.html", {"request": request, "last_output": _get_last_output(), "started": f"single {exp_id}"})

@app.post("/control/run-batch")
def control_run_batch(request: Request, repeats: int = Form(5), monitor: int = Form(0)):
    args = ["bash", "scripts/run_batch.sh", "--repeats", str(repeats), "--monitor-seconds", str(monitor)]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return templates.TemplateResponse("control.html", {"request": request, "last_output": _get_last_output(), "started": f"batch x{repeats}"})

# --- Simple GET triggers to enable launching from Grafana links ---
@app.get("/trigger/run-single")
def trigger_run_single(group: str = Query("control"), monitor: int = Query(0), report: bool = Query(True), seed: int = Query(None)):
    """Start a single experiment from a GET link (usable from Grafana).
    Accepts optional `seed` query parameter which will be forwarded to the run script as `--seed`.
    """
    exp_id = f"exp_{int(time.time())}_{group}"
    args = [
        "bash", "scripts/run_experiment.sh",
        "--group", group,
        "--id", exp_id,
        "--monitor-seconds", str(monitor)
    ]
    if seed is not None:
        args += ["--seed", str(seed)]
    if report:
        args.append("--report")
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    resp = {"status": "started", "type": "single", "group": group, "id": exp_id}
    if seed is not None:
        resp["seed"] = seed
    return resp

@app.get("/trigger/run-batch")
def trigger_run_batch(repeats: int = Query(5), monitor: int = Query(0)):
    args = ["bash", "scripts/run_batch.sh", "--repeats", str(repeats), "--monitor-seconds", str(monitor)]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return {"status": "started", "type": "batch", "repeats": repeats, "monitor": monitor}

# --- Extra GET triggers to orchestrate from Grafana links ---
@app.get("/trigger/aggregate")
def trigger_aggregate():
    args = ["bash", "scripts/aggregate_metrics.sh"]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return {"status": "started", "type": "aggregate"}

@app.get("/trigger/stats")
def trigger_stats():
    # prefer bash script wrapper if present
    script = ROOT / "scripts" / "stats_analysis.sh"
    if script.exists():
        args = ["bash", str(script)]
    else:
        args = ["python3", "python-analysis/stats_analysis.py"]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return {"status": "started", "type": "stats"}

@app.get("/trigger/run-jade")
def trigger_run_jade():
    args = ["bash", "scripts/run_jade_experiment.sh"]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return {"status": "started", "type": "jade"}

@app.get("/trigger/live-start")
def trigger_live_start(seconds: int = Query(60)):
    # Arm stateless live window
    now_ts = time.time()
    secs = max(0, int(seconds))
    with LIVE_LOCK:
        LIVE_STATE["start_ts"] = now_ts
        LIVE_STATE["end_ts"] = now_ts + secs if secs > 0 else now_ts + 60
        LIVE_STATE["duration"] = secs if secs > 0 else 60
        LIVE_STATE["manual_stop"] = False
        LIVE_STATE["active"] = True
        LIVE_STATE["last_ts"] = now_ts
        LIVE_STATE["counter"] = 0
        LIVE_STATE["watts"] = 0.0
        LIVE_STATE["rps"] = 0.0
    return {"status": "started", "type": "live", "seconds": int(LIVE_STATE["duration"])}

@app.get("/trigger/live-stop")
def trigger_live_stop():
    # Mark inactive; worker loop will exit on next tick if duration=0 not set; force inactive
    with LIVE_LOCK:
        LIVE_STATE["active"] = False
        LIVE_STATE["manual_stop"] = True
        LIVE_STATE["end_ts"] = time.time()
        LIVE_STATE["duration"] = 0
    return {"status": "stopped", "type": "live"}

@app.get("/live/state")
def live_state() -> Dict[str, Any]:
    """Expose current in-memory LIVE_STATE for quick debugging/inspection."""
    with LIVE_LOCK:
        # Return a shallow copy to avoid exposing the internal dict
        return dict(LIVE_STATE)

@app.post("/control/aggregate")
def control_aggregate(request: Request):
    args = ["python3", "python-analysis/aggregate_metrics.py"]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return templates.TemplateResponse("control.html", {"request": request, "last_output": _get_last_output(), "started": "aggregate"})

@app.post("/control/stats")
def control_stats(request: Request):
    args = ["python3", "python-analysis/stats_analysis.py"]
    threading.Thread(target=_run_script, args=(args,), daemon=True).start()
    return templates.TemplateResponse("control.html", {"request": request, "last_output": _get_last_output(), "started": "stats"})


@app.get("/pid")
def pid() -> Dict[str, Any]:
    return {"pid": os.getpid()}


@app.get("/")
def home(request: Request) -> HTMLResponse:
    rows = _read_aggregate_csv()
    exp_ids = _list_experiment_ids(rows)
    items = []
    for eid in exp_ids:
        items.append({
            "id": eid,
            "group": _group_for_experiment(rows, eid),
            "has_report": (DATA_DIR / eid / "report" / "report.html").exists(),
        })
    stats_md = (DATA_DIR / "stats_summary.md").read_text("utf-8") if (DATA_DIR / "stats_summary.md").exists() else None
    return templates.TemplateResponse("experiments.html", {
        "request": request,
        "experiments": items,
        "stats_md": stats_md,
    })


@app.get("/tour")
def tour(request: Request) -> HTMLResponse:
    """Pequeño recorrido guiado con enlaces directos a acciones comunes."""
    return templates.TemplateResponse("tour.html", {"request": request})


@app.get("/control")
def control_panel(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("control.html", {"request": request, "last_output": _get_last_output()})


@app.get("/experiments/{exp_id}")
def experiment_detail(request: Request, exp_id: str) -> HTMLResponse:
    rows = _read_aggregate_csv()
    filtered = [r for r in rows if r.get("experimentId") == exp_id]
    if not filtered:
        # Fallback: show links if only filesystem exists
        if not (DATA_DIR / exp_id).exists():
            raise HTTPException(status_code=404, detail="Experiment not found")
    report_url = None
    if (DATA_DIR / exp_id / "report" / "report.html").exists():
        report_url = f"/data/results/{exp_id}/report/report.html"
    return templates.TemplateResponse("experiment_detail.html", {
        "request": request,
        "exp_id": exp_id,
        "group": _group_for_experiment(rows, exp_id),
        "rows": filtered,
        "report_url": report_url,
    })


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    # Prometheus exposition format text (OpenMetrics v0.0.4 compatible)
    # 1) Update direct energy accumulator if available (Linux RAPL). Fallback to proxy metrics below.
    rapl_ok = update_energy_accumulator()
    # Pull last batch rows if present
    rows = _read_aggregate_csv()
    # Compute simple aggregates for demo
    try:
        train_durations = [float(r.get("time_ms") or 0.0) for r in rows if (r.get("stage") or "").startswith("TRAIN") and (r.get("time_ms") or "")]  # ms
    except Exception:
        train_durations = []
    train_sec = sum(train_durations) / 1000.0 if train_durations else 0.0
    # Accuracy/F1 by group from latest EVAL_* per group
    def last_eval_by_group(metric: str) -> Dict[str, float]:
        vals: Dict[str, float] = {"control": 0.0, "treatment": 0.0}
        seen = set()
        for r in reversed(rows):
            if (r.get("stage") or "").startswith("EVAL"):
                g = (r.get("group") or "").lower()
                if g in ("control", "treatment") and g not in seen:
                    try:
                        vals[g] = float(r.get(metric) or 0.0)
                        seen.add(g)
                    except Exception:
                        pass
                if len(seen) == 2:
                    break
        return vals

    acc_by_group = last_eval_by_group("accuracy")
    f1_by_group = last_eval_by_group("f1")

    # Resource/efficiency latest TRAIN_* means (approx): use last TRAIN_* row
    def last_train_metric(name: str) -> float:
        for r in reversed(rows):
            if (r.get("stage") or "").startswith("TRAIN") and (r.get(name) or ""):
                try:
                    return float(r.get(name))
                except Exception:
                    return 0.0
        return 0.0

    cpu_avg_last = last_train_metric("cpu_avg")
    mem_peak_last = last_train_metric("mem_peak_mb")
    rps_last = last_train_metric("records_per_s")
    mbs_last = last_train_metric("data_mb_per_s")
    # Watts-based metrics (preferred)
    avg_watts_last = last_train_metric("avg_watts")
    watts_per_mb_last = last_train_metric("watts_per_mb")
    watts_per_record_last = last_train_metric("watts_per_record")

    # Per‑algorithm latest TRAIN_* metrics
    def last_train_row_by_algo() -> Dict[str, Dict[str, Any]]:
        latest: Dict[str, Dict[str, Any]] = {}
        for r in reversed(rows):
            stg = (r.get("stage") or "").upper()
            if stg.startswith("TRAIN_"):
                algo = stg.split("_", 1)[1].lower()
                if algo and algo not in latest:
                    latest[algo] = r
        return latest

    last_by_algo = last_train_row_by_algo()

    # Counts
    experiments_total = len({r.get("experimentId") for r in rows if r.get("experimentId")})
    content = []
    content.append("# HELP train_duration_seconds Total training duration (sum) in seconds")
    content.append("# TYPE train_duration_seconds gauge")
    content.append(f"train_duration_seconds {train_sec:.3f}")
    # Accuracy/F1 per group (labeled)
    content.append("# HELP eval_accuracy_by_group Last evaluation accuracy by group")
    content.append("# TYPE eval_accuracy_by_group gauge")
    for g, v in acc_by_group.items():
        content.append(f'eval_accuracy_by_group{{group="{g}"}} {v:.6f}')
    content.append("# HELP eval_f1_by_group Last evaluation F1 by group")
    content.append("# TYPE eval_f1_by_group gauge")
    for g, v in f1_by_group.items():
        content.append(f'eval_f1_by_group{{group="{g}"}} {v:.6f}')

    # Backward-compat overall series expected by sma-overview: eval_accuracy, eval_f1
    try:
        acc_vals = [v for v in acc_by_group.values() if v is not None]
        acc_overall = sum(acc_vals) / len(acc_vals) if acc_vals else 0.0
    except Exception:
        acc_overall = 0.0
    try:
        f1_vals = [v for v in f1_by_group.values() if v is not None]
        f1_overall = sum(f1_vals) / len(f1_vals) if f1_vals else 0.0
    except Exception:
        f1_overall = 0.0
    content.append("# HELP eval_accuracy Last evaluation accuracy (overall mean across groups)")
    content.append("# TYPE eval_accuracy gauge")
    content.append(f"eval_accuracy {acc_overall:.6f}")
    content.append("# HELP eval_f1 Last evaluation F1 (overall mean across groups)")
    content.append("# TYPE eval_f1 gauge")
    content.append(f"eval_f1 {f1_overall:.6f}")

    # Efficiency / resources (latest train)
    content.append("# HELP train_cpu_avg_percent_last CPU percent average during last training")
    content.append("# TYPE train_cpu_avg_percent_last gauge")
    content.append(f"train_cpu_avg_percent_last {cpu_avg_last:.3f}")
    content.append("# HELP train_mem_peak_mb_last Peak memory (MB) during last training")
    content.append("# TYPE train_mem_peak_mb_last gauge")
    content.append(f"train_mem_peak_mb_last {mem_peak_last:.3f}")
    content.append("# HELP train_records_per_s_last Records per second during last training")
    content.append("# TYPE train_records_per_s_last gauge")
    content.append(f"train_records_per_s_last {rps_last:.3f}")
    content.append("# HELP train_data_mb_per_s_last Data MB per second during last training")
    content.append("# TYPE train_data_mb_per_s_last gauge")
    content.append(f"train_data_mb_per_s_last {mbs_last:.3f}")
    # Watts-focused metrics (replace prior Joule-focused gauges)
    content.append("# HELP train_avg_watts_last Average power (W) during last training stage (proxy or direct)")
    content.append("# TYPE train_avg_watts_last gauge")
    content.append(f"train_avg_watts_last {avg_watts_last:.6f}")
    content.append("# HELP train_watts_per_mb_last Average power normalized by MB/s processed in last train stage (W/MB)")
    content.append("# TYPE train_watts_per_mb_last gauge")
    content.append(f"train_watts_per_mb_last {watts_per_mb_last:.6f}")
    content.append("# HELP train_watts_per_record_last Average power normalized by records/s processed in last train stage (W/record)")
    content.append("# TYPE train_watts_per_record_last gauge")
    content.append(f"train_watts_per_record_last {watts_per_record_last:.6f}")

    # 2) Direct CPU package energy via RAPL (if available)
    if rapl_ok and RAPL_LAST_READ is not None:
        # Prefer exposing instantaneous power if available
        if RAPL_LAST_POWER_W is not None:
            content.append("# HELP cpu_package_power_w Instantaneous CPU package power derived from RAPL delta")
            content.append("# TYPE cpu_package_power_w gauge")
            content.append(f"cpu_package_power_w {RAPL_LAST_POWER_W:.6f}")
        # Still expose cumulative energy internally if needed for future derivations (commented out to satisfy 'no Joules')
        # content.append("# HELP cpu_package_energy_j Accumulated CPU package energy since process start (RAPL)")
        # content.append("# TYPE cpu_package_energy_j counter")
        # content.append(f"cpu_package_energy_j {RAPL_DELTA_J:.6f}")
    else:
        # Expose proxy instantaneous power based on last train CPU avg and env CPU_POWER_W
        try:
            proxy_avg_watts = CPU_POWER_W * (cpu_avg_last / 100.0)
        except Exception:
            proxy_avg_watts = 0.0
        content.append("# HELP cpu_power_w_proxy Estimated CPU power based on TDP and cpu_avg (fallback)")
        content.append("# TYPE cpu_power_w_proxy gauge")
        content.append(f"cpu_power_w_proxy {proxy_avg_watts:.6f}")
    # Per‑algo gauges
    if last_by_algo:
        content.append("# HELP train_duration_seconds_last Training duration (last) per algorithm in seconds")
        content.append("# TYPE train_duration_seconds_last gauge")
        for algo, r in last_by_algo.items():
            try:
                v = float(r.get("time_ms") or 0.0) / 1000.0
            except Exception:
                v = 0.0
            content.append(f'train_duration_seconds_last{{algo="{algo}"}} {v:.3f}')

        def _emit_algo_metric(name_csv: str, metric_name: str, fmt: str = ".3f"):
            content.append(f"# HELP {metric_name} Last training {name_csv} per algorithm")
            content.append(f"# TYPE {metric_name} gauge")
            for algo, r in last_by_algo.items():
                try:
                    v = float(r.get(name_csv) or 0.0)
                except Exception:
                    v = 0.0
                content.append(f'{metric_name}{{algo="{algo}"}} {v:{fmt}}')

        _emit_algo_metric("cpu_avg", "train_cpu_avg_percent_last_by_algo")
        _emit_algo_metric("mem_peak_mb", "train_mem_peak_mb_last_by_algo")
        _emit_algo_metric("records_per_s", "train_records_per_s_last_by_algo")
        _emit_algo_metric("data_mb_per_s", "train_data_mb_per_s_last_by_algo")
        _emit_algo_metric("avg_watts", "train_avg_watts_last_by_algo", fmt=".6f")
        _emit_algo_metric("watts_per_mb", "train_watts_per_mb_last_by_algo", fmt=".6f")
        _emit_algo_metric("watts_per_record", "train_watts_per_record_last_by_algo", fmt=".6f")
    # Dummy failure/recoveries counters (set to 0 unless instrumented)
    # Resilience metrics from RESILIENCE rows if present
    def _safe_int(x: Any) -> int:
        try:
            if x is None or x == "":
                return 0
            return int(float(x))
        except Exception:
            return 0

    failures_total_val = 0
    recoveries_total_val = 0
    for r in rows:
        if (r.get("stage") or "").startswith("RESILIENCE"):
            failures_total_val += _safe_int(r.get("fault_injected_count"))
            recoveries_total_val += _safe_int(r.get("fault_recovered_count"))

    recovery_rate = (recoveries_total_val / failures_total_val) if failures_total_val > 0 else 0.0

    content.append("# HELP failures_total Total failures observed")
    content.append("# TYPE failures_total counter")
    content.append(f"failures_total {failures_total_val}")
    content.append("# HELP recoveries_total Total auto-recoveries observed")
    content.append("# TYPE recoveries_total counter")
    content.append(f"recoveries_total {recoveries_total_val}")
    content.append("# HELP recovery_rate Overall recovery success rate (0..1)")
    content.append("# TYPE recovery_rate gauge")
    content.append(f"recovery_rate {recovery_rate:.6f}")
    content.append("# HELP experiments_total Total number of experiments discovered")
    content.append("# TYPE experiments_total gauge")
    content.append(f"experiments_total {experiments_total}")

    # --- Efficiency derived metrics from latest TRAIN_* row ---
    eff_cpu = last_train_metric("efficiency_cpu_rps_per_pct")
    eff_mem = last_train_metric("efficiency_mem_rps_per_mb")
    content.append("# HELP train_efficiency_cpu_rps_per_pct_last Efficiency CPU (records/s por %CPU) último entrenamiento")
    content.append("# TYPE train_efficiency_cpu_rps_per_pct_last gauge")
    content.append(f"train_efficiency_cpu_rps_per_pct_last {eff_cpu:.6f}")
    content.append("# HELP train_efficiency_mem_rps_per_mb_last Efficiency Memoria (records/s por MB) último entrenamiento")
    content.append("# TYPE train_efficiency_mem_rps_per_mb_last gauge")
    content.append(f"train_efficiency_mem_rps_per_mb_last {eff_mem:.6f}")

    # --- Stage-specific (PREPROCESS/EVAL) latest CPU/Mem metrics ---
    def last_stage_metric(stage_prefix: str, name: str) -> float:
        for r in reversed(rows):
            stg = (r.get("stage") or "").upper()
            if stg.startswith(stage_prefix.upper()) and (r.get(name) or ""):
                try:
                    return float(r.get(name))
                except Exception:
                    return 0.0
        return 0.0

    pre_cpu = last_stage_metric("PREPROCESS", "cpu_avg")
    pre_mem = last_stage_metric("PREPROCESS", "mem_peak_mb")
    eval_cpu = last_stage_metric("EVAL", "cpu_avg")
    eval_mem = last_stage_metric("EVAL", "mem_peak_mb")

    content.append("# HELP preprocess_cpu_avg_percent_last CPU promedio en la última etapa de preprocesamiento")
    content.append("# TYPE preprocess_cpu_avg_percent_last gauge")
    content.append(f"preprocess_cpu_avg_percent_last {pre_cpu:.6f}")
    content.append("# HELP preprocess_mem_peak_mb_last Memoria pico (MB) en la última etapa de preprocesamiento")
    content.append("# TYPE preprocess_mem_peak_mb_last gauge")
    content.append(f"preprocess_mem_peak_mb_last {pre_mem:.6f}")
    content.append("# HELP eval_cpu_avg_percent_last CPU promedio en la última etapa de evaluación")
    content.append("# TYPE eval_cpu_avg_percent_last gauge")
    content.append(f"eval_cpu_avg_percent_last {eval_cpu:.6f}")
    content.append("# HELP eval_mem_peak_mb_last Memoria pico (MB) en la última etapa de evaluación")
    content.append("# TYPE eval_mem_peak_mb_last gauge")
    content.append(f"eval_mem_peak_mb_last {eval_mem:.6f}")

    # --- Experimental live progress metrics ---
    # Parse latest events.jsonl (if exists) to infer current stage of latest experiment
    latest_exp = None
    latest_stage = None
    latest_stage_start_ts = None
    events_dir = DATA_DIR
    try:
        # Determine most recent experiment directory by mtime
        candidates = []
        for p in events_dir.iterdir():
            if p.is_dir() and (p / "logs" / "events.jsonl").exists():
                candidates.append((p.stat().st_mtime, p))
        if candidates:
            candidates.sort(reverse=True)
            latest_exp_path = candidates[0][1]
            latest_exp = latest_exp_path.name
            ev_file = latest_exp_path / "logs" / "events.jsonl"
            lines = ev_file.read_text(encoding="utf-8").strip().splitlines()
            if lines:
                # Walk lines reverse to find last meaningful stage marker
                for raw in reversed(lines):
                    try:
                        import json as _json
                        obj = _json.loads(raw)
                        ev = obj.get("event") or ""
                        ts = obj.get("timestamp")
                        if ev.startswith("MODEL_TRAINED_"):
                            latest_stage = ev
                            latest_stage_start_ts = ts
                            break
                        elif ev.startswith("TRAIN_") and ev.endswith("_START"):
                            latest_stage = ev
                            latest_stage_start_ts = ts
                            break
                        elif ev.startswith("EVAL_DONE_"):
                            latest_stage = ev
                            latest_stage_start_ts = ts
                            break
                        elif ev.startswith("EVAL_") and ev.endswith("_START"):
                            latest_stage = ev
                            latest_stage_start_ts = ts
                            break
                        elif ev.endswith("PREPROCESS_DONE"):
                            latest_stage = ev
                            latest_stage_start_ts = ts
                            break
                    except Exception:
                        continue
        # Compute elapsed seconds if timestamp parseable
        elapsed = 0.0
        if latest_stage_start_ts:
            try:
                from datetime import datetime
                dt = datetime.strptime(latest_stage_start_ts, "%Y-%m-%dT%H:%M:%SZ")
                elapsed = time.time() - dt.timestamp()
            except Exception:
                pass
        if latest_exp:
            content.append("# HELP experiment_last_id Último experimento detectado")
            content.append("# TYPE experiment_last_id gauge")
            # Expose length hash as numerical surrogate (not ideal but keeps type gauge)
            content.append(f"experiment_last_id {len(latest_exp)}")
        if latest_stage:
            content.append("# HELP experiment_current_stage_idx Índice simbólico de la etapa actual (hash reducido)")
            content.append("# TYPE experiment_current_stage_idx gauge")
            content.append(f"experiment_current_stage_idx {abs(hash(latest_stage)) % 10000}")
            content.append("# HELP experiment_current_stage_elapsed_seconds Segundos transcurridos desde la marca de la etapa detectada")
            content.append("# TYPE experiment_current_stage_elapsed_seconds gauge")
            content.append(f"experiment_current_stage_elapsed_seconds {elapsed:.2f}")
    except Exception:
        pass

    # --- Orchestration / Multi‑Agent status metrics ---
    # Goal: reflect creation/activation of multi‑agent platform and ML ingress steps.
    try:
        jade_root = ROOT / "data" / "results" / "_jade_logs"
        platform_up = 1 if jade_root.exists() else 0
        # Agents count (if a manifest exists)
        agents_cnt = 0
        try:
            import json as _json
            manifest = jade_root / "agents.json"
            if manifest.exists():
                data = _json.loads(manifest.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    agents_cnt = len(data)
                elif isinstance(data, dict) and "agents" in data:
                    agents_cnt = len(data.get("agents") or [])
        except Exception:
            agents_cnt = 0
        # Messages total approximated by line count in messages.log (monotonic)
        messages_total = 0
        msg_log = jade_root / "messages.log"
        if msg_log.exists():
            try:
                # Fast line count
                with msg_log.open("rb") as f:
                    messages_total = sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 16), b""))
            except Exception:
                messages_total = 0

        # Current orchestration stage name from events.jsonl (AGENTS_*, ORCH_*, ML_INGEST_*)
        orch_stage = None
        orch_elapsed = 0.0
        try:
            events = []
            if DATA_DIR.exists():
                for p in DATA_DIR.iterdir():
                    if p.is_dir() and (p / "logs" / "events.jsonl").exists():
                        events.append((p.stat().st_mtime, p))
            if events:
                events.sort(reverse=True)
                ev_file = events[0][1] / "logs" / "events.jsonl"
                lines = ev_file.read_text(encoding="utf-8").strip().splitlines()
                for raw in reversed(lines):
                    try:
                        import json as _json
                        o = _json.loads(raw)
                        ev = (o.get("event") or "").upper()
                        ts = o.get("timestamp")
                        if ev.startswith("AGENTS_") or ev.startswith("ORCH_") or ev.startswith("ML_INGEST_") or ev.startswith("PREPROCESS"):
                            orch_stage = ev
                            if ts:
                                from datetime import datetime
                                try:
                                    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                                    orch_elapsed = time.time() - dt.timestamp()
                                except Exception:
                                    orch_elapsed = 0.0
                            break
                    except Exception:
                        continue
        except Exception:
            pass

    # Emit orchestration metrics
        content.append("# HELP orchestration_platform_up Multi-agent platform up (1) or down (0)")
        content.append("# TYPE orchestration_platform_up gauge")
        content.append(f"orchestration_platform_up {platform_up}")

        content.append("# HELP orchestration_agents_count Registered agents (if known)")
        content.append("# TYPE orchestration_agents_count gauge")
        content.append(f"orchestration_agents_count {agents_cnt}")

        content.append("# HELP orchestration_messages_total Total orchestration messages observed (approx line count)")
        content.append("# TYPE orchestration_messages_total counter")
        content.append(f"orchestration_messages_total {messages_total}")

        if orch_stage:
            content.append("# HELP orchestration_current_stage_idx Hash index for current orchestration stage")
            content.append("# TYPE orchestration_current_stage_idx gauge")
            content.append(f"orchestration_current_stage_idx {abs(hash(orch_stage)) % 10000}")
            content.append("# HELP orchestration_current_stage_info Current orchestration stage as label")
            content.append("# TYPE orchestration_current_stage_info gauge")
            # Expose a label with the stage name set to 1
            safe = orch_stage.replace('"', "'")
            content.append(f'orchestration_current_stage_info{{name="{safe}"}} 1')
            content.append("# HELP orchestration_current_stage_elapsed_seconds Seconds since the orchestration stage timestamp")
            content.append("# TYPE orchestration_current_stage_elapsed_seconds gauge")
            content.append(f"orchestration_current_stage_elapsed_seconds {orch_elapsed:.2f}")

        # ML ingestion proxy metrics (using PREPROCESS as ingestion)
        try:
            last_pre_ms = 0.0
            for r in reversed(rows):
                if (r.get("stage") or "").startswith("PREPROCESS") and (r.get("time_ms") or ""):
                    last_pre_ms = float(r.get("time_ms") or 0.0)
                    break
            content.append("# HELP ml_ingest_duration_seconds_last Duration (s) of last ML ingestion/preprocess stage")
            content.append("# TYPE ml_ingest_duration_seconds_last gauge")
            content.append(f"ml_ingest_duration_seconds_last {last_pre_ms/1000.0:.3f}")
        except Exception:
            pass

        # Message latency (ms) last observed, based on AGENTS_MSG_SENT/AGENTS_MSG_ACK with same id
        try:
            last_latency_ms = 0.0
            if events:
                ev_file = events[0][1] / "logs" / "events.jsonl"
                lines = ev_file.read_text(encoding="utf-8").strip().splitlines()
                last_sent = None
                last_id = None
                for raw in reversed(lines):
                    try:
                        import json as _json
                        o = _json.loads(raw)
                        ev = (o.get("event") or "").upper()
                        ts = o.get("timestamp")
                        mid = o.get("messageId") or o.get("id") or None
                        if ev == "AGENTS_MSG_ACK" and mid and ts:
                            # remember last ack, then search back for its send
                            last_ack_ts = ts
                            last_id = mid
                            # find matching send earlier
                            for raw2 in reversed(lines):
                                try:
                                    o2 = _json.loads(raw2)
                                    if (o2.get("event") or "").upper() == "AGENTS_MSG_SENT" and (o2.get("messageId") or o2.get("id")) == last_id:
                                        ts2 = o2.get("timestamp")
                                        if ts2:
                                            from datetime import datetime
                                            try:
                                                t_ack = datetime.strptime(last_ack_ts, "%Y-%m-%dT%H:%M:%SZ").timestamp()
                                                t_sent = datetime.strptime(ts2, "%Y-%m-%dT%H:%M:%SZ").timestamp()
                                                last_latency_ms = max(0.0, (t_ack - t_sent) * 1000.0)
                                            except Exception:
                                                pass
                                        break
                                except Exception:
                                    continue
                            break
                    except Exception:
                        continue
            content.append("# HELP orchestration_message_latency_ms_last Last observed message latency in ms (send→ack)")
            content.append("# TYPE orchestration_message_latency_ms_last gauge")
            content.append(f"orchestration_message_latency_ms_last {last_latency_ms:.3f}")
        except Exception:
            pass
    except Exception:
        # Swallow orchestration metric errors silently to not break scraping
        pass
    # --- Live experiment metrics ---
    try:
        now_ts = time.time()
        # Update stateless live values on every scrape
        _compute_live_values(now_ts)
        with LIVE_LOCK:
            active_flag = bool(LIVE_STATE.get("active"))
            start_ts = float(LIVE_STATE.get("start_ts") or 0.0)
            watts = float(LIVE_STATE.get("watts") or 0.0)
            rps = float(LIVE_STATE.get("rps") or 0.0)
        elapsed = max(0.0, now_ts - start_ts) if active_flag and start_ts else 0.0
        content.append("# HELP live_experiment_active Live mode active (1) or not (0)")
        content.append("# TYPE live_experiment_active gauge")
        content.append(f"live_experiment_active {1 if active_flag else 0}")
        content.append("# HELP live_elapsed_seconds Elapsed seconds since live experiment started")
        content.append("# TYPE live_elapsed_seconds gauge")
        content.append(f"live_elapsed_seconds {elapsed:.3f}")
        content.append("# HELP live_avg_watts Instantaneous (demo) power during live experiment")
        content.append("# TYPE live_avg_watts gauge")
        content.append(f"live_avg_watts {watts:.6f}")
        content.append("# HELP live_records_per_s Instantaneous (demo) records/s during live experiment")
        content.append("# TYPE live_records_per_s gauge")
        content.append(f"live_records_per_s {rps:.6f}")
    except Exception:
        pass
    return PlainTextResponse("\n".join(content) + "\n", media_type="text/plain; version=0.0.4")


# --- Simple state endpoints for tooling/UI helpers ---
@app.get("/state/api-base")
def state_api_base(request: Request) -> Dict[str, Any]:
    """Return the recommended API base URL for Grafana/links.
    Priority:
    1) Respect X-Forwarded-* headers if present (behind proxy)
    2) Use request Host header (reflects published host:port when called from host)
    3) Fallback to persisted state files
    """
    # 1) X-Forwarded headers (common when behind reverse proxy)
    xf_proto = request.headers.get("x-forwarded-proto")
    xf_host = request.headers.get("x-forwarded-host")
    if xf_host:
        scheme = (xf_proto or request.url.scheme or "http").split(",")[0].strip()
        return {"apiBase": f"{scheme}://{xf_host}"}

    # 2) Host header from the incoming request
    host = request.headers.get("host")
    if host:
        scheme = request.url.scheme or "http"
        return {"apiBase": f"{scheme}://{host}"}

    # 3) Fallback to persisted state files
    state_dir = ROOT / "data" / "results" / "_server_state"
    port: Optional[int] = None
    try:
        txt = state_dir / "backend_host_port.txt"
        if txt.exists():
            # Wrap EIO or other FS errors gracefully
            port = int((txt.read_text(encoding="utf-8")).strip())
    except Exception:
        port = None
    if port is None:
        try:
            import json as _json
            j = state_dir / "uvicorn_dashboard.json"
            if j.exists():
                data = _json.loads(j.read_text(encoding="utf-8"))
                port = int(data.get("port")) if data and data.get("port") else None
        except Exception:
            port = None
    if port is None:
        port = 8000
    # Default to localhost when no host header available
    return {"apiBase": f"http://localhost:{port}"}


# --- Stub experiment workflow endpoints ---

@app.post("/preprocess")
def preprocess(req: Dict[str, Any]):
    """Stub preprocessing endpoint returning a prepRef.
    Expects JSON with experimentId and payload.prepConfig; ignores details.
    """
    exp_id = req.get("experimentId") or "exp_unknown"
    prep_ref = f"prep_{exp_id}_v1"
    return {"status": "ok", "payload": {"prepRef": prep_ref}}


@app.post("/train")
def train(req: Dict[str, Any]):
    """Stub training endpoint returning a modelRef and fake train metrics.
    Request payload should include algo and seed; hyperparams optionally nested.
    """
    exp_id = req.get("experimentId") or "exp_unknown"
    payload = req.get("payload") or {}
    algo = payload.get("algo") or "MODEL"
    hyper = payload.get("hyperparams") or {}
    seed = payload.get("seed") or 0
    model_ref = f"{algo.lower()}_{exp_id}_model"
    # --- Synthetic metric generation (deterministic from seed) ---
    cpu_avg = (seed * 7 % 50) + 30              # 30-79 %CPU avg
    time_ms = (seed * 13 % 500) + 500           # 500-999 ms duration
    mem_peak_mb = (seed * 17 % 200) + 100       # 100-299 MB peak
    records_per_s = round(1000.0 / (time_ms / 1000.0), 2)  # inversely proportional to duration
    duration_s = time_ms / 1000.0

    # --- Data size heuristics (derive MB processed & data_mb_per_s) ---
    # Use synthetic dataset size divided by line count for avg bytes per record.
    dataset_path = ROOT / "data" / "raw" / "synthetic_classification.csv"
    mb_processed = None
    data_mb_per_s = None
    n_train = None
    avg_record_bytes = None
    try:
        if dataset_path.exists():
            file_bytes = dataset_path.stat().st_size
            with dataset_path.open('r', encoding='utf-8', errors='ignore') as f:
                # Count lines (excluding header) cheaply; cap to avoid huge memory
                lines = 0
                for i, _ in enumerate(f):
                    pass
                lines = i + 1 if 'i' in locals() else 0
            # Assume first line is header; subtract one if lines>1
            if lines > 1:
                record_count = lines - 1
                avg_record_bytes = file_bytes / max(1, record_count)
                # Approx number of training records processed (assume full dataset)
                n_train = record_count
                mb_total = file_bytes / 1_000_000.0
                mb_processed = round(mb_total, 6)
                data_mb_per_s = round(mb_total / duration_s, 6)
            else:
                # Fallback single record assumptions
                n_train = int(records_per_s * duration_s)
                mb_processed = (file_bytes / 1_000_000.0)
                data_mb_per_s = round(mb_processed / duration_s, 6) if duration_s > 0 else None
        else:
            n_train = int(records_per_s * duration_s)
            mb_processed = round((records_per_s * duration_s * 256) / 1_000_000.0, 6)  # assume 256 B/record
            data_mb_per_s = round(mb_processed / duration_s, 6) if duration_s > 0 else None
    except Exception:
        n_train = int(records_per_s * duration_s)
        mb_processed = round((records_per_s * duration_s * 256) / 1_000_000.0, 6)
        data_mb_per_s = round(mb_processed / duration_s, 6) if duration_s > 0 else None

    # --- Watts estimation ---
    # Prefer direct RAPL instantaneous power if available (global RAPL_LAST_POWER_W updated on /metrics scrape).
    # For training metric snapshot we approximate using CPU avg percent * nominal TDP (CPU_POWER_W env, default 65).
    try:
        cpu_nominal = CPU_POWER_W
        avg_watts = round(cpu_nominal * (cpu_avg / 100.0), 6)
    except Exception:
        avg_watts = 0.0

    watts_per_mb = None
    if data_mb_per_s and data_mb_per_s > 0:
        watts_per_mb = round(avg_watts / data_mb_per_s, 6)
    watts_per_record = None
    if records_per_s and records_per_s > 0:
        watts_per_record = round(avg_watts / records_per_s, 6)

    # --- Efficiency derived metrics ---
    efficiency_cpu_rps_per_pct = None
    try:
        efficiency_cpu_rps_per_pct = round(records_per_s / cpu_avg, 6)
    except Exception:
        pass
    efficiency_mem_rps_per_mb = None
    try:
        efficiency_mem_rps_per_mb = round(records_per_s / mem_peak_mb, 6)
    except Exception:
        pass

    train_metrics = {
        "cpu_avg": cpu_avg,
        "time_ms": time_ms,
        "mem_peak_mb": mem_peak_mb,
        "records_per_s": records_per_s,
        "n_train": n_train,
        "mb_processed": mb_processed,
        "data_mb_per_s": data_mb_per_s,
        "avg_watts": avg_watts,
        "watts_per_mb": watts_per_mb,
        "watts_per_record": watts_per_record,
        "efficiency_cpu_rps_per_pct": efficiency_cpu_rps_per_pct,
        "efficiency_mem_rps_per_mb": efficiency_mem_rps_per_mb,
    }
    return {"status": "ok", "payload": {"modelRef": model_ref, "algo": algo, "hyperparams": hyper, "train_metrics": train_metrics}}


@app.post("/evaluate")
def evaluate(req: Dict[str, Any]):
    """Stub evaluation endpoint returning accuracy & f1 and confusion matrix."""
    payload = req.get("payload") or {}
    model_ref = payload.get("modelRef") or "model_unknown"
    # Fake metrics derived from model_ref hash for stability
    h = sum(ord(c) for c in model_ref)
    accuracy = round(0.75 + (h % 100) / 1000.0, 4)  # 0.75 .. 0.849
    f1 = round(0.70 + (h % 80) / 1000.0, 4)         # 0.70 .. 0.779
    confusion_matrix = [[42, 8], [7, 43]]  # Static illustrative
    eval_metrics = {"accuracy": accuracy, "f1": f1, "confusion_matrix": confusion_matrix}
    return {"status": "ok", "payload": eval_metrics}
