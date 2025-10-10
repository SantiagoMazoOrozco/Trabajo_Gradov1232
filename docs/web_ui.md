# UI Web Experimental

Esta interfaz web ligera se monta sobre la misma aplicación FastAPI (`python-analysis/api/main.py`) y permite navegar los experimentos generados en `data/results/`.

## Rutas

- `/` Lista experimentos (id, grupo, fecha) y muestra el contenido de `stats_summary.md` si existe.
- `/experiments/{id}` Detalle de un experimento: métricas de entrenamiento (tiempo, cpu, memoria, energía), evaluación (accuracy, f1) y eventos crudos.

## Cómo ejecutar

Opción A — Levantar dashboard con scripts (recomendado):

```powershell
# Intenta desde el puerto 8001 y avanza si está ocupado. Guarda el PID en data/results/_server_state/uvicorn_dashboard.json
powershell -ExecutionPolicy Bypass -File .\scripts\start_dashboard.ps1 -PortStart 8001 -ApiHost '127.0.0.1' -Verbose
# Para detenerlo:
powershell -ExecutionPolicy Bypass -File .\scripts\stop_dashboard.ps1
```

Opción B — Manual (uvicorn):

```powershell
.\.venv\Scripts\python.exe -m uvicorn python-analysis.api.main:app --host 127.0.0.1 --port 8001
```

Luego abre: http://127.0.0.1:8001/

## Estructura añadida

- `python-analysis/web/templates/` (Jinja2): `base.html`, `experiments.html`, `experiment_detail.html`.
- `python-analysis/web/static/style.css` estilos simples.

## Actualización de datos

La UI lee directamente el filesystem. Cuando generas nuevos experimentos o ejecutas `aggregate_metrics.py` / `stats_analysis.py`, refresca el navegador (F5) para ver cambios.

## Energía y métricas

Las métricas de energía (`energy_j_total`, `energy_j_per_mb`) aparecen en la tabla de entrenamiento si fueron calculadas (endpoints de entrenamiento ya lo hacen). Si un modelo no entrenó, se muestra `-`.

## Extensiones futuras (opcionales)

- Gráficas con Chart.js (comparación energía por algoritmo y grupo).
- Filtros dinámicos por grupo.
- Auto-refresh parcial (HTMX) para nuevas ejecuciones.

## Propósito académico

Sirve como capa de observación y transparencia metodológica: permite al jurado validar que los artefactos existen, las métricas están coherentes y la comparación control vs. treatment es reproducible.
