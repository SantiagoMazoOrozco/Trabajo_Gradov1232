from fastapi import FastAPI, HTTPException
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
        X_train = pd.read_csv(prep_ref.paths["X_train"]).values
        y_train = pd.read_csv(prep_ref.paths["y_train"]).values.ravel()
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

    metrics = TrainMetrics(
        time_ms=round(elapsed_ms, 3),
        cpu_avg=(round(sampler.cpu_avg, 2) if sampler.cpu_avg is not None else None),
        mem_peak_mb=sampler.mem_peak_mb,
        energy_j_per_mb=None,  # TODO: estimar si se dispone de potencia promedio CPU/SoC
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
