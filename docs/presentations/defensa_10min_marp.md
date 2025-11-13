---
marp: true
paginate: true
class: default
headingDivider: 2
theme: gaia
footer: "Defensa — 10 min | Santiago Mazo Orozco"
author: "Santiago Mazo Orozco"
lang: es
---

# Defensa de Trabajo de Grado (10 min)

Eficiencia y Sostenibilidad Computacional en ML con un Enfoque Multiagente (SMA)

Programa: Administración de Sistemas Informáticos  
Fecha: 2025-11-12

---

## Agenda (10 min)

1. Problema y motivación (1:00)  
2. Objetivos (0:40)  
3. Metodología (1:10)  
4. Arquitectura y stack (1:20)  
5. Datos, experimento y métricas (1:10)  
6. Resultados (2:00)  
7. Análisis y validez (1:00)  
8. Conclusiones (0:40)  
9. Aportes (0:40)  
10. Futuro y cierre (0:20)

---

## Problema y motivación

- ML debe evaluarse por precisión y por eficiencia/sostenibilidad.  
- Brecha: poca evidencia comparativa SMA vs centralizado con energía.  
- Impacto: decisiones técnicas y ambientales informadas.

Ref: `docs/Macroproceso.txt` (Intro/Justificación)

---

## Objetivo general

- Diseñar e implementar un prototipo SMA para evaluar eficiencia computacional y sostenibilidad energética en entrenamiento de ML supervisado.  
- Entornos simulados, controlados y replicables.

Ref: `docs/Macroproceso.txt` §4

---

## Objetivos específicos (resumen)

- Implementar SMA con RF y SVM.  
- Evaluar eficiencia y sostenibilidad (tiempo, CPU, memoria, energía normalizada).  
- Analizar e interpretar resultados e implicaciones.

Ref: `docs/Macroproceso.txt` §5; `docs/achievements/objetivos_especificos.{md,tex}`

---

## Metodología (cómo / por qué / para qué)

- Cómo: control (centralizado) vs tratamiento (SMA); n≈10 por grupo; permutaciones (≥5000).  
- Por qué: diferencias rigurosas con trazabilidad y reproducibilidad.  
- Para qué: validar utilidad del SMA y sentar base experimental escalable.

Ref: `docs/achievements/metodologia.{md,tex}`

---

## Arquitectura y stack

- SMA en JADE (Java 21/Maven) + Backend FastAPI (/metrics Prometheus).  
- Observabilidad: Prometheus + Grafana (dashboards).  
- Flujo: PREPROCESS → TRAIN → EVAL; orquestación por agentes.

Ref: `docs/architecture/*`, `docs/bridge_jade.md`, `backend/api/main.py`

---

## Datos, experimento y métricas

- Dataset sintético reproducible (seeds, metadatos).  
- Escenarios: control vs SMA; modelos: RF y SVM.  
- Métricas: time_ms, cpu_avg, mem_peak_mb, records/s, J = W×s; J/MB, W/MB.

Ref: `python-analysis/generate_dataset.py`, `python-analysis/aggregate_metrics.py`, `docs/energy_plan.md`

---

## Resultados (RF)

- TRAIN_RF — tiempo y energía por MB.

![w:480](../../data/results/batch_20251027_145840/figures/TRAIN_RF_time_ms.png)
![w:480](../../data/results/batch_20251027_145840/figures/TRAIN_RF_energy_j_per_mb.png)

Ref: `docs/thesis_results_section.md` §7

---

## Resultados (SVM)

- TRAIN_SVM — tiempo y energía por MB.

![w:480](../../data/results/batch_20251027_145840/figures/TRAIN_SVM_time_ms.png)
![w:480](../../data/results/batch_20251027_145840/figures/TRAIN_SVM_energy_j_per_mb.png)

Ref: `docs/thesis_results_section.md` §7

---

## Análisis inferencial y validez

- Permutaciones (≥5000); H0: sin diferencia entre grupos.  
- Resultado: p ≥ 0.05 en métricas principales (RF y SVM).  
- Amenazas: proxy energético (TDP×CPU), dataset pequeño; mitigación: documentar y escalar.

Ref: `python-analysis/stats_analysis.py`, `data/results/stats_summary.{json,md}`

---

## Conclusiones principales

- SMA funcional y reproducible (monitoreo, reportes, scripts).  
- Sin diferencias significativas en el escenario actual.  
- El marco permite escalar y medir energía directa (RAPL/powercap).

Ref: `docs/conclusions_implications_future_work.md`

---

## Aportes específicos

- Marco reproducible (scripts, dashboards, normalizaciones J/MB).  
- Arquitectura SMA y guía watts-first para energía.  
- Capítulos de metodología, cronograma, resultados y checklist.

Ref: `docs/achievements/resultados_aporte.{md,tex}`

---

## Trabajo futuro y cierre

- Medición directa (RAPL/powercap).  
- Escalar datasets/concurrencia; ampliar modelos (XGBoost/LightGBM).  
- Resiliencia/elasticidad: MTTR, reconfiguración, fallos inducidos.

Gracias. Preguntas.

Refs: `docs/thesis_results_section.md` · `docs/conclusions_implications_future_work.md` · `docs/appendix/reproducibility_checklist.md`

---

## Backups — Definiciones de energía

- J = W × s  
- watts_per_mb = avg_watts / MB_procesados  
- energy_j_total = avg_watts × time_s  
- Proxy: avg_watts ≈ CPU_POWER_W × (cpu_avg/100) (si no hay RAPL)

Ref: `docs/energy_plan.md`, `docs/thesis_results_section.md`

---

## Backups — Configuración experimental

- n≈10 por grupo; control vs SMA.  
- Modelos: RF (parametrización standard), SVM (lineal/RBF según config).  
- Artefactos: CSV agregados, reportes HTML, figuras.

Ref: `scripts/run_batch.*`, `python-analysis/report_run.py`, `data/results/*`

---

## Backups — p-values y tamaños de efecto

- Resumen p-values (permutaciones) y Cliff's δ por etapa/métrica.  
- Interpretación: p≥0.05 → no significativo; |δ| pequeño/medio.

Ref: `data/results/stats_summary.{json,md}`

---

## Backups — Stack de monitoreo

- Prometheus (scrape /metrics) y Grafana (dashboards).  
- Capturas disponibles en `docs/grafana/img/*` (si aplica) y figuras por batch.

Ref: `infra/compose/*`, `docs/grafana/thesis_minimal.json`

---

## Backups — Hardware y entorno

- Toolchain: JDK 21 (Corretto 21), Maven 3.9.6, JADE 4.6.0 (repo local).  
- Backend: FastAPI con endpoint /metrics (Prometheus).  
- Proxy energético: `CPU_POWER_W` calibrable; opción RAPL/powercap en Linux.  
- Reproducibilidad: seeds, metadatos de dataset, artefactos por ejecución.

Ref: `docs/Macroproceso.txt` (Nota técnica), `backend/api/main.py`, `docs/appendix/reproducibility_checklist.md`