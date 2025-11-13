# Grafana — Guía rápida para la tesis

Este README explica cómo abrir los tableros de Grafana provistos, importar uno mínimo para la tesis y solucionar problemas comunes.

## 1) Arranque del stack

- Requisitos: Docker, Docker Compose.
- Inicia Prometheus (9090) y Grafana (3000) y el backend (host o aislado):

```bash
./scripts/start_stack.sh
```

- Accede a Grafana: http://localhost:3000
  - Usuario: `admin`  
  - Contraseña: `admin`

La fuente de datos Prometheus se aprovisiona automáticamente desde `infra/compose/provisioning/datasources/datasource.yml` (URL interna `http://prometheus:9090`).

## 2) Dashboards incluidos

- Dashboards de ejemplo versionados en `infra/compose/grafana/dashboards/`:
  - `performance.json` — CPU, memoria, throughput, tiempo de etapa.
  - `energy.json` — Potencia promedio y normalizaciones energéticas.
  - `resilience.json` — Resiliencia, eventos y señales.
- Dashboard mínimo para la tesis: `docs/grafana/thesis_minimal.json` (importación manual explicada abajo).

## 2.1) Imágenes y evidencias

Puedes guardar capturas en `docs/grafana/img/` y referenciarlas desde la tesis. Sugerencias:

![Login](img/01-login.svg)
![Home](img/02-home.svg)
![Datasource Prometheus](img/03-datasource-prometheus.svg)
![Import Dashboard](img/04-import-dashboard.svg)
![Panel Performance](img/05-performance-panel.svg)
![Panel Energy](img/06-energy-panel.svg)
![Panel Progress](img/07-progress-panel.svg)

## 3) Importar un dashboard

1. En Grafana, click en “Dashboards” → “New” → “Import”.
2. Elige “Upload JSON” y selecciona alguno de:
   - `infra/compose/grafana/dashboards/performance.json`
   - `infra/compose/grafana/dashboards/energy.json`
   - `infra/compose/grafana/dashboards/resilience.json`
   - `docs/grafana/thesis_minimal.json`
3. Asegúrate de seleccionar la datasource “Prometheus” si se solicita.

## 4) Métricas clave (nombres en Prometheus)

Según `docs/monitoring_spec.md` y el backend (`/metrics`):

- Eficiencia computacional
  - `train_duration_seconds` (y derivados)
  - `train_cpu_avg_percent_last`
  - `train_mem_peak_mb_last`
  - `train_records_per_s_last`
  - `train_data_mb_per_s_last`
  - `train_efficiency_cpu_rps_per_pct_last`
  - `train_efficiency_mem_rps_per_mb_last`
- Energía (watts-first)
  - `cpu_package_power_w` (si RAPL disponible)
  - `cpu_power_w_proxy`
  - `train_avg_watts_last`
  - `train_watts_per_mb_last`
  - `train_watts_per_record_last`
- Progreso
  - `experiment_last_id`
  - `experiment_current_stage_idx`
  - `experiment_current_stage_elapsed_seconds`

Nota: Algunas métricas pueden estar disponibles con variante `_by_algo`. Ajusta el panel para RF/SVM según necesidad.

## 5) Generar datos rápidamente

Ejecuta un smoke test que levanta el stack, detecta el puerto del backend, corre dos cargas breves y agrega resultados:

```bash
./scripts/monitoring_smoke.sh
```

Luego abre Grafana y explora los tableros.

## 6) Solución de problemas (FAQ)

- “Grafana está vacía / no hay métricas”
  - Verifica que Prometheus tenga targets: http://localhost:9090/targets  
    Debe existir un job `app` con estado “UP”.
  - Revisa `data/results/_server_state/prom_targets.json` (lo genera `scripts/start_stack.sh`).
- “Prometheus no alcanza al backend (modo host)”
  - `scripts/start_stack.sh` calcula la IP de `docker0`. En entornos sin `docker0` (p. ej., Podman), edita manualmente `prom_targets.json` para apuntar al host.
- “RAPL no aparece (cpu_package_power_w = 0)”
  - Ejecuta backend en host (no contenedor) y garantiza permisos de lectura de `powercap`; usa el proxy `cpu_power_w_proxy` como respaldo.
- “Conflicto de puertos (8000, 3000, 9090)”
  - Libera puertos o ajusta variables (`BACKEND_PORT`) y reinicia. El backend en host busca puertos libres 8000..8010.

## 7) Referencias

- `docs/monitoring_spec.md`
- `docs/energy_plan.md`
- `docs/achievements/cumplimiento_objetivo_general.md` (sección 4.1 y Apéndices)
