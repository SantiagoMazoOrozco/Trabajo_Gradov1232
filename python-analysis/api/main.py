from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
import os
import time
import json
import hashlib
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import numpy as np
import psutil
from threading import Event, Thread


# --------- Models (aligned with docs/message-protocol.md) ---------

class DataRef(BaseModel):
    path: str
    sha256: Optional[str] = None
    rows: Optional[int] = None
    cols: Optional[int] = None


class PrepConfig(BaseModel):
    scale: bool = True
    encode: bool = False
    test_size: float = 0.2
    seed: int = 42


class PrepRef(BaseModel):
    method: list[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)
    seed: int
    paths: Dict[str, str]  # {"X_train":..., "y_train":..., "X_test":..., "y_test":...}


class TrainHyperparams(BaseModel):
    RF: Optional[Dict[str, Any]] = None
    SVM: Optional[Dict[str, Any]] = None


class ModelRef(BaseModel):
    algo: Literal["RF", "SVM"]
    path: str
    sha256: Optional[str] = None


class TrainMetrics(BaseModel):
    time_ms: float
    cpu_avg: Optional[float] = None
    mem_peak_mb: Optional[float] = None
    energy_j_per_mb: Optional[float] = None
    energy_j_total: Optional[float] = None
    # Throughput and efficiencies
    n_train: Optional[int] = None
    mb_processed: Optional[float] = None
    records_per_s: Optional[float] = None
    data_mb_per_s: Optional[float] = None
    energy_j_per_record: Optional[float] = None
    efficiency_cpu_rps_per_pct: Optional[float] = None  # records/s per 1% CPU
    efficiency_mem_rps_per_mb: Optional[float] = None   # records/s per MB peak
    seed: int


class EvalSpec(BaseModel):
    metrics: list[str] = Field(default_factory=lambda: ["accuracy", "f1"])  # accuracy, f1
    confusion_matrix: bool = True
    test_paths: Optional[Dict[str, str]] = None  # {"X_test":..., "y_test":...}


class EvalMetrics(BaseModel):
    accuracy: Optional[float] = None
    f1: Optional[float] = None
    cm_path: Optional[str] = None


# Request envelopes (minimal header + payload)
class RequestHeader(BaseModel):
    experimentId: str
    conversationId: Optional[str] = None
    performative: Literal["REQUEST", "INFORM", "FAILURE", "CANCEL"]
    payloadType: str


class PrepRequest(BaseModel):
    # header
    experimentId: str
    conversationId: Optional[str] = None
    payload: Dict[str, Any]


class PrepResponse(BaseModel):
    experimentId: str
    conversationId: Optional[str] = None
    payloadType: Literal["PrepResult"] = "PrepResult"
    payload: Dict[str, Any]


class TrainRequest(BaseModel):
    experimentId: str
    conversationId: Optional[str] = None
    payload: Dict[str, Any]


class TrainResponse(BaseModel):
    experimentId: str
    conversationId: Optional[str] = None
    payloadType: Literal["TrainResult"] = "TrainResult"
    payload: Dict[str, Any]


class EvalRequest(BaseModel):
    experimentId: str
    conversationId: Optional[str] = None
    payload: Dict[str, Any]


class EvalResponse(BaseModel):
    experimentId: str
    conversationId: Optional[str] = None
    payloadType: Literal["EvalResult"] = "EvalResult"
    payload: Dict[str, Any]


# --------- Utility: metrics sampler ---------

class ResourceSampler:
    def __init__(self, interval_sec: float = 0.1) -> None:
        self.interval = interval_sec
        self._stop = Event()
        self._cpu_samples: list[float] = []
        self._mem_peak: int = 0

    def _run(self) -> None:
        proc = psutil.Process()
        # Warm up cpu_percent measurement
        psutil.cpu_percent(interval=None)
        while not self._stop.is_set():
            self._cpu_samples.append(psutil.cpu_percent(interval=self.interval))
            try:
                rss = proc.memory_info().rss
                if rss > self._mem_peak:
                    self._mem_peak = rss
            except psutil.Error:
                pass

    def __enter__(self):
        self._stop.clear()
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        self._thread.join(timeout=1.0)

    @property
    def cpu_avg(self) -> Optional[float]:
        return float(np.mean(self._cpu_samples)) if self._cpu_samples else None

    @property
    def mem_peak_mb(self) -> Optional[float]:
        return round(self._mem_peak / (1024 * 1024), 3) if self._mem_peak else None


