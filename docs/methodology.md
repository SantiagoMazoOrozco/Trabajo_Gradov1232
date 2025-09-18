# Metodología y justificación experimental

Este anexo documenta decisiones metodológicas, criterios de evaluación y controles de validez utilizados en el proyecto. Busca que cualquier tercero pueda comprender, replicar y auditar los resultados.

## Diseño experimental

- Objetivo: evaluar un pipeline supervisado (RF y SVM) sobre un dataset sintético bajo ejecución controlada, con alta observabilidad y trazabilidad de decisiones.
- Variables:
  - Independientes: algoritmo (RF/SVM), hiperparámetros, semilla aleatoria, tamaño de prueba, escalado.
  - Dependientes: accuracy, F1-macro, tiempo de entrenamiento (ms), CPU promedio (%), pico de memoria (MB).
- Tratamientos: RF(n_estimators=100), SVM(kernel=rbf, C=1.0). Semilla fija 42.
- Repeticiones: por corrida (ExperimentId), con agregación en `data/results/aggregate_metrics.csv`.

## Datos y preprocesamiento

- Dataset: `data/raw/synthetic_classification.csv` (con hash registrado en `docs/dataset-catalog.md`).
- Escalado: StandardScaler activado por defecto (stabiliza el entrenamiento, especialmente SVM). Justificación: centrado y varianza unitaria reducen sensibilidad a escala; para RF no es crítico pero no perjudica.
- Split: 80/20 estratificado, semilla 42. Justificación: equilibrio entre tamaño de entrenamiento y evaluación, y reproducibilidad.

## Modelos y configuración

- RandomForestClassifier:
  - n_estimators=100, random_state=42. Justificación: buen baseline robusto a outliers y ruido; 100 árboles balancea sesgo-varianza con costo computacional razonable.
- SVC:
  - kernel=rbf, C=1.0. Justificación: configuración clásica de referencia; RBF capta no linealidades; C=1.0 controla regularización estándar.

## Métricas

- Accuracy: proporción de aciertos; fácil de interpretar.
- F1-macro: promedio entre clases equitativo; relevante ante desbalance.
- Recursos: tiempo de entrenamiento (ms), CPU promedio (%), pico de memoria (MB) para evaluar eficiencia.

## Observabilidad y trazabilidad

- Eventos estructurados: START/RETRY/FAILURE/DONE con `agent`, `action`, `details` y `why` (causa/justificación).
- Línea de tiempo: `timeline.png` superpone CPU/mem con marcas de eventos e incidentes.
- Reporte HTML: tabla por etapa con métricas y "porqués"; glosario y sección de incidentes.

## Control de entorno

- Script `scripts/run_experiment.ps1`:
  - Health-check, logs de servidor, timeout ampliado.
  - Flags: `-Quiesce`, `-HighPriority`, `-AffinityMask`, `-Monitored`, `-MonitorSeconds`, `-Report`, `-ApiHost`, `-ApiPort`.
  - Scripts de quiesce/restore para reducir interferencias (plan de energía, servicios, OneDrive).

## Reproducibilidad

- Versionado de dependencias en `requirements.txt`.
- Semillas fijadas (42) y split estratificado.
- Dataset congelado y con SHA-256 registrado.
- Resultados por `ExperimentId` en `data/results/<exp>/`.

## Validez y amenazas

- Validez interna: control del entorno y semillas; logging detallado; manejo de incidentes con retries.
- Validez externa: dataset sintético limita generalización; mitigar incluyendo datasets reales en fases futuras.
- Constructo: métricas (accuracy, F1) adecuadas para clasificación balanceada; considerar ROC-AUC y tiempos de inferencia en futuros trabajos.

## Energía y sostenibilidad (nota)

- Se registra `mem_peak_mb` y `cpu_avg` durante entrenamiento. Estimar energía/j se dejará como trabajo futuro sujeto a disponibilidad de medición o modelos de potencia del sistema.

## Próximos pasos metodológicos

- Incorporar validación cruzada y búsqueda de hiperparámetros con seeds controlados.
- Añadir datasets reales y escenarios de ruido.
- Medir inferencia y latencias end-to-end.
