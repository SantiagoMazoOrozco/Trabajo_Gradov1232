# Matriz de Cumplimiento — Objetivos y Actividades

Fecha: 2025-11-11

Este documento mapea los objetivos (general y específicos) y actividades del Macroproceso contra la evidencia disponible en el repositorio, señalando brechas y acciones.

## Objetivo General
Diseñar e implementar un prototipo de arquitectura SMA para evaluar eficiencia computacional y sostenibilidad energética durante el entrenamiento de algoritmos de ML supervisado de clasificación.

Estado: Cumplido (prototipo SMA + pipeline experimental + análisis)

## Objetivos Específicos

| Objetivo específico | Criterio de cumplimiento | Evidencia principal | Estado |
|---|---|---|---|
| 1. Modelar la arquitectura SMA para orquestar fases (ingesta, preproceso, preparación de datos) | Arquitectura documentada y trazabilidad de fases en pipeline | docs/architecture.md; docs/message-protocol.md; docs/actividades/2025-10-02-*; scripts/run_experiment.* | COMPLETADO |
| 2. Implementar prototipo integrando RF y SVM usando JADE | Ejecución de entrenamientos RF/SVM con orquestación; artefactos de modelos | agents/jade-platform/*; data/results/*/models/*.pkl; scripts/run_jade_*.ps1 | COMPLETADO |
| 3. Evaluar eficiencia y sostenibilidad en entrenamiento (tiempo, throughput, CPU, memoria, Joules/MB) comparando control vs SMA | Métricas agregadas y pruebas estadísticas (permutación) por grupo y etapa | data/results/aggregate_metrics.csv; data/results/stats_summary.{json,md}; docs/thesis_results_section.md (Sec. 4–5) | COMPLETADO |
| 4. Analizar e interpretar resultados y sintetizar implicaciones | Sección de resultados y conclusiones redactadas | docs/thesis_results_section.md; docs/conclusions_implications_future_work.md; figures del batch | COMPLETADO |

Notas:
- Métrica energética usa proxy (CPU_POWER_W×utilización). Lectura directa RAPL/powercap propuesta como trabajo futuro (ver Sec. 8 de resultados).
- La API backend está vacía actualmente (`backend/api/`), pero no afecta la ejecución del pipeline de experimentos y análisis.

## Actividades del Macroproceso (1–8)

| Actividad | Evidencia | Estado |
|---|---|---|
| 1. Revisión de Literatura y Metodología | docs/Actividad1_Revision_Metodologia.md; docs/methodology.md; docs/experiment-design.md | COMPLETADO |
| 2. Diseño Arquitectura SMA y Experimento | docs/architecture.md; docs/toolchain.md; docs/actividades/2025-10-02-* | COMPLETADO |
| 3. Implementación y Prototipos | agents/jade-platform/; scripts/*; python-analysis/* | COMPLETADO |
| 4. Recolección/Pre-proceso | data/raw/*; data/results/*/prep/ | COMPLETADO |
| 5. Análisis e Interpretación | data/results/stats_summary.{json,md}; python-analysis/stats_analysis.py | COMPLETADO |
| 6. Visualización/Modelos | data/results/batch_*/figures/*; python-analysis/report_run.py | COMPLETADO |
| 7. Redacción de Resultados | docs/thesis_results_section.md (+ tablas LaTeX en docs/_auto_results_tables.tex) | COMPLETADO |
| 8. Conclusiones e Implicaciones | docs/conclusions_implications_future_work.md | COMPLETADO |

## Brechas y acciones sugeridas
- Energía real (RAPL/powercap): integrar lectura directa y comparar vs proxy.
- Escalabilidad y resiliencia: diseñar escenario con concurrencia de agentes, fallos inducidos y metricado de recuperación (las filas RESILIENCE en CSV están vacías: plan de instrumentación).
- Backend API: decidir mantener o retirar del diseño; si se mantiene, restituir endpoints mínimos o documentar su reemplazo.

## Conclusión
Según los criterios del tutor (cumplimiento de objetivos y actividades), el proyecto está en cumplimiento. Se dejaron abiertas líneas de mejora para cerrar brechas antes del cierre de semestre (ver roadmap).
