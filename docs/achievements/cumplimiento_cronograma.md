# Cumplimiento del Cronograma (Actividades 1–8)

Este documento explica, para cada actividad del cronograma, cómo se ejecutó y por qué se logró satisfactoriamente, con la evidencia correspondiente en el repositorio.

Resumen: todas las actividades 1–8 fueron marcadas como COMPLETADAS (ver `docs/Macroproceso.txt`, “Registro de cumplimiento”).

---

## Actividad 1: Revisión de Literatura y Definición de Metodología
- Cómo se realizó
  - Revisión sistemática y análisis documental de literatura académica/industrial/regulatoria.
  - Definición del enfoque mixto (cuantitativo predominante + cualitativo), del diseño (experimental/cuasi), y la operacionalización (VI/VD, métricas, energía J/MB).
  - Redacción del capítulo de metodología (MD + LaTeX).
- Por qué se logró
  - Existencia de objetivos claros y alcance aplicado; trazabilidad con el Macroproceso.
  - Disponibilidad de bases documentales y especificaciones internas (monitoreo, energía, arquitectura) que permitieron alinear teoría y práctica.
- Evidencia
  - `docs/achievements/metodologia.md`, `docs/achievements/metodologia.tex`
  - `docs/monitoring_spec.md`, `docs/energy_plan.md`
  - `docs/architecture/README.md`
- Resultado: COMPLETADA

## Actividad 2: Diseño de la Arquitectura del SMA y del Experimento
- Cómo se realizó
  - Modelado de agentes, interacciones y protocolo de mensajes; definición del puente JADE y del flujo PREPROCESS→TRAIN→EVAL.
  - Estructura de observabilidad: Prometheus + Grafana (datasource, dashboards versionados).
  - Compose del stack y scripts de smoke para validar endpoints y scraping.
- Por qué se logró
  - Modularidad por agentes y separación de preocupaciones; plantillas de infraestructura y dashboards reutilizables.
  - Documentación de arquitectura y monitoreo que guió decisiones y pruebas.
- Evidencia
  - `docs/architecture/*` (índice, arquitectura, bridge, message-protocol)
  - `infra/compose/*` (servicios, Prometheus, Grafana)
  - `docs/grafana/README.md`, `docs/grafana/thesis_minimal.json`
- Resultado: COMPLETADA

## Actividad 3: Implementación y Desarrollo de Prototipos
- Cómo se realizó
  - Implementación del orquestador SMA en JADE y del backend FastAPI con métricas (estilo Prometheus) para las fases del pipeline y entrenamiento de RF/SVM.
  - Scripts de ejecución (single/batch) y utilidades de simulación.
- Por qué se logró
  - Integración técnica clara entre agentes, backend y telemetría.
  - Disponibilidad de toolchain (JDK, Maven) y guías reproducibles.
- Evidencia
  - `agents/jade-platform/*` (módulo JADE)
  - `backend/api/main.py`
  - `python-analysis/simulate_experiment.py`, `python-analysis/monitor_run.py`
  - `scripts/run_experiment.*`, `scripts/run_batch.*`, `scripts/monitoring_smoke.sh`
- Resultado: COMPLETADA

## Actividad 4: Recolección y Pre-procesamiento de Datos Experimentales
- Cómo se realizó
  - Generación de dataset sintético reproducible (semillas y metadatos).
  - Ejecuciones controladas para grupos control (centralizado) y tratamiento (SMA) con registro de meta y eventos.
  - Consolidación en CSV y preparación para análisis.
- Por qué se logró
  - Procedimientos estandarizados (scripts) y registro exhaustivo (meta, eventos, reportes).
  - Estructura de directorios de resultados por ejecución/lote.
- Evidencia
  - `python-analysis/generate_dataset.py`, `data/raw/*`
  - `data/results/<exp_id>/*` (meta, eventos, reportes)
  - `python-analysis/aggregate_metrics.py`, `data/results/aggregate_metrics.csv`
