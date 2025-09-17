import requests
import json
import os
from datetime import datetime

API = "http://127.0.0.1:8000"


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


def run(exp_id: str = "exp_local_demo"):
    # 1) Preprocess
    log_line(exp_id, "PREPROCESS_START", {
        "agent": "PreprocessingAgent",
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
    r = requests.post(f"{API}/preprocess", json=req, timeout=60)
    r.raise_for_status()
    prep = r.json()["payload"]["prepRef"]
    log_line(exp_id, "PREPROCESS_DONE", {
        "prepRef": prep,
        "why": "Se aplicó escalado estándar para estabilizar el entrenamiento y se separó 20% para test con semilla fija."
    })

    # 2) Train RF
    log_line(exp_id, "TRAIN_RF_START", {
        "agent": "TrainingAgentRF",
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
    r = requests.post(f"{API}/train", json=train_req, timeout=120)
    r.raise_for_status()
    train_rf = r.json()["payload"]
    log_line(exp_id, "MODEL_TRAINED_RF", {
        **train_rf,
        "why": "Se entrenó RandomForest por robustez a outliers y buen baseline; n_estimators=100 por compromiso sesgo-varianza."
    })

    # 3) Evaluate RF
    log_line(exp_id, "EVAL_RF_START", {
        "agent": "EvaluationAgent",
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
    r = requests.post(f"{API}/evaluate", json=eval_req, timeout=60)
    r.raise_for_status()
    eval_rf = r.json()["payload"]
    log_line(exp_id, "EVAL_DONE_RF", {
        **eval_rf,
        "why": "Se midió accuracy y F1-macro para balancear exactitud y equilibrio entre clases; se guarda la matriz de confusión."
    })

    # 4) Train SVM
    log_line(exp_id, "TRAIN_SVM_START", {
        "agent": "TrainingAgentSVM",
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
    r = requests.post(f"{API}/train", json=train_req, timeout=120)
    r.raise_for_status()
    train_svm = r.json()["payload"]
    log_line(exp_id, "MODEL_TRAINED_SVM", {
        **train_svm,
        "why": "Se entrenó SVM kernel RBF como comparativa clásica; C=1.0 para regularización estándar."
    })

    # 5) Evaluate SVM
    log_line(exp_id, "EVAL_SVM_START", {
        "agent": "EvaluationAgent",
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
    r = requests.post(f"{API}/evaluate", json=eval_req, timeout=60)
    r.raise_for_status()
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
