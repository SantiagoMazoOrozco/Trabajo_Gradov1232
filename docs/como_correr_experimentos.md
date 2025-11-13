# Cómo correr experimentos (con ejemplos)

Esta guía contiene ejemplos concretos para lanzar experimentos, usar seed, ejecutar batches y post-procesar resultados.

## 1) Lanzar un experimento sencillo

- Desde el dashboard (sección Controls) o por API:
```bash
# Reemplaza <PUERTO> por el puerto publicado (ver backend_host_port.txt)
curl "http://localhost:<PUERTO>/trigger/run-single?group=control"
```

- Opciones:
  - `group`: control | treatment (default: control)
  - `monitor`: segundos de monitorización (0 por defecto)
  - `seed`: número entero opcional para reproducibilidad
  - `report`: true/false para generar reporte de resultados

Ejemplo con seed y reporte:
```bash
curl "http://localhost:<PUERTO>/trigger/run-single?group=treatment&seed=123&report=true"
```

## 2) Ejecutar un batch

```bash
curl "http://localhost:<PUERTO>/trigger/run-batch?repeats=5&monitor=10"
```

También puedes usar los scripts bash directamente (útil si prefieres correr fuera del backend):
```bash
bash scripts/run_experiment.sh --group control --id exp_demo_ctrl --monitor-seconds 5 --report
bash scripts/run_experiment.sh --group treatment --id exp_demo_treat --monitor-seconds 5 --report
bash scripts/run_batch.sh --repeats 5 --monitor-seconds 10
```

## 3) Agregar métricas y análisis estadístico

Tras ejecutar runs, consolida y calcula estadísticas:
```bash
bash scripts/aggregate_metrics.sh
bash scripts/stats_analysis.sh
```

Archivos generados en `data/results/`:
- `aggregate_metrics.csv` – todas las filas de métricas por etapa/experimento
- `stats_summary.json` / `stats_summary.md` – resumen de estadísticas y comparación control vs treatment

## 4) Ver resultados en la UI

- Backend UI de control: `http://localhost:<PUERTO>/control`
- Lista de experimentos y detalle: `http://localhost:<PUERTO>/`
- Dashboard Grafana: `http://localhost:3000`

## 5) Métricas del sistema (CPU/RAM/Watts)

- Ya disponibles (derivadas del pipeline):
  - `train_cpu_avg_percent_last`, `train_mem_peak_mb_last`, `train_records_per_s_last`, `train_avg_watts_last`, `cpu_power_w_proxy`.
- Opción avanzada (host completo): añadir `node-exporter` al compose y rasparlo desde Prometheus.
  - Nota: si el host no puede descargar imágenes Docker por red, puedes usar un fallback basado en psutil desde el backend.

## 6) Modo Live de demo (WIP, sin hilos)

Calcula valores de watts y rps por raspado de Prometheus, sin hilos en background:
```bash
curl "http://localhost:<PUERTO>/trigger/live-start?seconds=60"
# ... observar paneles Live ...
curl "http://localhost:<PUERTO>/trigger/live-stop"
```

## 7) Consejos de reproducibilidad

- Guarda el seed en el nombre del experimento (o conserva el seed en tu tracking).
- Consolida siempre con `aggregate_metrics.sh` tras cada batch.
- Verifica tu dataset congelado en `data/raw` y su hash `.meta.json`.