- Resultado: COMPLETADA

## Actividad 5: Análisis e Interpretación de Datos
- Cómo se realizó
  - Agregación y análisis estadístico (descriptivo e inferencial: permutaciones / t-test o Mann-Whitney según supuestos).
  - Reportes HTML por ejecución y resúmenes consolidados.
- Por qué se logró
  - Pipeline analítico en Python con scripts versionados y reproducibles.
  - Métricas homogéneas y normalizadas (incluyendo energía) para comparaciones justas.
- Evidencia
  - `python-analysis/aggregate_metrics.py`, `python-analysis/stats_analysis.py`
  - `data/results/aggregate_metrics.csv`, `data/results/stats_summary.{json,md}`
  - `python-analysis/report_run.py`, `data/results/*/report/report.html`
- Resultado: COMPLETADA

## Actividad 6: Visualización de Hallazgos y Elaboración de Modelos
- Cómo se realizó
  - Dashboards Grafana para CPU/Mem/Throughput/Energía y progreso; guía de importación y troubleshooting.
  - Generación de figuras para la tesis cuando aplica.
- Por qué se logró
  - Dashboards versionados y datasource provisto; guía operativa clara.
  - Métricas expuestas en tiempo real por el backend.
- Evidencia
  - `docs/grafana/README.md`, `docs/grafana/thesis_minimal.json`, `docs/grafana/img/*`
  - `python-analysis/generate_thesis_figures.py` (si aplica)
- Resultado: COMPLETADA

## Actividad 7: Redacción del Reporte de Resultados
- Cómo se realizó
  - Redacción de capítulos en formato tesis (MD + LaTeX) con evidencias, errores/incidencias y validez.
  - Integración de resultados, gráficos y referencias cruzadas.
- Por qué se logró
  - Base analítica consolidada y documentación técnica previa.
  - Flujo de trabajo reproducible y activos versionados.
- Evidencia
  - `docs/thesis_results_section.{md,tex}`
  - `docs/achievements/cumplimiento_objetivo_general.{md,tex}`
  - `docs/achievements/objetivos_especificos.{md,tex}`
- Resultado: COMPLETADA

## Actividad 8: Consolidación de Conclusiones, Implicaciones y Trabajos Futuros
- Cómo se realizó
  - Síntesis de hallazgos y discusión de limitaciones, amenazas a la validez, implicaciones técnicas/éticas y roadmap.
- Por qué se logró
  - Evidencia cuantitativa/cualitativa suficiente y documentación continua del proceso.
  - Material de apoyo (metodología, energía, observabilidad, arquitectura) consolidado.
- Evidencia
  - `docs/conclusions_implications_future_work.md`
  - `docs/future_work_roadmap.md`, `docs/resilience_test_scenarios.md`
- Resultado: COMPLETADA

---

## Factores transversales de éxito
- Planificación y trazabilidad: Macroproceso y objetivos claros; capítulos de metodología y arquitectura como guías.
- Reproducibilidad: scripts de ejecución/analítica y estructura de datos/resultados consistentemente versionadas.
- Observabilidad: Prometheus + Grafana facilitaron validación, diagnóstico y comunicación de resultados.
- Normalizaciones energéticas: enfoque “watts-first” con J/MB permitió comparaciones justas sin depender siempre de RAPL.

## Referencias cruzadas
- Macroproceso (estado y cronograma): `docs/Macroproceso.txt`
- Metodología: `docs/achievements/metodologia.{md,tex}`
- Arquitectura: `docs/architecture/*`
- Observabilidad/Energía: `docs/monitoring_spec.md`, `docs/energy_plan.md`, `docs/grafana/*`
- Cumplimiento objetivos: `docs/achievements/cumplimiento_objetivo_general.{md,tex}`, `docs/achievements/objetivos_especificos.{md,tex}`
