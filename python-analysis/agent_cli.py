#!/usr/bin/env python3
"""
agent_cli.py — Puente de línea de comandos para integrar JADE (o cualquier SMA)
con el API FastAPI del proyecto. Permite invocar preprocess/train/evaluate y
lee/escribe JSON para facilitar la orquestación con mensajes ACL o ProcessBuilder.

Uso básico (PowerShell):
  # Preprocess (a partir de CSV con columna 'target')
  python python-analysis/agent_cli.py preprocess `
    --experiment-id exp_demo `
    --data data/raw/synthetic_classification.csv `
    --scale true --test-size 0.2 --seed 42 `
    --out prepRef.json

  # Train RF usando el prepRef devuelto por preprocess
  python python-analysis/agent_cli.py train `
    --experiment-id exp_demo --algo RF --seed 42 `
    --prep-ref-file prepRef.json `
    --out train_rf.json

  # Evaluate usando el modelRef devuelto por train
  python python-analysis/agent_cli.py evaluate `
    --experiment-id exp_demo `
    --model-ref-file train_rf.json `
    --metrics accuracy f1 `
    --confusion-matrix true `
    --out eval_rf.json

Variables de entorno:
  API_BASE: URL base del servicio FastAPI (por defecto http://127.0.0.1:8000)

Salidas:
  - Imprime a stdout un JSON con la respuesta completa del API.
  - Si se usa --out <file>, guarda la sección útil (prepRef, modelRef/train_metrics o eval_metrics)
    en el archivo indicado (formato JSON, UTF-8).
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from typing import Any, Dict, Optional, Tuple

import requests

API = os.environ.get("API_BASE", "http://127.0.0.1:8000")

def _bool(s: str) -> bool:
    if isinstance(s, bool):
        return s
    return str(s).strip().lower() in {"1", "true", "t", "yes", "y"}


def _write_out(obj: Any, out_path: Optional[str]) -> None:
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)


def _post(path: str, body: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{API}{path}"
    r = requests.post(url, json=body, timeout=180)
    r.raise_for_status()
    return r.json()


def cmd_preprocess(args: argparse.Namespace) -> Dict[str, Any]:
    exp = args.experiment_id
    if args.payload_file:
        with open(args.payload_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
            if not isinstance(payload, dict):
                raise SystemExit("--payload-file debe ser un JSON dict con dataRef/prepConfig")
            req = {"experimentId": exp, "conversationId": args.conversation_id, "payload": payload}
    else:
        data_ref = {"path": args.data}
        prep_cfg = {
            "scale": _bool(args.scale),
            "encode": False,
            "test_size": float(args.test_size),
            "seed": int(args.seed),
        }
        req = {"experimentId": exp, "conversationId": args.conversation_id, "payload": {"dataRef": data_ref, "prepConfig": prep_cfg}}

    res = _post("/preprocess", req)
    # Salida útil: prepRef
    payload = res.get("payload") or {}
    prep_ref = payload.get("prepRef")
    if args.out:
        _write_out(prep_ref, args.out)
    return res


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_train(args: argparse.Namespace) -> Dict[str, Any]:
    exp = args.experiment_id
    if args.payload_file:
        req = _load_json(args.payload_file)
        if not isinstance(req, dict):
            raise SystemExit("--payload-file debe ser un JSON dict con experimentId/payload")
        # asegurar experimentId si no viene
        req.setdefault("experimentId", exp)
        req.setdefault("conversationId", args.conversation_id)
    else:
        if not args.prep_ref_file:
            raise SystemExit("Se requiere --prep-ref-file cuando no se usa --payload-file")
        prep_ref = _load_json(args.prep_ref_file)
        payload = {
            "prepRef": prep_ref,
            "algo": args.algo,
            "hyperparams": {args.algo: {}},
            "seed": int(args.seed),
        }
        req = {"experimentId": exp, "conversationId": args.conversation_id, "payload": payload}

    res = _post("/train", req)
    # Salida útil: modelRef + train_metrics
    payload = res.get("payload") or {}
    useful = {k: payload.get(k) for k in ("modelRef", "train_metrics")}
    if args.out:
        _write_out(useful, args.out)
    return res


essential_eval_keys = ("accuracy", "f1", "cm_path")

def cmd_evaluate(args: argparse.Namespace) -> Dict[str, Any]:
    exp = args.experiment_id
    if args.payload_file:
        req = _load_json(args.payload_file)
        if not isinstance(req, dict):
            raise SystemExit("--payload-file debe ser un JSON dict con experimentId/payload")
        req.setdefault("experimentId", exp)
        req.setdefault("conversationId", args.conversation_id)
    else:
        if not args.model_ref_file:
            raise SystemExit("Se requiere --model-ref-file cuando no se usa --payload-file")
        model_ref_container = _load_json(args.model_ref_file)
        # Acepta archivo con {modelRef, train_metrics} (salida de train) o directamente {algo,path}
        if "modelRef" in model_ref_container and isinstance(model_ref_container["modelRef"], dict):
            model_ref = model_ref_container["modelRef"]
        else:
            model_ref = model_ref_container
        eval_spec = {
            "metrics": args.metrics or ["accuracy", "f1"],
            "confusion_matrix": _bool(args.confusion_matrix),
        }
        payload = {"modelRef": model_ref, "evalSpec": eval_spec}
        req = {"experimentId": exp, "conversationId": args.conversation_id, "payload": payload}

    res = _post("/evaluate", req)
    payload = res.get("payload") or {}
    eval_metrics = payload.get("eval_metrics")
    if args.out:
        _write_out(eval_metrics, args.out)
    return res


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CLI puente para el API experimental (JADE bridge)")
    p.add_argument("--conversation-id", default=None, help="Id de conversación (opcional)")
    sp = p.add_subparsers(dest="cmd", required=True)

    # preprocess
    p1 = sp.add_parser("preprocess", help="Preprocesar dataset CSV con 'target'")
    p1.add_argument("--experiment-id", required=True)
    p1.add_argument("--data", help="Ruta al CSV con columna 'target'")
    p1.add_argument("--scale", default="true")
    p1.add_argument("--test-size", default="0.2")
    p1.add_argument("--seed", default="42")
    p1.add_argument("--payload-file", help="Archivo JSON con {dataRef, prepConfig}")
    p1.add_argument("--out", help="Archivo destino para guardar prepRef (JSON)")

    # train
    p2 = sp.add_parser("train", help="Entrenar modelo RF/SVM")
    p2.add_argument("--experiment-id", required=True)
    p2.add_argument("--algo", choices=["RF", "SVM"], required=False, default="RF")
    p2.add_argument("--seed", default="42")
    p2.add_argument("--prep-ref-file", help="Archivo JSON con prepRef devuelto por preprocess")
    p2.add_argument("--payload-file", help="Archivo JSON con la petición completa")
    p2.add_argument("--out", help="Archivo destino para guardar {modelRef, train_metrics}")

    # evaluate
    p3 = sp.add_parser("evaluate", help="Evaluar modelo previamente entrenado")
    p3.add_argument("--experiment-id", required=True)
    p3.add_argument("--model-ref-file", help="Archivo JSON con modelRef o {modelRef,train_metrics}")
    p3.add_argument("--metrics", nargs="*", default=["accuracy", "f1"])
    p3.add_argument("--confusion-matrix", default="true")
    p3.add_argument("--payload-file", help="Archivo JSON con la petición completa")
    p3.add_argument("--out", help="Archivo destino para guardar eval_metrics")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "preprocess":
            res = cmd_preprocess(args)
        elif args.cmd == "train":
            res = cmd_train(args)
        elif args.cmd == "evaluate":
            res = cmd_evaluate(args)
        else:
            raise SystemExit(f"Comando no soportado: {args.cmd}")
    except requests.HTTPError as he:
        print(json.dumps({"error": str(he), "response": getattr(he, 'response', None) and getattr(he.response, 'text', None)}), file=sys.stderr)
        return 2
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1

    # Imprimir la respuesta completa del API a stdout
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
