import argparse
import time
import json
import os
from datetime import datetime
import psutil
import requests
import pandas as pd
import matplotlib.pyplot as plt

API = os.environ.get("API_BASE", "http://127.0.0.1:8000")


def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def load_events(exp_id: str):
    path = f"data/results/{exp_id}/logs/events.jsonl"
    if not os.path.exists(path):
        return []
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except Exception:
                pass
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_id")
    parser.add_argument("--duration", type=float, default=120.0, help="Max seconds to monitor")
    parser.add_argument("--interval", type=float, default=0.25, help="Sampling interval in seconds")
    parser.add_argument("--pid", type=int, default=None, help="Target PID; if not provided, query /pid")
    args = parser.parse_args()

    exp = args.experiment_id
    os.makedirs(f"data/results/{exp}/monitor", exist_ok=True)

    # Resolve PID
    pid = args.pid
    if pid is None:
        try:
            pid = requests.get(f"{API}/pid", timeout=3).json()["pid"]
        except Exception:
            pid = None
    proc = psutil.Process(pid) if pid else psutil.Process()

    # Warm-up CPU percent
    psutil.cpu_percent(interval=None)

    rows = []
    start = time.perf_counter()
    t0 = datetime.utcnow()

    while True:
        elapsed = time.perf_counter() - start
        if elapsed > args.duration:
            break
        try:
            cpu_total = psutil.cpu_percent(interval=None)
            rss = proc.memory_info().rss if proc.is_running() else 0
            rows.append({
                "timestamp": now_iso(),
                "t": elapsed,
                "cpu_total": cpu_total,
                "mem_mb": round(rss / (1024 * 1024), 3)
            })
        except Exception:
            rows.append({"timestamp": now_iso(), "t": elapsed, "cpu_total": None, "mem_mb": None})
        time.sleep(args.interval)

    df = pd.DataFrame(rows)
    csv_path = f"data/results/{exp}/monitor/timeline.csv"
    df.to_csv(csv_path, index=False)

    # Overlay events
    evs = load_events(exp)

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df["t"], df["cpu_total"], label="CPU total %", color="tab:blue")
    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("CPU %", color="tab:blue")
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.plot(df["t"], df["mem_mb"], label="Memoria (MB)", color="tab:red", alpha=0.6)
    ax2.set_ylabel("Memoria (MB)", color="tab:red")
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Event markers
    start_events = {
        "PREPROCESS_START": "Prep",
        "TRAIN_RF_START": "Train RF",
        "EVAL_RF_START": "Eval RF",
        "TRAIN_SVM_START": "Train SVM",
        "EVAL_SVM_START": "Eval SVM",
    }
    for ev in evs:
        label = start_events.get(ev.get("event"))
        if not label:
            continue
        # Align by time since first sample
        try:
            ts = datetime.strptime(ev["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            t = (ts - t0).total_seconds()
            ax1.axvline(x=t, color="gray", linestyle="--", alpha=0.6)
            ax1.text(t, ax1.get_ylim()[1]*0.9, label, rotation=90, va='top', ha='right', fontsize=8)
        except Exception:
            pass

    # Incident markers: RETRY_* (orange), FAILURE_* (red)
    for ev in evs:
        ename = ev.get("event", "")
        if not (ename.startswith("RETRY_") or ename.startswith("FAILURE_")):
            continue
        try:
            ts = datetime.strptime(ev["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            t = (ts - t0).total_seconds()
            color = "orange" if ename.startswith("RETRY_") else "red"
            ax1.scatter([t], [ax1.get_ylim()[1]*0.8], color=color, s=30, zorder=5)
            ax1.text(t, ax1.get_ylim()[1]*0.78, ename.replace("RETRY_","R:").replace("FAILURE_","F:"), rotation=90, va='top', ha='right', fontsize=7, color=color)
        except Exception:
            pass

    fig.tight_layout()
    png_path = f"data/results/{exp}/monitor/timeline.png"
    fig.savefig(png_path, dpi=150)

    print(json.dumps({"timeline_csv": csv_path, "timeline_png": png_path}))


if __name__ == "__main__":
    main()
