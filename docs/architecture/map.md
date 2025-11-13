# Mapa de Arquitectura — Componentes y Responsabilidades

Este mapa sintetiza los componentes, sus responsabilidades, puntos de integración y artefactos generados.

## 1. Componentes

- JADE (Plataforma SMA)
  - Responsabilidad: orquestación multiagente, coordinación de etapas, emisión de eventos.
  - Artefactos: `_jade_logs/agents.json`, `_jade_logs/messages.log`, `_jade_logs/events.jsonl`.
  - Lanzamiento: `scripts/run_jade_experiment.sh` → `org.gaia.sma.RunJade`.

- Backend (FastAPI)
  - Responsabilidad: API de orquestación y observabilidad; exposición `/metrics` (Prometheus); lectura RAPL/proxy; progreso experimental.
  - Archivos: `backend/api/main.py`.

- Simulación/Análisis (Python)
  - Responsabilidad: generar dataset, ejecutar etapas PREPROCESS/TRAIN/EVAL, consolidar métricas, reportar y estadística.
  - Archivos: `python-analysis/generate_dataset.py`, `simulate_experiment.py`, `aggregate_metrics.py`, `report_run.py`, `stats_analysis.py`.

- Observabilidad (Prometheus/Grafana)
  - Responsabilidad: scraping de métricas, paneles y análisis visual.
  - Archivos: `infra/compose/docker-compose.yml`, `infra/compose/prometheus.yml`, `infra/compose/provisioning/datasources/datasource.yml`, dashboards en `infra/compose/grafana/dashboards/`.

## 2. Flujos de datos

1) PREPROCESS/ TRAIN/ EVAL emiten `events.jsonl` (Simulador o JADE).
2) Backend agrega métricas recientes y potencia (RAPL/proxy) → `/metrics`.
3) Prometheus scrapéa el backend (targets en `data/results/_server_state/prom_targets.json`).
4) Grafana visualiza paneles; Python consolida CSV en `data/results/aggregate_metrics.csv`.

## 3. Métricas clave

- Eficiencia: `train_duration_seconds`, `train_cpu_avg_percent_last`, `train_mem_peak_mb_last`, `train_records_per_s_last`, `train_data_mb_per_s_last`.
- Energía: `cpu_package_power_w`, `cpu_power_w_proxy`, `train_avg_watts_last`, `train_watts_per_mb_last`, `train_watts_per_record_last`.
- Progreso: `experiment_last_id`, `experiment_current_stage_idx`, `experiment_current_stage_elapsed_seconds`.

## 4. Contratos

- Eventos (JSONL): `ts_utc`, `stage`, `algo`, `duration_s`, `cpu_avg`, `mem_peak_mb`, `records`, `data_mb`, `why`.
- CSV agregado: por etapa/algoritmo con watts y normalizaciones; joules derivados.

## 5. Despliegue y ejecución

- Stack local: `./scripts/start_stack.sh`.
- Smoke test: `./scripts/monitoring_smoke.sh`.
- Experimento: `./scripts/run_experiment.sh`.
- Agregación y análisis: `./scripts/aggregate_metrics.sh`, `./scripts/stats_analysis.sh`.

## 6. Referencias cruzadas

- `docs/architecture/architecture.md` — visión general
- `docs/architecture/bridge_jade.md` — detalles JADE
- `docs/architecture/message-protocol.md` — protocolo de mensajes y eventos
- `docs/monitoring_spec.md`, `docs/energy_plan.md`
- `docs/achievements/cumplimiento_objetivo_general.md`
