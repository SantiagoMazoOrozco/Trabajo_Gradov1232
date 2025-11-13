# Presentación intermedia — Trabajo de Grado

Autor: Santiago Mazo Orozco  
Tutor: Néstor Darío Duque Méndez  
Fecha: 2025-11-11

## 1. Título y objetivos
- Título: Eficiencia y Sostenibilidad Computacional de Algoritmos de ML… (Enfoque Multiagente)
- Objetivo general y 4 específicos (resumen breve con bullets)

## 2. Motivación y contexto
- Crecimiento de datos, necesidad de eficiencia y sostenibilidad
- SMA como alternativa: autonomía, comunicación, proactividad

## 3. Arquitectura propuesta
- Diagrama SMA y orquestación experimental (referencia a docs/architecture.md)
- Mensajería y agentes clave (preproceso, entrenamiento, evaluación, monitoreo)

## 4. Diseño experimental
- Control vs tratamiento (SMA) — 10 repeticiones por grupo
- Algoritmos: Random Forest, SVM
- Métricas: time_ms, cpu_avg, mem_peak_mb, records_per_s, watts_per_mb; accuracy/f1 en evaluación

## 5. Implementación y pipeline
- Scripts y automatización: scripts/run_batch.*, run_experiment.*, aggregate_metrics, stats_analysis
- Artefactos por experimento (prep/, models/, report/)

## 6. Resultados (resumen)
- Descriptivos por etapa/grupo (Tabla: ver docs/_auto_results_tables.md)
- p-values (perm): no significativos en métricas principales (Tabla: docs/_auto_results_tables.md)
- Tamaños de efecto (Cliff's δ): algunos medios/grandes, pero CIs cruzan 0 (cohens_d_ci.csv)

### Figuras (vinculadas)
- TRAIN_RF time_ms: ![TRAIN_RF_time_ms](../data/results/batch_20251027_145840/figures/TRAIN_RF_time_ms.png)
- TRAIN_SVM time_ms: ![TRAIN_SVM_time_ms](../data/results/batch_20251027_145840/figures/TRAIN_SVM_time_ms.png)
- TRAIN_RF energía/MB: ![TRAIN_RF_energy_j_per_mb](../data/results/batch_20251027_145840/figures/TRAIN_RF_energy_j_per_mb.png)
- TRAIN_SVM energía/MB: ![TRAIN_SVM_energy_j_per_mb](../data/results/batch_20251027_145840/figures/TRAIN_SVM_energy_j_per_mb.png)

## 7. Conclusiones preliminares
- No hay evidencia de diferencias significativas entre control y SMA bajo la carga actual
- Prototipo SMA funcional y replicable; base para escalar

## 8. Trabajo en curso y próximos pasos
- Integrar RAPL/powercap para energía real
- Escenarios de concurrencia y resiliencia (fallos inducidos, métricas de recuperación)
- Aumentar tamaño de datasets y repeticiones
- Redacción final (integración LaTeX: `\input{docs/_auto_results_tables.tex}`)

## 9. Riesgos y mitigaciones
- Variabilidad del entorno —> repeticiones y permutaciones
- Proxy energético —> medición directa

## 10. Cierre
- Repositorio listo para reproducir con scripts y evidencia empaquetada (ZIP)
- Q&A
