import requests
import json
import os
import time
from datetime import datetime

API = os.environ.get("API_BASE", "http://127.0.0.1:8000")


def log_line(exp_id: str, event: str, payload: dict):
    os.makedirs(f"data/results/{exp_id}/logs", exist_ok=True)
    line = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "experimentId": exp_id,
        "event": event,
        **payload,
    }
    with open(f"data/results/{exp_id}/logs/events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def load_agent_names():
    cfg_path = os.path.join("python-analysis", "agent_config.json")
    default = {
        "PreprocessingAgent": "PreprocessingAgent",
        "TrainingAgentRF": "TrainingAgentRF",
        "TrainingAgentSVM": "TrainingAgentSVM",
        "EvaluationAgent": "EvaluationAgent",
    }
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**default, **data}
    except Exception:
        return default


def run(exp_id: str = "exp_local_demo"):
    agents = load_agent_names()
    # 1) Preprocess
    log_line(exp_id, "PREPROCESS_START", {
        "agent": agents["PreprocessingAgent"],
        "action": "preprocess",
        "details": {"scale": True, "test_size": 0.2, "seed": 42, "data": "data/raw/synthetic_classification.csv"}
    })
    conv = f"{exp_id}_prep_1"
    data_ref = {
        "path": "data/raw/synthetic_classification.csv",
        "sha256": None,
    }
    prep_cfg = {"scale": True, "test_size": 0.2, "seed": 42}
    req = {"experimentId": exp_id, "conversationId": conv, "payload": {"dataRef": data_ref, "prepConfig": prep_cfg}}
    try:
        r = requests.post(f"{API}/preprocess", json=req, timeout=60)
        r.raise_for_status()
    except Exception as e:
        log_line(exp_id, "RETRY_PREPROCESS", {"agent": agents["PreprocessingAgent"], "action": "preprocess", "error": str(e), "suggestion": "Verificar que el API esté levantado y el dataset exista."})
        time.sleep(2)
        try:
            r = requests.post(f"{API}/preprocess", json=req, timeout=60)
            r.raise_for_status()
        except Exception as e2:
            log_line(exp_id, "FAILURE_PREPROCESS", {"agent": agents["PreprocessingAgent"], "action": "preprocess", "error": str(e2), "fatal": True})
            raise
    prep = r.json()["payload"]["prepRef"]
    log_line(exp_id, "PREPROCESS_DONE", {
        "prepRef": prep,
        "why": "Se aplicó escalado estándar para estabilizar el entrenamiento y se separó 20% para test con semilla fija."
    })

    # 2) Train RF
    log_line(exp_id, "TRAIN_RF_START", {
        "agent": agents["TrainingAgentRF"],
        "action": "train",
        "details": {"algo": "RF", "hyperparams": {"n_estimators": 100}, "seed": 42}
    })
    conv = f"{exp_id}_train_rf_1"
    train_req = {
        "experimentId": exp_id,
        "conversationId": conv,
        "payload": {
            "prepRef": prep,
            "algo": "RF",
            "hyperparams": {"RF": {"n_estimators": 100}},
            "seed": 42,
        },
    }
    try:
        r = requests.post(f"{API}/train", json=train_req, timeout=120)
        r.raise_for_status()
    except Exception as e:
        log_line(exp_id, "RETRY_TRAIN_RF", {"agent": agents["TrainingAgentRF"], "action": "train", "error": str(e), "suggestion": "Validar hyperparams y que el prep haya generado datos."})
        time.sleep(2)
        try:
            r = requests.post(f"{API}/train", json=train_req, timeout=120)
            r.raise_for_status()
        except Exception as e2:
            log_line(exp_id, "FAILURE_TRAIN_RF", {"agent": agents["TrainingAgentRF"], "action": "train", "error": str(e2), "fatal": True})
            raise
    train_rf = r.json()["payload"]
    log_line(exp_id, "MODEL_TRAINED_RF", {
        **train_rf,
        "why": "Se entrenó RandomForest por robustez a outliers y buen baseline; n_estimators=100 por compromiso sesgo-varianza."
    })

    # 3) Evaluate RF
    log_line(exp_id, "EVAL_RF_START", {
        "agent": agents["EvaluationAgent"],
        "action": "evaluate",
        "details": {"algo": "RF", "metrics": ["accuracy", "f1"], "confusion_matrix": True}
    })
    conv = f"{exp_id}_eval_rf_1"
    eval_req = {
        "experimentId": exp_id,
        "conversationId": conv,
        "payload": {
            "modelRef": train_rf["modelRef"],
            "evalSpec": {"metrics": ["accuracy", "f1"], "confusion_matrix": True},
        },
    }
    try:
        r = requests.post(f"{API}/evaluate", json=eval_req, timeout=60)
        r.raise_for_status()
    except Exception as e:
        log_line(exp_id, "RETRY_EVAL_RF", {"agent": agents["EvaluationAgent"], "action": "evaluate", "error": str(e), "suggestion": "Revisar que el modelo RF y los paths de test existan."})
        time.sleep(2)
        try:
            r = requests.post(f"{API}/evaluate", json=eval_req, timeout=60)
            r.raise_for_status()
        except Exception as e2:
            log_line(exp_id, "FAILURE_EVAL_RF", {"agent": agents["EvaluationAgent"], "action": "evaluate", "error": str(e2), "fatal": True})
            raise
    eval_rf = r.json()["payload"]
    log_line(exp_id, "EVAL_DONE_RF", {
        **eval_rf,
        "why": "Se midió accuracy y F1-macro para balancear exactitud y equilibrio entre clases; se guarda la matriz de confusión."
    })

    # 4) Train SVM
    log_line(exp_id, "TRAIN_SVM_START", {
        "agent": agents["TrainingAgentSVM"],
        "action": "train",
        "details": {"algo": "SVM", "hyperparams": {"kernel": "rbf", "C": 1.0}, "seed": 42}
    })
    conv = f"{exp_id}_train_svm_1"
    train_req = {
        "experimentId": exp_id,
        "conversationId": conv,
        "payload": {
            "prepRef": prep,
            "algo": "SVM",
            "hyperparams": {"SVM": {"kernel": "rbf", "C": 1.0}},
            "seed": 42,
        },
    }
    try:
        r = requests.post(f"{API}/train", json=train_req, timeout=120)
        r.raise_for_status()
    except Exception as e:
        log_line(exp_id, "RETRY_TRAIN_SVM", {"agent": agents["TrainingAgentSVM"], "action": "train", "error": str(e), "suggestion": "Validar hyperparams SVM y datos de entrenamiento."})
        time.sleep(2)
        try:
            r = requests.post(f"{API}/train", json=train_req, timeout=120)
            r.raise_for_status()
        except Exception as e2:
            log_line(exp_id, "FAILURE_TRAIN_SVM", {"agent": agents["TrainingAgentSVM"], "action": "train", "error": str(e2), "fatal": True})
            raise
    train_svm = r.json()["payload"]
    log_line(exp_id, "MODEL_TRAINED_SVM", {
        **train_svm,
        "why": "Se entrenó SVM kernel RBF como comparativa clásica; C=1.0 para regularización estándar."
    })

    # 5) Evaluate SVM
    log_line(exp_id, "EVAL_SVM_START", {
        "agent": agents["EvaluationAgent"],
        "action": "evaluate",
        "details": {"algo": "SVM", "metrics": ["accuracy", "f1"], "confusion_matrix": True}
    })
    conv = f"{exp_id}_eval_svm_1"
    eval_req = {
        "experimentId": exp_id,
        "conversationId": conv,
        "payload": {
            "modelRef": train_svm["modelRef"],
            "evalSpec": {"metrics": ["accuracy", "f1"], "confusion_matrix": True},
        },
    }
    try:
        r = requests.post(f"{API}/evaluate", json=eval_req, timeout=60)
        r.raise_for_status()
    except Exception as e:
        log_line(exp_id, "RETRY_EVAL_SVM", {"agent": agents["EvaluationAgent"], "action": "evaluate", "error": str(e), "suggestion": "Revisar que el modelo SVM y los paths de test existan."})
        time.sleep(2)
        try:
            r = requests.post(f"{API}/evaluate", json=eval_req, timeout=60)
            r.raise_for_status()
        except Exception as e2:
            log_line(exp_id, "FAILURE_EVAL_SVM", {"agent": agents["EvaluationAgent"], "action": "evaluate", "error": str(e2), "fatal": True})
            raise
    eval_svm = r.json()["payload"]
    log_line(exp_id, "EVAL_DONE_SVM", {
        **eval_svm,
        "why": "Se evaluó con las mismas métricas para comparabilidad; se guarda matriz de confusión."
    })

    # 6) Finish
    log_line(exp_id, "EXPERIMENT_FINISHED", {"resultPaths": [f"data/results/{exp_id}"]})


if __name__ == "__main__":
    import sys
    exp = sys.argv[1] if len(sys.argv) > 1 else "exp_local_demo"
    run(exp)
