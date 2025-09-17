# Protocolo de Mensajes (ACL simplificado)

Objetivo: estandarizar la comunicación entre agentes (y con el Orchestrator) para el flujo experimental.

## Performative
- REQUEST: solicita ejecución de una tarea.
- INFORM: envía resultados exitosos de ejecución.
- FAILURE: notifica fallo con causa.
- CANCEL: (opcional) aborta una tarea.

## Encabezado común
Cada mensaje incluye los siguientes campos:
- experimentId: string (UUID/slug)
- conversationId: string (para encadenar diálogos dentro del mismo experimento)
- from: string (nombre del agente emisor)
- to: string (nombre del agente receptor)
- timestamp: ISO-8601 UTC
- performative: REQUEST | INFORM | FAILURE | CANCEL
- ontology: "sma-ml-v1" (versión simple de ontología)
- payloadType: string (ej.: DataRequest, PrepResult, TrainResult, EvalRequest, MetricsAggregate, ExportResult)

## Payloads (esquemas JSON)

1) DataRequest (REQUEST DataIngestion)
{
  "datasetRef": { "path": "data/raw/synthetic_classification.csv", "sha256": "..." }
}

2) DataReady (INFORM → Orchestrator)
{
  "dataRef": { "path": "...", "rows": 3000, "cols": 21, "sha256": "..." }
}

3) PrepRequest (REQUEST Preprocessing)
{
  "dataRef": { ... },
  "prepConfig": { "scale": true, "encode": false, "test_size": 0.2, "seed": 42 }
}

4) PrepResult (INFORM)
{
  "prepRef": { "method": ["scale"], "params": {"scaler": "StandardScaler"}, "seed": 42 }
}

5) TrainRequest (REQUEST TrainingRF|SVM)
{
  "prepRef": { ... },
  "algo": "RF|SVM",
  "hyperparams": { "RF": {"n_estimators": 100}, "SVM": {"kernel": "rbf", "C": 1.0} },
  "seed": 42
}

6) TrainResult (INFORM → Metrics)
{
  "modelRef": { "algo": "RF", "path": "data/results/<exp>/models/rf.pkl", "sha256": "..." },
  "train_metrics": { "time_ms": 453, "cpu_avg": 35.2, "mem_peak_mb": 512.4, "energy_j_per_mb": 0.87, "seed": 42 }
}

7) EvalRequest (REQUEST Evaluation)
{
  "modelRef": { ... },
  "evalSpec": { "metrics": ["accuracy","f1"], "confusion_matrix": true }
}

8) EvalResult (INFORM → Metrics)
{
  "eval_metrics": { "accuracy": 0.88, "f1": 0.87, "cm_path": "data/results/<exp>/cm.png" }
}

9) MetricsAggregate (INFORM → Export)
{
  "aggregates": { "accuracy": 0.88, "f1": 0.87, "time_ms": 453, "energy_j_per_mb": 0.87 },
  "artifacts": ["data/results/<exp>/models/rf.pkl"]
}

10) ExportResult (INFORM → Orchestrator)
{
  "resultPaths": ["data/results/<exp>/report.json", "data/results/<exp>/metrics.csv" ],
  "hashes": { "report.json": "...", "metrics.csv": "..." }
}

11) Failure (FAILURE genérico)
{
  "stage": "Training|Evaluation|...",
  "reason": "<mensaje/stack>",
  "retryable": true
}

## Ejemplo de mensaje completo (REQUEST → Preprocessing)
{
  "experimentId": "exp20250917_01",
  "conversationId": "exp20250917_01_prep_1",
  "from": "Orchestrator",
  "to": "Preprocessing",
  "timestamp": "2025-09-17T12:00:00Z",
  "performative": "REQUEST",
  "ontology": "sma-ml-v1",
  "payloadType": "PrepRequest",
  "payload": {
    "dataRef": { "path": "data/raw/synthetic_classification.csv", "sha256": "9969bedfaea6d914479d46de9abb98d96d4ba9e1a635e9d9606834ca094ed57a" },
    "prepConfig": { "scale": true, "test_size": 0.2, "seed": 42 }
  }
}

## Consideraciones
- Todos los mensajes deben registrarse como JSON línea con el mismo esquema (para parsers simples).
- Tiempos en UTC y formato ISO-8601.
- Los agentes deben validar `payloadType` antes de procesar.
- `experimentId` único por ejecución; `conversationId` por etapa.
- En caso de fallo, `stage` indica el componente y `retryable` sugiere si Orchestrator reintenta.
