# Protocolo de Mensajes y Eventos

Este documento captura el esquema de mensajes (ACL) y la estructura de eventos utilizada para la orquestación y la trazabilidad.

## Mensajes (ACL)

- Emisor, Receptor, Performativa (REQUEST, INFORM, FAILURE, etc.)
- Ontología: tareas de PREPROCESS, TRAIN, EVAL
- Contenido: carga estructurada (JSON/XML) con parámetros de etapa

## Eventos (JSONL)

- Campos principales:
  - `ts_utc` — timestamp UTC ISO8601
  - `stage` — PREPROCESS|TRAIN_RF|EVAL_RF|TRAIN_SVM|EVAL_SVM
  - `algo` — RF|SVM
  - `duration_s`, `cpu_avg`, `mem_peak_mb`
  - `records`, `data_mb`
  - `why` — justificación/criterio

## Mapeo a métricas

- Duración, CPU, memoria → métricas `train_*` y derivados
- Throughput (reg/s) y MB/s → `train_records_per_s_last`, `train_data_mb_per_s_last`
- Energía (watts-first): potencia instantánea y promedio → `cpu_package_power_w`, `cpu_power_w_proxy`, `train_avg_watts_last`

## Consideraciones de compatibilidad

- El agregador acepta variantes con `energy_j_*` y normaliza a watts y joules derivados.
- Versionar cambios de esquema y documentar en commit messages/CHANGELOG.
