# Actividad 1: Revisión de Literatura y Definición de Metodología

Estado: Completado

## Evidencias de Revisión de Literatura
- Macroproceso.txt
  - Sección 6. ANTECEDENTES: síntesis de trabajos relevantes (SMA, green computing y eficiencia energética en ML).
  - Sección 10. BIBLIOGRAFÍA CITADA: referencias base (Braubach & Pokahr 2019; Chung et al. 2025; Kuzin 2022; Paik 2024; Rodriguez 2024; Yu 2022).
  - Sección 11. REFERENCIAS ADICIONALES: repertorio extendido de fuentes.
- docs/baf_integration_plan.md: análisis de encaje de BAF y oportunidades de integración.

Observación: Las referencias están consolidadas; si se requiere un estilo específico (APA/IEEE), se puede normalizar el formato y añadir DOI/URL en una iteración breve.

## Evidencias de Definición de Metodología
- Macroproceso.txt
  - Sección 7. METODOLOGÍA: enfoque (cuantitativo con complemento cualitativo), diseño experimental, operacionalización de variables y dimensiones (eficiencia, adaptabilidad, escalabilidad y sostenibilidad).
  - Anexos (agregados):
    - Anexo A: Mapeo de artefactos del repositorio al Macroproceso.
    - Anexo B: Método de estimación de energía (proxy) y supuestos.
    - Anexo C: Procedimiento de ejecución y análisis (pipeline reproducible).
- Documentos y scripts operativos (metodología ejecutable):
  - docs/experiments.md: ejecución individual y por lotes; agregación y análisis estadístico.
  - python-analysis/stats_analysis.py: pruebas de permutación por etapa/métrica (tiempo, energía/MB, accuracy, f1, y throughput).
  - scripts/run_experiment.ps1 / scripts/run_batch.ps1: orquestación reproducible, grupos control vs. treatment, semillas.
  - python-analysis/api/main.py: cálculo de métricas de eficiencia y energía.
  - python-analysis/aggregate_metrics.py / report_run.py: agregación y reporte por experimento.
  - UI Web: navegación de resultados (`/`, `/experiments/{id}`) — docs/web_ui.md.

## Criterios de Aceptación Cubiertos
- Revisión de literatura pertinente y citada en el documento base.
- Metodología definida y operacionalizada con scripts, métricas y análisis replicables.
- Procedimientos documentados y trazables (experimentos, agregación, análisis, UI y reportes).

## Sugerencias de Mejora (opcionales)
- Normalizar citas al estilo requerido (APA/IEEE) y agregar DOIs/URLs.
- Si se desea un enfoque sistemático, añadir un breve protocolo (criterios de inclusión/exclusión, bases consultadas, proceso de selección tipo PRISMA) en un anexo adicional.
