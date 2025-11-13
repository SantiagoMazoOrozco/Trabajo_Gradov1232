# Especificación de Monitoreo (Derivada de Macroproceso.txt)

Este documento mapea cada dimensión y métrica descrita en `Macroproceso.txt` con:
- Nombre de métrica Prometheus (actual o propuesta)
- Fuente (script, endpoint, evento)
- Panel Grafana esperado
- Estado (OK / PENDIENTE)

## 1. Eficiencia Computacional
| Dimensión | Métrica Macroproceso | Métrica Prometheus | Fuente | Panel | Estado |
|-----------|----------------------|--------------------|--------|-------|--------|
| Tiempo ejecución | Tiempo total (ms) | train_duration_seconds (sum) / train_duration_seconds_last{algo} | /metrics agrega CSV | sma-overview | OK |
| Rendimiento | Throughput (reg/s) | train_records_per_s_last / train_records_per_s_last_by_algo | CSV derivado | sma-overview | OK |
| CPU uso promedio | CPU % | train_cpu_avg_percent_last / _by_algo | CSV derivado | sma-overview | OK |
| Memoria pico | Mem peak MB | train_mem_peak_mb_last / _by_algo | CSV derivado | sma-overview | OK |
| Datos procesados | MB/s | train_data_mb_per_s_last | CSV derivado | performance stub | OK |
| Eficiencia CPU | reg/s / %CPU | train_efficiency_cpu_rps_per_pct_last / _by_algo | /metrics (CSV derivado) | sma-overview | OK |
| Eficiencia Mem | reg/s / MB | train_efficiency_mem_rps_per_mb_last / _by_algo | /metrics (CSV derivado) | sma-overview | OK |

## 2. Potencia y Eficiencia Energética (Watts)
| Métrica | Prometheus | Fuente | Estado |
|---------|------------|--------|--------|
| Potencia instantánea CPU (RAPL) | cpu_package_power_w | RAPL delta (si hardware disponible) | OK (si hardware) |
| Potencia proxy | cpu_power_w_proxy | /metrics: TDP * cpu_avg | OK |
| Potencia promedio (último TRAIN) | train_avg_watts_last / train_avg_watts_last_by_algo | /metrics (CSV derivado o RAPL) | OK |
| W/MB (último TRAIN) | train_watts_per_mb_last / train_watts_per_mb_last_by_algo | /metrics (CSV derivado) | OK |
| W/record (último TRAIN) | train_watts_per_record_last / train_watts_per_record_last_by_algo | /metrics (CSV derivado) | OK |
| Joules acumulados CPU (opcional) | cpu_package_energy_j | RAPL directa | Opcional (sin panel) |

## 3. Adaptabilidad y Resiliencia
| Métrica | Prometheus | Fuente | Estado |
|---------|------------|--------|--------|
| Fallos inyectados | failures_total | RESILIENCE fila CSV | OK |
| Fallos recuperados | recoveries_total | RESILIENCE fila CSV | OK |
| Tasa recuperación | recovery_rate | RESILIENCE fila CSV | OK |
| MTTR (mean/p95) | (export pendiente) | recovery_time_ms_mean / p95 | PENDIENTE |
| Reconfiguración autónoma | (definir) | eventos JADE futuros | PENDIENTE |

## 4. Escalabilidad
| Métrica | Prometheus | Fuente | Estado |
|---------|------------|--------|--------|
| Tamaño dataset | (definir: dataset_rows) | meta + generador | PENDIENTE |
| Throughput vs tamaño | Panel combinación | Métricas existentes + dataset size | PENDIENTE |

## 5. Progreso Experimental
| Métrica | Prometheus | Fuente | Estado |
|---------|------------|--------|--------|
| Etapa actual (índice hash) | experiment_current_stage_idx | Último evento en events.jsonl | OK |
| Duración etapa actual | experiment_current_stage_elapsed_seconds | Cálculo dinámico | OK |
| Último experimento | experiment_last_id | FS (último dir) | OK |
| Timestamp inicio etapa | experiment_stage_started_ts | events.jsonl | PENDIENTE |

## Próximas Implementaciones
1. Exponer etiqueta legible de etapa actual (no solo hash), por ejemplo experiment_current_stage_name{stage="TRAIN_RF"}.
2. Añadir paneles de serie temporal para train_avg_watts_last y cpu_package_power_w (si hardware) para ver tendencias.
3. Incluir MTTR mean/p95 como gauges si existen valores (>0).
4. Definir dataset_rows desde metadatos del generador sintético y correlacionar con throughput.

## Referencia rápida de fuentes
- aggregate_metrics.csv: métricas derivadas (tiempo, CPU, memoria, eficiencia, energía).
- events.jsonl: secuencia de eventos de etapas (PREPROCESS_*, TRAIN_*, EVAL_*).
- Prometheus /metrics: resumen dinámico + indicadores agregados.
- RAPL: lectura directa (si hardware disponible) para energía acumulada.

## Estado Resumen
| Categoría | % Cobertura Implementada |
|-----------|--------------------------|
| Eficiencia Computacional | ~90% |
| Potencia/Energía (Watts) | ~75% (proxy y watts directos si hardware) |
| Resiliencia | ~40% |
| Escalabilidad | ~0% (definida, no instrumentada) |
| Progreso vivo | ~70% |

---
Actualizado: 2025-11-11 (watts-first)
