# Arquitectura SMA (Fase 1)

Este documento define la primera versión de la arquitectura basada en Sistemas Multiagente (SMA) para orquestar experimentos de ML (entrenamiento y evaluación) conforme al Macroproceso.

## Objetivo
Diseñar agentes especializados y su interacción para ejecutar, medir y exportar experimentos sobre algoritmos supervisados (Random Forest, SVM) de forma reproducible y trazable.

## Agentes mínimos y responsabilidades

1) Orchestrator
- Propósito: Coordinar el flujo end-to-end de un experimento (planificación, seguimiento, reintentos, cierre).
- Inputs: REQUEST de usuario o job scheduler con experimentId + configuración.
- Outputs: REQUEST a agentes subsiguientes; INFORM final (resumen) hacia Export/Metrics.
- Eventos: EXPERIMENT_STARTED, STAGE_COMPLETED, STAGE_FAILED, EXPERIMENT_FINISHED.

2) DataIngestion
- Propósito: Resolver dataset (ruta en `data/raw` + meta), particionar si aplica.
- Inputs: REQUEST(experimentId, datasetRef).
- Outputs: INFORM con dataRef/partitions.
- Eventos: DATA_READY, INGESTION_FAILED.

3) Preprocessing
- Propósito: Limpieza, escalado, split train/test (si no viene), encoding.
- Inputs: REQUEST(dataRef, config).
- Outputs: INFORM con prepRef (referencia a artefactos preprocesados o parámetros aplicados).
- Eventos: PREPROCESS_DONE, PREPROCESS_FAILED.

4) Training(RF)
- Propósito: Entrenar RandomForest con hyperparams recibidos.
- Inputs: REQUEST(prepRef, hyperparams, seed).
- Outputs: INFORM con modelRef + train_metrics (tiempo, CPU, memoria, energía estimada).
- Eventos: MODEL_TRAINED, TRAIN_FAILED.

5) Training(SVM)
- Propósito: Entrenar SVM con hyperparams recibidos.
- Inputs: REQUEST(prepRef, hyperparams, seed).
- Outputs: INFORM con modelRef + train_metrics.
- Eventos: MODEL_TRAINED, TRAIN_FAILED.

6) Evaluation
- Propósito: Evaluar modelos en conjunto de prueba/validación.
- Inputs: REQUEST(modelRef, evalSpec).
- Outputs: INFORM con eval_metrics (accuracy, f1, matriz conf., etc.).
- Eventos: EVAL_DONE, EVAL_FAILED.

7) Metrics
- Propósito: Agregar, normalizar y enriquecer métricas (e.g., Joules/MB, throughput, picos).
- Inputs: INFORM parciales de Training/Evaluation.
- Outputs: INFORM agregada al Orchestrator/Export.
- Eventos: METRICS_AGGREGATED.

8) Export
- Propósito: Persistir resultados en `data/results`, generar reportes/CSV/JSON.
- Inputs: REQUEST/INFORM con agregados y artefactos.
- Outputs: INFORM con paths finales y hashes.
- Eventos: EXPORT_DONE, EXPORT_FAILED.

## Flujo básico (secuencia)
1. Orchestrator → DataIngestion: REQUEST {experimentId, datasetRef}
2. DataIngestion → Orchestrator: INFORM {dataRef}
3. Orchestrator → Preprocessing: REQUEST {dataRef, prepConfig}
4. Preprocessing → Orchestrator: INFORM {prepRef}
5. Orchestrator → Training(RF|SVM): REQUEST {prepRef, hyperparams, seed}
6. Training → Metrics: INFORM {train_metrics}
7. Orchestrator → Evaluation: REQUEST {modelRef, evalSpec}
8. Evaluation → Metrics: INFORM {eval_metrics}
9. Metrics → Export: INFORM {agregados}
10. Export → Orchestrator: INFORM {resultPaths}
11. Orchestrator: EXPERIMENT_FINISHED

Nota: En caso de fallo en cualquier etapa, el agente emite FAILURE con causa + retry-able, y el Orchestrator decide reintentos o aborta.

## Contratos de datos (resumen)
- dataRef: { path: "data/raw/...csv", sha256: "...", rows, cols }
- prepRef: { method: ["scale","encode"], params: {...}, seed }
- modelRef: { algo: "RF|SVM", path: "data/results/models/...", sha256 }
- train_metrics: { time_ms, cpu_avg, mem_peak_mb, energy_j_per_mb?, seed }
- eval_metrics: { accuracy, f1, precision, recall, cm_path? }
- agregados: { experimentId, stages: [...], metrics: {...}, artifacts: [...] }

## Requisitos no funcionales
- Reproducibilidad: semillas fijas, hashes de artefactos, versionado de código y datasets.
- Observabilidad: logs estructurados JSON línea; correlación por experimentId y conversationId.
- Aislamiento: cada experimento genera carpeta dedicada en `data/results/<experimentId>/`.
- Idempotencia: procesos export y metrics deben tolerar reintentos.

## Integración con Python
- Opción CLI: agentes Java (JADE) invocan scripts Python (`python-analysis`) con parámetros y leen JSON/archivos.
- Opción REST local: microservicio Flask/FastAPI para Training/Evaluation; agentes envían payloads.
- Opción Py4J/JEP: incrustar Python en JVM (más complejo, evitar en primera iteración).

## Diagrama (texto)
[User] → Orchestrator → DataIngestion → Preprocessing → Training(RF|SVM) → Evaluation → Metrics → Export → Orchestrator → [User]

## Aceptación Fase 1
- Documentación de agentes con propósito, inputs, outputs, eventos.
- Protocolo de mensajes definido (ver `docs/message-protocol.md`).
- Plantilla de configuración de experimento (variables y factores) enlazada con Orchestrator.
- Un flujo de extremo a extremo simulado (mock o scripts) que produce archivos en `data/results/` con logs.

## Nombres de agentes parametrizables

Para facilitar la futura integración con JADE, los nombres de agentes que aparecen en los eventos/logs son configurables mediante el archivo `python-analysis/agent_config.json`. Ejemplo por defecto:

```
{
	"PreprocessingAgent": "PreprocessingAgent",
	"TrainingAgentRF": "TrainingAgentRF",
	"TrainingAgentSVM": "TrainingAgentSVM",
	"EvaluationAgent": "EvaluationAgent"
}
```

El simulador (`python-analysis/simulate_experiment.py`) carga este archivo al inicio y utiliza los nombres resultantes en los eventos START/RETRY/FAILURE/DONE. Esto permite alinear la nomenclatura con agentes reales de la plataforma (p. ej., JADE) sin modificar código.
