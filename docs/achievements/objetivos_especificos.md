# Cumplimiento de Objetivos Específicos

Fecha: 2025-11-12

Este documento detalla, con formato de tesis, cómo se cumplieron los objetivos específicos del proyecto. Para cada objetivo se presenta: enunciado, enfoque, implementación, evidencia, métricas, incidencias/errores y estado.

## Lista de objetivos específicos

1) Modelar la arquitectura de un prototipo de SMA capaz de orquestar y gestionar fases clave del pipeline de ML supervisado de clasificación (ingesta, preprocesamiento, preparación de datos) en entornos simulados.
2) Implementar el prototipo de arquitectura SMA modelado, integrando al menos dos algoritmos representativos (Random Forest y SVM) para su ejecución durante la fase de entrenamiento, usando JADE como entorno multiagente.
3) Evaluar la eficiencia computacional y la sostenibilidad energética del prototipo SMA frente a una arquitectura centralizada, durante el entrenamiento, mediante métricas de tiempo, throughput, CPU, memoria y energía normalizada (J/MB) en escenarios simulados, controlados y replicables.
4) Analizar e interpretar los resultados para validar la eficiencia y sostenibilidad del SMA, sintetizando implicaciones técnicas, éticas y operativas, y señalando desafíos/limitaciones/oportunidades.

---

## OE1 — Modelado de la arquitectura SMA (orquestación del pipeline)

- Enunciado: Modelar la arquitectura de un prototipo de SMA capaz de orquestar y gestionar fases clave del pipeline de ML supervisado, en entornos simulados.
- Enfoque: Arquitectura basada en JADE + backend FastAPI exponiendo métricas y orquestación; simulación de etapas PREPROCESS → TRAIN → EVAL con eventos JSONL.
- Implementación:
  - Documentación de arquitectura: `docs/architecture/architecture.md`, índice en `docs/architecture/README.md`.
  - Puente con JADE, artefactos y acoplamientos: `docs/architecture/bridge_jade.md`.
  - Protocolo de mensajes y eventos: `docs/architecture/message-protocol.md`.
  - Scripts de orquestación/arranque: `scripts/run_jade_experiment.sh`, `scripts/start_stack.sh`.
- Evidencia:
  - Artefactos de orquestación: `data/results/_jade_logs/{agents.json,messages.log,events.jsonl}`.
  - Métricas de orquestación y progreso (backend): `backend/api/main.py` (sección `/metrics`).
- Métricas involucradas: `experiment_last_id`, `experiment_current_stage_idx`, `experiment_current_stage_elapsed_seconds`.
- Incidencias/errores relevantes:
  - Falta de artefactos JADE al inicio → síntesis en `run_jade_experiment.sh` para asegurar continuidad del pipeline.
  - Documentos de arquitectura “movidos” → normalización en `docs/architecture/*` y actualización de enlaces.
- Estado: Cumplido.

## OE2 — Implementación del prototipo SMA con RF y SVM (JADE)

- Enunciado: Implementar el prototipo SMA integrando al menos Random Forest y SVM para ejecución durante el entrenamiento, usando JADE.
- Enfoque: Generador de dataset reproducible + simulador que ejecuta PREPROCESS/ TRAIN_RF/ EVAL_RF/ TRAIN_SVM/ EVAL_SVM y registra eventos; JADE disponible para orquestación y artefactos.
- Implementación:
  - Dataset sintético reproducible: `python-analysis/generate_dataset.py` → `data/raw/synthetic_classification.csv` + `.meta.json` (SHA‑256, parámetros).
  - Simulación de etapas: `python-analysis/simulate_experiment.py` (invoca backend y registra `logs/events.jsonl`).
  - Reporte por ejecución: `python-analysis/report_run.py`.
  - Plataforma JADE y lanzador: `agents/jade-platform/*`, `scripts/run_jade_experiment.sh`.
- Evidencia:
  - Directorios `data/results/<exp_id>/` con `meta.json`, `logs/events.jsonl`, `report/report.html`.
  - Presencia de etapas TRAIN_RF y TRAIN_SVM en eventos y en métricas `/metrics` con sufijos `_by_algo`.
- Métricas involucradas: `train_duration_seconds_last_by_algo`, `train_cpu_avg_percent_last_by_algo`, `train_mem_peak_mb_last_by_algo`, `train_records_per_s_last_by_algo`, `train_avg_watts_last_by_algo` (cuando corresponde).
- Incidencias/errores relevantes:
  - Esquemas históricos con `energy_j_*` heterogéneos → normalización en `aggregate_metrics.py` (watts y Joules derivados) y tolerancia a variantes.
  - Rutas de JADE/CLASSPATH en algunos entornos → script de lanzamiento documentado y fallback de artefactos.
- Estado: Cumplido.

## OE3 — Evaluación de eficiencia y sostenibilidad (SMA vs centralizado)

