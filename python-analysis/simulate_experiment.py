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
    log_line(exp_id, "PREPROCESS_DONE", {"prepRef": prep})

    # 2) Train RF
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
    log_line(exp_id, "MODEL_TRAINED_RF", train_rf)

    # 3) Evaluate RF
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
    log_line(exp_id, "EVAL_DONE_RF", eval_rf)

    # 4) Train SVM
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
    log_line(exp_id, "MODEL_TRAINED_SVM", train_svm)

    # 5) Evaluate SVM
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
    log_line(exp_id, "EVAL_DONE_SVM", eval_svm)

    # 6) Finish
    log_line(exp_id, "EXPERIMENT_FINISHED", {"resultPaths": [f"data/results/{exp_id}"]})


if __name__ == "__main__":
    run()
