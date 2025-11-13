# Actividad 2 — Fase 2: Integración SMA/JADE y Métricas Extendidas (2025-10-02)

Estado: Completado

## Alcance
- Integración orquestable desde SMA/JADE vía CLI puente.
- Métricas extendidas de eficiencia y sostenibilidad en entrenamiento.
- Ejecución y análisis end-to-end con evidencia (control vs treatment).
- Actualización de Macroproceso (Anexo B) con definiciones precisas.

## Evidencias técnicas
- Puente CLI: `python-analysis/agent_cli.py`
  - Subcomandos: `preprocess`, `train`, `evaluate`.
  - Entradas por flags o `--payload-file` (JSON); salida JSON y `--out`.
- Documentación puente: `docs/bridge_jade.md` y referencia en `docs/experiments.md`.
- API y UI: `python-analysis/api/main.py` sirve endpoints y dashboard (`/`, `/experiments/{id}`).
- Scripts: `scripts/run_experiment.ps1`, `scripts/run_batch.ps1` (API único por batch; seeds y grupos).
- Agregación y estadística: `python-analysis/aggregate_metrics.py`, `python-analysis/stats_analysis.py`.
- Macroproceso actualizado: `docs/Macroproceso.txt` (Anexo B con throughput, J/record, eficiencias CPU/Mem).

## Métricas cubiertas
- Throughput: `records_per_s`, `data_mb_per_s`.
- Energía proxy: `energy_j_total`, `energy_j_per_mb`, `energy_j_per_record`.
- Eficiencias: `efficiency_cpu_rps_per_pct`, `efficiency_mem_rps_per_mb`.

## Resultado de corrida de evidencia (1× por grupo)
- Experimentos: `control_20251002_100959_7288`, `treatment_20251002_101009_3518`.
- Artefactos:
  - `data/results/aggregate_metrics.csv`
  - `data/results/stats_summary.md` y `.json`
- Resumen stats (p-values aproximados, N=10000):
  - TRAIN_RF time_ms: ~0.6532
  - TRAIN_SVM time_ms: 1.0
  - TRAIN_RF records_per_s: 1.0
  - TRAIN_SVM records_per_s: 1.0
  - TRAIN_RF energy_j_per_mb: ~0.6532
  - TRAIN_SVM energy_j_per_mb: ~0.6532
  - EVAL_* accuracy/f1: ≥0.33

Nota: con 1× por grupo es demostrativo; para significancia recomendada ≥10×.

## Resultados (5× por grupo) y artefactos
- API en: http://127.0.0.1:8001 (8000 estaba ocupado)
- Resumen stats: `data/results/stats_summary.md`
- JSON stats: `data/results/stats_summary.json`
- Agregado: `data/results/aggregate_metrics.csv`

p-values (control vs treatment, N=10000):
- TRAIN_RF time_ms: 0.4232
- TRAIN_SVM time_ms: 0.3747
- TRAIN_RF records_per_s: 0.5294
- TRAIN_SVM records_per_s: 0.3652
- TRAIN_RF energy_j_per_mb: 0.3835
- TRAIN_SVM energy_j_per_mb: 0.4968
- EVAL_RF accuracy: 0.6809 | f1: 0.6738
- EVAL_SVM accuracy: 0.1437 | f1: 0.1376

Interpretación: con 5× por grupo no se observan diferencias estadísticamente significativas (p < 0.05) entre control y treatment bajo este setup; el procedimiento queda reproducible para corridas mayores.

## Cómo reproducir (rápido)
1) Lote mínimo (1× por grupo):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_batch.ps1 -Repeats 1 -SeedBase 52 -MonitorSeconds 0
```
2) Ver dashboard: `http://127.0.0.1:8000/` (si el API está levantado) y/o revisar los artefactos.

## Conclusión
Fase 2 de la Actividad 2 completada: integración operativa con orquestación vía CLI para SMA/JADE, métricas ampliadas alineadas al Macroproceso, y pipeline de ejecución/análisis replicable con evidencia actualizada.