- Enunciado: Evaluar eficiencia computacional y sostenibilidad energética del SMA frente a una arquitectura centralizada, durante el entrenamiento, con métricas (tiempo, throughput, CPU, memoria, energía normalizada J/MB) en escenarios simulados, controlados y replicables.
- Enfoque: Comparación experimental “control vs tratamiento” como proxy de arquitectura centralizada (invocación directa) vs. orquestada (con/sin artefactos SMA). Se ejecutan cargas equivalentes con semillas dados y dataset congelado.
- Implementación:
  - Ejecución reproducible: `scripts/monitoring_smoke.sh` (dos corridas breves control/tratamiento) y `scripts/run_experiment.sh`.
  - Agregación: `python-analysis/aggregate_metrics.py` → `data/results/aggregate_metrics.csv` con duración, CPU, memoria, throughput, `avg_watts`, `watts_per_mb`, `watts_per_record` y Joules derivados (`joules = avg_watts × duration_s`).
  - Métrica solicitada (J/MB): se deriva como `joules_per_mb = joules / data_mb`; base disponible en CSV (duration_s, avg_watts, data_mb). Puede calcularse en análisis o añadirse al agregador (mejora menor).
  - Observabilidad: Prometheus + Grafana (`infra/compose/*`), dashboards (`infra/compose/grafana/dashboards/*` y `docs/grafana/thesis_minimal.json`).
- Evidencia:
  - CSV consolidado por grupo/algoritmo (control/tratamiento, RF/SVM): `data/results/aggregate_metrics.csv`.
  - Paneles de performance/energía con series `train_*` y `cpu_*`.
  - Scripts y estados del backend: `data/results/_server_state/uvicorn_dashboard.json`, `prom_targets.json`.
- Métricas comparadas (ejemplos):
  - Eficiencia computacional: `train_duration_seconds`, `train_records_per_s_last`, `train_cpu_avg_percent_last`, `train_mem_peak_mb_last`.
  - Energía (watts-first): `train_avg_watts_last`, `watts_per_mb`, `watts_per_record`; derivación a Joules y `joules_per_mb`.
- Incidencias/errores relevantes:
  - RAPL inaccesible en algunos hosts/contendedores → proxy de potencia (`cpu_power_w_proxy`) calibrable (`CPU_POWER_W`), documentado en `docs/energy_plan.md`.
  - Targets de Prometheus en modo host → generación dinámica de `prom_targets.json` con IP de `docker0`.
  - Puertos ocupados → exploración 8000..8010 y persistencia de puerto detectado para clientes/scripts.
- Limitaciones y supuestos:
  - La “arquitectura centralizada” se modela como invocación directa (control) vs. orquestación (tratamiento). Es un proxy válido en prototipo, pero no sustituye una implementación monolítica separada.
  - `joules_per_mb` se computa a partir de campos ya presentes; agregarlo explícitamente al CSV es mejora incremental.
- Estado: Cumplido (en alcance de prototipo y bajo supuestos anteriores).

## OE4 — Análisis e interpretación de resultados (validación y síntesis)

- Enunciado: Analizar e interpretar resultados para validar eficiencia y sostenibilidad del SMA; sintetizar implicaciones técnicas, éticas y operativas; identificar desafíos/limitaciones/oportunidades.
- Enfoque: Uso de CSV consolidado + reportes por ejecución + paneles de Grafana para extraer tendencias y ratios; discusión de amenazas a la validez y ética energética.
- Implementación:
  - Consolidación: `python-analysis/aggregate_metrics.py` y `data/results/aggregate_metrics.csv`.
  - Estadística: `scripts/stats_analysis.sh` y `python-analysis/stats_analysis.py`.
  - Reportes por ejecución: `python-analysis/report_run.py`.
  - Documentación: `docs/achievements/cumplimiento_objetivo_general.md` (Apéndices B y C), `docs/monitoring_spec.md`, `docs/energy_plan.md`.
- Evidencia:
  - Resultados cuantitativos (CSV) y visuales (Grafana) con comparaciones control/tratamiento y por algoritmo (RF/SVM).
  - Discusión de incidencias reales y amenazas a la validez.
- Síntesis (ejemplos de implicaciones):
  - Técnicas: trade‑offs de overhead de orquestación vs. eficiencia en etapas; calibración de `CPU_POWER_W` en ausencia de RAPL.
  - Éticas: reporte transparente de energía (watts/joules), normalizaciones para comparabilidad, evitar claims sin hardware.
  - Operativas: scripts reproducibles, dashboards versionados, trazabilidad de datasets/eventos.
- Desafíos y oportunidades:
  - Integrar RAPL por ventana de entrenamiento en CSV (p. ej., `energy_log.csv`) y exponer `joules_per_mb` directamente.
  - Extender a datasets reales y cargas intensivas; añadir modos paralelos y GPU (con métricas dedicadas).
- Estado: Cumplido.

---

## Conclusión

Los cuatro objetivos específicos se consideran cumplidos en el alcance de prototipo. El repositorio contiene el modelado de arquitectura SMA, su implementación con RF y SVM sobre JADE y backend instrumentado, una evaluación cuantitativa reproducible (eficiencia y energía) con comparación control/tratamiento como proxy de arquitectura centralizada, y el análisis/interpretación con implicaciones y limitaciones claramente documentadas.

## Referencias cruzadas

- Arquitectura: `docs/architecture/README.md`, `architecture.md`, `bridge_jade.md`, `message-protocol.md`
- Observabilidad/energía: `docs/monitoring_spec.md`, `docs/energy_plan.md`, dashboards en `infra/compose/grafana/dashboards/`, `docs/grafana/README.md`
- Cumplimiento objetivo general: `docs/achievements/cumplimiento_objetivo_general.md`
- Pipelines/simulación/análisis: `python-analysis/*.py`, `scripts/*.sh`
 - Metodología: `docs/achievements/metodologia.md`
 - Cronograma (cómo/por qué se lograron las actividades): `docs/achievements/cumplimiento_cronograma.md`
 - Resultados esperados y aporte específico: `docs/achievements/resultados_aporte.md`