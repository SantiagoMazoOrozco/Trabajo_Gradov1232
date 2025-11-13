# Reproducibility Checklist (Proyecto de Grado v1)

Fecha: 2025-11-12

Use esta lista para verificar que cualquier persona pueda replicar los resultados del prototipo.

## Entorno y dependencias
- [ ] Python: versión y entorno virtual documentados (`requirements.txt`).
- [ ] Java JDK 21 y Maven 3.9.x disponibles (o toolchain local según `docs/Macroproceso.txt`).
- [ ] JADE instalado en repo Maven local o provisto (ver instrucciones en `Macroproceso.txt`).
- [ ] Variables de entorno documentadas (`CPU_POWER_W`, puertos, etc.).

## Datos y semillas
- [ ] Dataset sintético generado con `python-analysis/generate_dataset.py`.
- [ ] Metadatos de dataset (`data/raw/synthetic_classification.meta.json`) con parámetros y hash.
- [ ] Semillas (seed base) y repeticiones documentadas para corridas.

## Ejecución y monitoreo
- [ ] Stack de observabilidad levantado (`scripts/start_stack.sh`) con Prometheus y Grafana.
- [ ] Backend levantado (puerto detectado y persistido en `_server_state/uvicorn_dashboard.json`).
- [ ] Corridas control y tratamiento ejecutadas (`scripts/monitoring_smoke.sh` o `scripts/run_experiment.sh`).
- [ ] Artefactos por ejecución generados (`meta.json`, `logs/events.jsonl`, `report/report.html`).

## Agregación y análisis
- [ ] Agregado de métricas (`python-analysis/aggregate_metrics.py` → `data/results/aggregate_metrics.csv`).
- [ ] Análisis estadístico reproducible (`python-analysis/stats_analysis.py` → `data/results/stats_summary.{json,md}`).
- [ ] (Opcional) Figuras generadas para la tesis (`python-analysis/generate_thesis_figures.py`).

## Energía (watts-first)
- [ ] RAPL/powercap disponible o documentado como no disponible.
- [ ] Si RAPL no está, `CPU_POWER_W` calibrado y anotado.
- [ ] Joules derivados (J = W × s) y normalizaciones (J/MB, W/registro) documentadas.

## Tableros y evidencia visual
- [ ] Dashboards importados/precargados (`infra/compose/grafana/dashboards/*`, `docs/grafana/thesis_minimal.json`).
- [ ] Capturas exportadas o placeholders reemplazados (`docs/grafana/img/*`).

## Trazabilidad y reporte
- [ ] Índices y documentos de resultados (`docs/thesis_results_section.{md,tex}`).
- [ ] Capítulos de cumplimiento y metodología (`docs/achievements/*`).
- [ ] Registro de cumplimiento del Macroproceso actualizado (`docs/Macroproceso.txt`).

## Notas de replicación
- Ejecutar primero `start_stack.sh` y un smoke; luego corridas mayores y `aggregate_metrics.sh`/`stats_analysis.sh`.
- Para medición directa de energía, correr backend en host con permisos de powercap. En contenedor usar proxy (documentado).