# --------- FastAPI app ---------

app = FastAPI(title="SMA-ML Experimental API", version="0.1.0")

# ---- Templates & Static (Dashboard) ----
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'templates')
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'static')
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATES_DIR)
if not any([p for p in app.routes if getattr(p, 'path', None) == '/static']):
    app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


def list_experiments(root: str = os.path.join('data', 'results')):
    exps = []
    if not os.path.exists(root):
        return exps
    for name in os.listdir(root):
        if name.startswith('_'):
            continue
        exp_dir = os.path.join(root, name)
        if not os.path.isdir(exp_dir):
            continue
        meta_path = os.path.join(exp_dir, 'meta.json')
        group = None
        created = None
        if os.path.exists(meta_path):
            try:
                import json
                with open(meta_path, 'r', encoding='utf-8-sig') as f:
                    meta = json.load(f) or {}
                group = meta.get('group')
                created = meta.get('created_utc')
            except Exception:
                pass
        exps.append({'id': name, 'group': group, 'created_utc': created})
    exps.sort(key=lambda x: x.get('created_utc') or '', reverse=True)
    return exps


def load_events(exp_id: str):
    ev_path = os.path.join('data', 'results', exp_id, 'logs', 'events.jsonl')
    events = []
    if os.path.exists(ev_path):
        with open(ev_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
    return events


def summarize_experiment(exp_id: str):
    events = load_events(exp_id)
    by_event = {e.get('event'): e for e in events}
    summary = {'id': exp_id, 'train': {}, 'eval': {}, 'raw_events': events}
    for algo in ('RF', 'SVM'):
        t_ev = by_event.get(f'MODEL_TRAINED_{algo}')
        e_ev = by_event.get(f'EVAL_DONE_{algo}')
        if t_ev:
            tm = t_ev.get('train_metrics') or {}
            summary['train'][algo] = {
                'time_ms': tm.get('time_ms'),
                'cpu_avg': tm.get('cpu_avg'),
                'mem_peak_mb': tm.get('mem_peak_mb'),
                'energy_j_total': tm.get('energy_j_total'),
                'energy_j_per_mb': tm.get('energy_j_per_mb')
            }
        if e_ev:
            em = e_ev.get('eval_metrics') or {}
            summary['eval'][algo] = {
                'accuracy': em.get('accuracy'),
                'f1': em.get('f1')
            }
    return summary


@app.get('/', response_class=HTMLResponse)
def dashboard_root(request: Request):
    exps = list_experiments()
    stats_md = None
    stats_path = os.path.join('data', 'results', 'stats_summary.md')
    if os.path.exists(stats_path):
        try:
            with open(stats_path, 'r', encoding='utf-8') as f:
                stats_md = f.read()
        except Exception:
            pass
    return templates.TemplateResponse('experiments.html', {
        'request': request,
        'experiments': exps,
        'stats_md': stats_md,
        'title': 'Experimentos'
    })


@app.get('/experiments/{exp_id}', response_class=HTMLResponse)
def experiment_detail(exp_id: str, request: Request):
    summary = summarize_experiment(exp_id)
    return templates.TemplateResponse('experiment_detail.html', {
        'request': request,
        'exp': summary,
        'title': f'Experimento {exp_id}'
    })


def ensure_results_dir(exp_id: str, *subdirs: str) -> str:
    base = os.path.join("data", "results", exp_id, *subdirs)
    os.makedirs(base, exist_ok=True)
    return base


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


@app.post("/preprocess", response_model=PrepResponse)
def preprocess(req: PrepRequest):
    exp = req.experimentId
    payload = req.payload
    data_ref = DataRef(**payload.get("dataRef"))
    prep_cfg = PrepConfig(**payload.get("prepConfig", {}))

    if not os.path.exists(data_ref.path):
        raise HTTPException(status_code=404, detail=f"Dataset not found: {data_ref.path}")

    df = pd.read_csv(data_ref.path)
    if "target" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'target' column")

    X = df.drop(columns=["target"]).values
    y = df["target"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=prep_cfg.test_size, random_state=prep_cfg.seed, stratify=y
    )

    methods = []
    params: Dict[str, Any] = {"test_size": prep_cfg.test_size}
    if prep_cfg.scale:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        methods.append("scale")
        params["scaler"] = "StandardScaler"
        params["scaler_mean"] = scaler.mean_.tolist()
        params["scaler_scale"] = scaler.scale_.tolist()

    out_dir = ensure_results_dir(exp, "prep")
    xtr = os.path.join(out_dir, "X_train.csv")
    ytr = os.path.join(out_dir, "y_train.csv")
    xte = os.path.join(out_dir, "X_test.csv")
    yte = os.path.join(out_dir, "y_test.csv")

    pd.DataFrame(X_train).to_csv(xtr, index=False)
    pd.DataFrame(y_train, columns=["target"]).to_csv(ytr, index=False)
    pd.DataFrame(X_test).to_csv(xte, index=False)
    pd.DataFrame(y_test, columns=["target"]).to_csv(yte, index=False)

    prep_ref = PrepRef(method=methods, params=params, seed=prep_cfg.seed,
                       paths={"X_train": xtr, "y_train": ytr, "X_test": xte, "y_test": yte})

    return PrepResponse(
        experimentId=exp,
        conversationId=req.conversationId,
        payload={"prepRef": prep_ref.dict()}
    )


@app.post("/train", response_model=TrainResponse)
def train(req: TrainRequest):
    exp = req.experimentId
    payload = req.payload
    algo = payload.get("algo")
    seed = int(payload.get("seed", 42))
    hyper = TrainHyperparams(**payload.get("hyperparams", {}))
    prep_ref = PrepRef(**payload.get("prepRef"))

    try:
        X_train_df = pd.read_csv(prep_ref.paths["X_train"])  # keep df to compute memory footprint
        y_train_df = pd.read_csv(prep_ref.paths["y_train"])  # keep df to compute memory footprint
        X_train = X_train_df.values
        y_train = y_train_df.values.ravel()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot load training data: {e}")

    model = None
    model_name = None
    if algo == "RF":
        params = hyper.RF or {"n_estimators": 100, "random_state": seed}
        params.setdefault("random_state", seed)
        model = RandomForestClassifier(**params)
        model_name = "rf"
    elif algo == "SVM":
        params = hyper.SVM or {"kernel": "rbf", "C": 1.0}
        model = SVC(**params, probability=False, random_state=seed if "random_state" in SVC().get_params() else None)
        model_name = "svm"
    else:
        raise HTTPException(status_code=400, detail="algo must be 'RF' or 'SVM'")

    start = time.perf_counter()
    with ResourceSampler() as sampler:
        model.fit(X_train, y_train)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    models_dir = ensure_results_dir(exp, "models")
    model_path = os.path.join(models_dir, f"{model_name}.pkl")
    joblib.dump(model, model_path)
    model_hash = sha256_file(model_path)

    # Estimate energy consumption proxy
    try:
        cpu_power_w = float(os.environ.get("CPU_POWER_W", "35.0"))  # configurable TDP/power in watts
    except ValueError:
        cpu_power_w = 35.0
    cpu_avg = float(np.mean(sampler._cpu_samples)) if sampler._cpu_samples else None
    time_s = elapsed_ms / 1000.0
    # Approx processed data size in MB (features + labels) using pandas memory_usage
    bytes_processed = int(X_train_df.memory_usage(deep=True).sum() + y_train_df.memory_usage(deep=True).sum())
    mb_processed = (bytes_processed / (1024.0 * 1024.0)) if bytes_processed > 0 else None
    energy_total_j = None
    energy_per_mb = None
    if cpu_avg is not None:
        energy_total_j = cpu_power_w * (cpu_avg / 100.0) * time_s
        if mb_processed and mb_processed > 0:
            energy_per_mb = energy_total_j / mb_processed

    # Throughput and derived efficiencies
    n_train = int(len(y_train)) if isinstance(y_train, (list, np.ndarray)) else int(y_train_df.shape[0])
    records_per_s = (n_train / time_s) if time_s > 0 else None
    data_mb_per_s = (mb_processed / time_s) if (mb_processed and time_s > 0) else None
    energy_j_per_record = (energy_total_j / n_train) if (energy_total_j is not None and n_train > 0) else None
    efficiency_cpu = (records_per_s / cpu_avg) if (records_per_s is not None and cpu_avg and cpu_avg > 0) else None
    efficiency_mem = (records_per_s / sampler.mem_peak_mb) if (records_per_s is not None and sampler.mem_peak_mb and sampler.mem_peak_mb > 0) else None

    metrics = TrainMetrics(
        time_ms=round(elapsed_ms, 3),
        cpu_avg=(round(sampler.cpu_avg, 2) if sampler.cpu_avg is not None else None),
        mem_peak_mb=sampler.mem_peak_mb,
        energy_j_per_mb=(round(energy_per_mb, 6) if energy_per_mb is not None else None),
        energy_j_total=(round(energy_total_j, 3) if energy_total_j is not None else None),
        n_train=n_train,
        mb_processed=(round(mb_processed, 6) if mb_processed is not None else None),
        records_per_s=(round(records_per_s, 6) if records_per_s is not None else None),
        data_mb_per_s=(round(data_mb_per_s, 6) if data_mb_per_s is not None else None),
        energy_j_per_record=(round(energy_j_per_record, 9) if energy_j_per_record is not None else None),
        efficiency_cpu_rps_per_pct=(round(efficiency_cpu, 6) if efficiency_cpu is not None else None),
        efficiency_mem_rps_per_mb=(round(efficiency_mem, 6) if efficiency_mem is not None else None),
        seed=seed,
    )

    model_ref = ModelRef(algo=algo, path=model_path, sha256=model_hash)

    return TrainResponse(
        experimentId=exp,
        conversationId=req.conversationId,
        payload={"modelRef": model_ref.dict(), "train_metrics": metrics.dict()}
    )


@app.post("/evaluate", response_model=EvalResponse)
def evaluate(req: EvalRequest):
    exp = req.experimentId
    payload = req.payload
    model_ref = ModelRef(**payload.get("modelRef"))
    spec = EvalSpec(**payload.get("evalSpec", {}))

    try:
        model = joblib.load(model_ref.path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot load model: {e}")

    # Test data paths
    if not spec.test_paths:
        # default to experiment results
        prep_dir = ensure_results_dir(exp, "prep")
        xte = os.path.join(prep_dir, "X_test.csv")
        yte = os.path.join(prep_dir, "y_test.csv")
    else:
        xte = spec.test_paths.get("X_test")
        yte = spec.test_paths.get("y_test")

    try:
        X_test = pd.read_csv(xte).values
        y_test = pd.read_csv(yte).values.ravel()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot load test data: {e}")

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred) if "accuracy" in spec.metrics else None
    f1 = f1_score(y_test, y_pred, average="macro") if "f1" in spec.metrics else None

    cm_path = None
    if spec.confusion_matrix:
        cm = confusion_matrix(y_test, y_pred)
        eval_dir = ensure_results_dir(exp, "eval")
        cm_path = os.path.join(eval_dir, "confusion_matrix.csv")
        pd.DataFrame(cm).to_csv(cm_path, index=False)

    metrics = EvalMetrics(accuracy=acc, f1=f1, cm_path=cm_path)

    return EvalResponse(
        experimentId=exp,
        conversationId=req.conversationId,
        payload={"eval_metrics": metrics.dict()}
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/pid")
def pid():
    return {"pid": os.getpid()}
