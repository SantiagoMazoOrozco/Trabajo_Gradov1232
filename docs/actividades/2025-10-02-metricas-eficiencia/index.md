# Actividad: Métricas de eficiencia y sostenibilidad (2025-10-02)

Estado: Completado

## Objetivo
Cubrir los aspectos del Macroproceso relacionados con:
- Eficiencia del procesamiento de datos (throughput).
- Eficiencia por unidad de carga (CPU y memoria).
- Sostenibilidad energética (J/MB y J/record).

## Cambios realizados
- API (`python-analysis/api/main.py`):
  - Nuevas métricas en `TrainMetrics`: `n_train`, `mb_processed`, `records_per_s`, `data_mb_per_s`, `energy_j_per_record`, `efficiency_cpu_rps_per_pct`, `efficiency_mem_rps_per_mb`.
- Agregación (`python-analysis/aggregate_metrics.py`):
  - Inclusión de columnas para las nuevas métricas.
- Estadística (`python-analysis/stats_analysis.py`):
  - Pruebas de permutación adicionales para `records_per_s` en `TRAIN_RF` y `TRAIN_SVM`.
- Reporte (`python-analysis/report_run.py`):
  - Tabla de entrenamiento muestra records/s, MB/s, J/record, además de energía.
- UI Web:
  - Plantilla de detalle (`python-analysis/web/templates/experiment_detail.html`) ampliada con todas las nuevas métricas.
- Documentación: `docs/experiments.md` ampliado con definiciones.

## Cómo validar
1. Ejecutar lote pequeño:
```powershell
$env:CPU_POWER_W = 50
powershell -ExecutionPolicy Bypass -File .\scripts\run_batch.ps1 -Repeats 3 -SeedBase 42 -MonitorSeconds 10
```
2. Regenerar agregado y análisis:
```powershell
.\.venv\Scripts\python.exe .\python-analysis\aggregate_metrics.py --verbose
.\.venv\Scripts\python.exe .\python-analysis\stats_analysis.py
```
3. Ver la UI: http://127.0.0.1:8000/ y abrir cada experimento.

## Evidencias
- `data/results/aggregate_metrics.csv` con nuevas columnas.
- `data/results/stats_summary.md` con filas de records_per_s.
- Reporte HTML por experimento con throughput y J/record.
- Capturas/recorridos se pueden añadir aquí en caso necesario.

## Observaciones
- Para p-values informativos, se recomiendan ≥10 repeticiones por grupo.
- `CPU_POWER_W` debe ajustarse al hardware para mejorar la fidelidad del proxy de energía.
