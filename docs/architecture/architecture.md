# Arquitectura general

Este documento resume la arquitectura del prototipo SMA con foco en componentes, flujos y contratos, enlazando con los detalles en el repositorio.

## Objetivo del sistema

Diseñar e implementar un prototipo basado en Sistemas Multiagente (SMA) para evaluar eficiencia computacional y sostenibilidad energética durante el entrenamiento de algoritmos supervisados de clasificación, en entornos simulados.

## Componentes principales

- Plataforma SMA (JADE): orquesta y registra eventos. Lanzada por `scripts/run_jade_experiment.sh`. Artefactos en `data/results/_jade_logs/`.
- Backend (FastAPI): expone API y métricas Prometheus (`/metrics`), integra RAPL/proxy, consolida progreso.
- Simulador/Análisis (Python): `python-analysis/` (dataset, simulación, reportes, agregación, estadísticas).
- Observabilidad: Prometheus + Grafana por `infra/compose/`.

## Flujos clave

1. Generación de dataset reproducible (`python-analysis/generate_dataset.py`).
2. Orquestación de experimento (`python-analysis/simulate_experiment.py` o JADE): PREPROCESS → TRAIN_* → EVAL_* con eventos a `events.jsonl`.
3. Backend exporta métricas (tiempos, CPU/mem, throughput, potencia, progreso).
4. Prometheus scrapéa targets (host o aislado) desde `data/results/_server_state/prom_targets.json`.
5. Grafana visualiza paneles (`infra/compose/grafana/dashboards/*` o `docs/grafana/thesis_minimal.json`).
6. Agregación a CSV (`python-analysis/aggregate_metrics.py`) + reportes (`python-analysis/report_run.py`).

## Contratos y puntos de integración

- Eventos (JSONL): `ts_utc`, `stage`, `algo`, `duration_s`, `cpu_avg`, `mem_peak_mb`, `records`, `data_mb`, `why`.
- Métricas (Prometheus): prefijo `train_*`, `cpu_package_power_w`, `cpu_power_w_proxy`, `experiment_*`.
- Artefactos SMA: `_jade_logs/agents.json`, `messages.log`, `events.jsonl`.
- RAPL/proxy: `update_energy_accumulator()` y `CPU_POWER_W`.

## Despliegue (local)

- Stack: `./scripts/start_stack.sh` (Prometheus 9090, Grafana 3000, backend en host o aislado).
- Composición: `infra/compose/docker-compose.yml`, `prometheus.yml`, provisioning de datasources/dashboard.

## Referencias

- `docs/architecture/bridge_jade.md`
- `docs/architecture/message-protocol.md`
- `docs/monitoring_spec.md`, `docs/energy_plan.md`
- `docs/achievements/cumplimiento_objetivo_general.md`
