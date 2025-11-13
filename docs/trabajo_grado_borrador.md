---
title: "Eficiencia y Sostenibilidad Computacional de Algoritmos de Machine Learning para la Clasificación Supervisada en Analítica de Datos: Un Enfoque Multiagente"
author: "Santiago Mazo Orozco"
university: "Universidad Nacional de Colombia"
faculty: "Facultad de Administración, Departamento de Informática y Computación"
city: "Manizales, Colombia"
year: "2025"
degree_target: "Administrador(a) de Sistemas Informáticos"
advisor_title: "Profesor"
advisor_name: "Néstor Darío Duque M"
modality: "Trabajos investigativos – Proyecto Final"
research_group: "GAIA – Grupo de Investigación en Ambientes Inteligentes Adaptativos (en alianza con ACSIC, Universidad de Islas Baleares)"
program: "Administración de Sistemas Informáticos"

# Cubierta (Carátula)

## {{ title }}

{{ author }}

{{ university }}  
{{ faculty }}  
{{ city }}  
{{ year }}

<!-- pagebreak -->

# Portada

## {{ title }}

{{ author }}

Trabajo de grado presentado como requisito parcial para optar al título de:  
**{{ degree_target }}**

Director(a):  
{{ advisor_title }} {{ advisor_name }}

Modalidad del trabajo de grado:  
{{ modality }}

Programa Curricular:  
{{ program }}

Grupo de Investigación:  
{{ research_group }}

{{ university }}  
{{ faculty }}  
{{ city }}  
{{ year }}

<!-- pagebreak -->

# Dedicatoria [opcional]

> A mi familia, por su apoyo incondicional durante todo el proceso.

<!-- pagebreak -->

# Agradecimientos [opcional]

A la Universidad Nacional de Colombia – Sede Manizales, al Departamento de Informática y Computación, y al grupo GAIA por el acompañamiento académico y técnico. Al profesor {{ advisor_name }} por su dirección y valiosas sugerencias.

<!-- pagebreak -->

# Resumen y Abstract

## Resumen (en español)

La rápida expansión de los datos y las exigencias de procesamiento han evidenciado las limitaciones de arquitecturas centralizadas para analítica y Machine Learning (ML). Este trabajo diseña e implementa un prototipo de arquitectura basada en Sistemas Multiagente (SMA), soportada en JADE, para orquestar y evaluar el entrenamiento de algoritmos de clasificación supervisada (Random Forest y Support Vector Machine), con énfasis en eficiencia computacional y sostenibilidad energética. Se comparan dos condiciones experimentales: arquitectura centralizada (control) y arquitectura SMA (tratamiento), en escenarios simulados, controlados y replicables. Las métricas cuantitativas incluyen: tiempo de ejecución (ms), rendimiento (registros/s), uso promedio de CPU (%), memoria pico (MB) y consumo energético estimado (J/MB). La recolección y agregación de resultados se automatiza con scripts Python; el monitoreo y visualización se instrumenta con Prometheus y Grafana. El análisis estadístico (pruebas de permutación y contraste inferencial) sugiere, con la configuración actual, ausencia de diferencias significativas (p ≥ 0.05) entre control y tratamiento; sin embargo, la plataforma demuestra viabilidad para estudios rigurosos, reproducibles y extensibles, aportando evidencia y herramientas para evaluar eficiencia, resiliencia y sostenibilidad en ML distribuido. Se discuten implicaciones técnicas, éticas y operativas, y se proponen líneas de trabajo futuro.

Palabras clave: Sistemas Multiagente, JADE, Machine Learning, Eficiencia Computacional, Sostenibilidad Energética, Random Forest, SVM.

## Abstract (in English)

The rapid growth of data and processing demands has exposed the limitations of centralized architectures for Analytics and Machine Learning (ML). This work designs and implements a Multi‑Agent System (MAS) prototype—based on JADE—to orchestrate and evaluate the training of supervised classification algorithms (Random Forest and Support Vector Machine), focusing on computational efficiency and energy sustainability. Two experimental conditions are compared: centralized architecture (control) and MAS‑based architecture (treatment), under simulated, controlled, and replicable settings. Quantitative metrics include execution time (ms), throughput (records/s), average CPU usage (%), peak memory (MB), and estimated energy consumption (J/MB). Result collection and aggregation are automated with Python scripts; monitoring and visualization are instrumented with Prometheus and Grafana. Statistical analysis (permutation tests and inferential comparisons) suggests, with the current configuration, no significant differences (p ≥ 0.05) between control and treatment; however, the platform proves viable for rigorous, reproducible, and extensible studies, providing evidence and tools to assess efficiency, resilience, and sustainability in distributed ML. Technical, ethical, and operational implications are discussed, along with future work.

Keywords: Multi‑Agent Systems, JADE, Machine Learning, Computational Efficiency, Energy Sustainability, Random Forest, SVM.

<!-- pagebreak -->

# Contenido

- Resumen … vii  
- Lista de figuras … x  
- Lista de tablas … xi  
- Lista de símbolos y abreviaturas … xii  
- Introducción … 1  
- 1. Presentación del trabajo de grado … 3  
  - 1.1 Planteamiento del problema o situación abordada … 3  
  - 1.2 Objetivo general … 3  
  - 1.3 Objetivos específicos … 4  
  - 1.4 Metodología … 4  
  - 1.5 Ejemplo de presentación y citación de figuras, tablas y cuadros … 4  
- 2. Revisión de literatura … 7  
- 3. Desarrollo … 9  
- 4. Conclusiones y recomendaciones … 11  
  - 4.1 Conclusiones … 11  
  - 4.2 Recomendaciones … 11  
- A. Anexos … 13  
- Bibliografía … 15

<!-- pagebreak -->

# Lista de figuras

| Nº | Título | Página |
|---:|--------|:-----:|
| 1 | Arquitectura de la plataforma SMA | [ ] |

# Lista de tablas

| Nº | Título | Página |
|---:|--------|:-----:|
| 1 | Métricas cuantitativas y descripción | [ ] |

# Lista de símbolos y abreviaturas [opcional]

| Abreviatura | Término |
|:-----------:|---------|
| SMA | Sistema Multiagente |
| ML | Machine Learning |
| RF | Random Forest |
| SVM | Support Vector Machine |

<!-- pagebreak -->

# Introducción

El crecimiento exponencial de datos en sensores y plataformas digitales exige arquitecturas capaces de escalar, adaptarse y ser resilientes. Los Sistemas Multiagente (SMA) ofrecen autonomía, comunicación y proactividad, adecuándose a entornos dinámicos y distribuidos. Este trabajo propone una plataforma SMA experimental, modular y replicable para evaluar algoritmos de ML supervisado (RF y SVM) con un enfoque integral en eficiencia computacional y sostenibilidad energética. Además de precisión, se consideran métricas como tiempo, throughput, uso de CPU y memoria, y energía (J/MB), con análisis estadístico para contrastar un grupo de control centralizado frente a un tratamiento SMA.

<!-- pagebreak -->

# 1. Presentación del trabajo de grado

## 1.1 Planteamiento del problema o situación abordada

Las soluciones centralizadas para ML presentan límites de escalabilidad y tolerancia a fallos. Se requiere evaluar arquitecturas alternativas, como los SMA, que permitan comparar eficiencia y sostenibilidad energética en condiciones controladas, con resultados confiables y replicables.

## 1.2 Objetivo general

Diseñar e implementar un prototipo de arquitectura basada en Sistemas Multiagente (SMA) para evaluar la eficiencia computacional y la sostenibilidad energética durante el entrenamiento de algoritmos de Machine Learning supervisado de clasificación, en entornos simulados de analítica de datos.

## 1.3 Objetivos específicos

1. Modelar la arquitectura de un SMA que orqueste ingesta, preprocesamiento y preparación de datos para entrenamiento.  
2. Implementar el prototipo SMA integrando al menos RF y SVM en la fase de entrenamiento, utilizando JADE.  
3. Evaluar eficiencia computacional y sostenibilidad energética frente a una arquitectura centralizada, midiendo tiempo, throughput, CPU, memoria y energía (J/MB).  
4. Analizar e interpretar resultados cuantitativos para validar eficiencia y sostenibilidad, identificando implicaciones técnicas, éticas y operativas.

## 1.4 Metodología

- Enfoque cuantitativo con complemento cualitativo.  
- Diseño experimental (o cuasi‑experimental) con dos condiciones: control (centralizado) vs tratamiento (SMA).  
- Variables dependientes: tiempo (ms), throughput (reg/s), CPU (%), memoria (MB), energía (J/MB).  
- Adaptabilidad y resiliencia: tiempo de respuesta ante eventos dinámicos, tasa de reconfiguración autónoma, fallos recuperados y tiempo medio de recuperación/eficiencia adaptativa.  
- Escalabilidad: mantenimiento de métricas ante incrementos de carga.  
- Instrumentación: scripts Python para orquestación y análisis; Prometheus+Grafana para monitoreo; backend FastAPI; agentes JADE para orquestación; dataset sintético controlado.  
- Repeticiones por escenario (≥ 10) para soporte inferencial; pruebas de permutación y contrastes (p‑value).  
- Consideraciones éticas y de sostenibilidad (impacto ambiental, control humano significativo, diseño ético por defecto).

### 1.4.1 Dataset y control experimental

- Dataset base: `synthetic_classification.csv` (sklearn.make_classification), 3000 filas, 21 columnas. Metadatos en `data/raw/synthetic_classification.meta.json` (catálogo en `docs/dataset-catalog.md`).  
- Control de variables: semillas fijas, dataset congelado, hardware registrado.  
- Registro estructurado de resultados en `data/results/` y agregado en `data/results/aggregate_metrics.csv`.

## 1.5 Ejemplo de presentación y citación de figuras, tablas y cuadros

Las figuras se mencionan en el texto y se ubican en la misma página o la siguiente. Las tablas llevan título en la parte superior y numeración consecutiva.

<!-- pagebreak -->

# 2. Revisión de literatura

Trabajos previos muestran aplicaciones de SMA en analítica de datos y ciudades inteligentes (Braubach & Pokahr, 2019; Paik, 2024; Kuzin et al., 2022), así como medición de eficiencia energética en ML (Rodríguez et al., 2024; Yu et al., 2022; Chung et al., 2025). Persiste un vacío en evaluaciones integrales que combinen eficiencia, adaptabilidad y sostenibilidad en un marco homogéneo; este trabajo apunta a cubrir ese vacío con una plataforma experimental replicable.

<!-- pagebreak -->

# 3. Desarrollo

## 3.1 Arquitectura técnica

La arquitectura integra una capa multiagente (JADE) y una capa de servicios ligeros (FastAPI) para desacoplar orquestación de instrumentación y persistencia:

- Capa Agentes (JADE): agentes especializados (Ingest/Prep, Trainer, Evaluator, Metrics/Monitor, Orchestrator) coordinan las fases del pipeline. Comunicación asíncrona (ACL) con mensajes estructurados en JSON (cuando aplica) y manejo de estados por experimento.  
- Capa API (FastAPI): expone endpoints REST (`/preprocess`, `/train`, `/evaluate`) y un endpoint `/metrics` Prometheus que sintetiza métricas agregadas y “last session” etiquetadas (por grupo y por algoritmo).  
- Telemetría y Observabilidad: Prometheus realiza scraping periódico (file_sd con `prom_targets.json` generado dinámicamente). Los paneles de Grafana se aprovisionan (JSON provisioning) y cubren: desempeño del modelo (accuracy, F1), eficiencia de entrenamiento (CPU, memoria, throughput, energía), resiliencia (fallos, recuperaciones, tasa), y comparaciones por algoritmo.  
- Persistencia de Resultados: cada experimento crea una jerarquía en `data/results/<experimentId>/` con subcarpetas (prep, models, eval, logs, monitor, report). Agregados globales: `aggregate_metrics.csv`, `stats_summary.json|md`.  
- Scripts de Automatización: `run_experiment.*` (unidad), `run_batch.*` (lotes control vs tratamiento), `aggregate_metrics.py`, `stats_analysis.py`, y generación de índices diarios `generate_daily_docs.ps1`.  
- Proxy Energético: cálculo estimado de energía a partir de potencia media CPU (configurable vía `CPU_POWER_W`), tiempo y uso de CPU, normalizada por MB procesados.

## 3.2 Flujo experimental

1. Preparación: selección de grupo (control vs treatment), semilla y dataset (congelado).  
2. Preprocesamiento: agentes/servicio transforman dataset (split train/test, escalado) y registran artefactos (prep ref).  
3. Entrenamiento: ejecución RF y/o SVM; recolección de tiempo, CPU promedio, memoria pico, throughput, MB procesados y energía estimada.  
4. Evaluación: cálculo de accuracy, F1 macro y (si configurado) matriz de confusión.  
5. Agregación: consolidación en CSV y actualización del endpoint `/metrics` con métricas “last” y contadores globales (experimentos totales, fallos, recuperaciones).  
6. Análisis estadístico: pruebas de permutación para diferencias entre grupos (p ≥ 0.05 en la configuración actual).  
7. Visualización: paneles Grafana y reportes HTML por experimento (figuras, tablas y métricas derivadas).  
8. Empaquetado de evidencia: compresión de artefactos y generación de índices de documentación por fecha.

## 3.3 Estrategia de medición y energía

- Métricas base: `time_ms`, `cpu_avg`, `mem_peak_mb`, `records_per_s`, `data_mb_per_s`, `energy_j_total`, `energy_j_per_mb`, `accuracy`, `f1`.  
- Derivadas de eficiencia: `efficiency_cpu_rps_per_pct`, `efficiency_mem_rps_per_mb`, `energy_j_per_record`.  
- Resiliencia: `failures_total`, `recoveries_total`, `recovery_rate` (a partir de filas RESILIENCE en agregados).  
- Etiquetado Prometheus: `{group="control|treatment"}`, `{algo="rf|svm"}` y métricas globales last-session.  
- Limitaciones: el proxy energético se basa en potencia media y no en medición directa (RAPL). Aun así, permite comparar escenarios relativos y evolucionar a mediciones hardware‑level futuras.  
- Reproducibilidad: semillas registradas en `meta.json`; dataset inmutable; versión de toolchain (Java 21, JADE 4.6.0) documentada.

## 3.4 Resultados

Objetivo: comparar control (arquitectura centralizada) vs tratamiento (SMA/JADE) para RF y SVM en entrenamiento, con foco en eficiencia y sostenibilidad (proxy energético) y desempeño del modelo.

Configuración resumida:
- Algoritmos: RF, SVM.  
- Repeticiones: 10 por grupo (batch 2025-10-27).  
- Scripts: `scripts/run_batch.*`, `scripts/run_experiment.*`.  
- Agregación/análisis: `python-analysis/aggregate_metrics.py`, `python-analysis/stats_analysis.py` (≥ 5000 permutaciones).  
- Proxy energético: `avg_watts ≈ CPU_POWER_W * (cpu_avg/100)` (lectura directa RAPL futura).

Métricas y definiciones principales: time_ms, cpu_avg, mem_peak_mb, records_per_s, data_mb_per_s, energy_j_total, energy_j_per_mb, accuracy, f1.

Descriptivos (batch 20251027; medianas/medias):

| Stage | Group | time_ms (med/mean) | cpu_avg% (med/mean) | mem_peak_mb (med/mean) | records_per_s (med/mean) | watts_per_mb (med/mean) |
|---|---|---:|---:|---:|---:|---:|
| TRAIN_RF | control | 1781.030/1785.152 | 30.345/32.238 | 190.769/191.081 | 1348.189/1346.414 | 47.675/52.559 |
| TRAIN_RF | treatment | 1773.894/1769.241 | 30.640/32.163 | 193.727/193.864 | 1353.601/1357.479 | 50.305/51.785 |
| TRAIN_SVM | control | 203.090/203.252 | 27.000/31.025 | 190.769/191.231 | 11817.402/11808.020 | 4.992/5.738 |
| TRAIN_SVM | treatment | 203.642/203.600 | 27.125/29.025 | 193.790/193.877 | 11785.376/11787.840 | 5.029/5.375 |

Inferencia (permutación, N≈5000; criterio p < 0.05):

| Stage | Métrica | p-value | Interpretación |
|---|---|---:|---|
| TRAIN_RF | time_ms | 0.4788 | No significativo |
| TRAIN_SVM | time_ms | 0.5081 | No significativo |
| TRAIN_RF | records_per_s | 0.5766 | No significativo |
| TRAIN_SVM | records_per_s | 0.5044 | No significativo |
| TRAIN_RF | energy_j_per_mb | 0.4868 | No significativo |
| TRAIN_SVM | energy_j_per_mb | 0.8785 | No significativo |

Figuras (batch 20251027):

![Figura 1 — TRAIN_RF time_ms](../data/results/batch_20251027_145840/figures/TRAIN_RF_time_ms.png)
![Figura 2 — TRAIN_SVM time_ms](../data/results/batch_20251027_145840/figures/TRAIN_SVM_time_ms.png)
![Figura 3 — TRAIN_RF energía/MB](../data/results/batch_20251027_145840/figures/TRAIN_RF_energy_j_per_mb.png)
![Figura 4 — TRAIN_SVM energía/MB](../data/results/batch_20251027_145840/figures/TRAIN_SVM_energy_j_per_mb.png)

Resumen: En el escenario evaluado (dataset sintético, 10 repeticiones por grupo), no se observaron diferencias estadísticamente significativas entre control y tratamiento para las métricas principales (p ≥ 0.05). Para evidenciar beneficios del SMA, se recomienda escalar la carga (datos/concurrencia), extender el pipeline y medir energía con RAPL/powercap.

<!-- pagebreak -->

# 4. Conclusiones y recomendaciones

## 4.1 Conclusiones

La plataforma SMA demuestra viabilidad técnica para orquestar y evaluar experimentos de ML con rigor y replicabilidad. En la configuración actual, no se observaron diferencias significativas (p ≥ 0.05) entre control y tratamiento, lo cual motiva ajustar cargas, escalas y condiciones para evaluar mejor escalabilidad y resiliencia. El aporte clave es metodológico y de instrumentación: una base reproducible para estudios comparativos de eficiencia y sostenibilidad.

## 4.2 Recomendaciones

- Incorporar medición energética directa (RAPL/powercap) para mayor fidelidad.  
- Aumentar tamaño muestral, cargas y escenarios de estrés.  
- Extender a otras tareas (inferencias, pipelines más largos) y más algoritmos.  
- Profundizar en resiliencia (fallos/recoveries reales) y escalabilidad.  
- Integrar análisis cualitativo de implicaciones éticas y regulatorias.

<!-- pagebreak -->

# Anexos

## Anexo A. Mapeo de artefactos a objetivos

- Backend/API, scripts de experimentación, agregación y análisis; datos y reportes en `data/results/`.  
- Paneles Grafana: calidad (accuracy/F1), eficiencia (CPU/Mem/Throughput/Energía), resiliencia, per‑algoritmo.

## Anexo B. Evidencia generada (verificación 2025-11-11)

- Agregado de métricas: `data/results/aggregate_metrics.csv`  
- Resumen estadístico: `data/results/stats_summary.json` y `data/results/stats_summary.md`  
- Paquete de evidencia: `data/results/evidence_batch_20251027_145840.zip`  
- Figuras por batch: `data/results/batch_20251027_145840/figures/`  
- Reportes HTML por experimento: `data/results/batch_20251027_145840_*/report/report.html`  
- Sección de resultados: `docs/thesis_results_section.{md,tex}`  
- Conclusiones e implicaciones: `docs/conclusions_implications_future_work.md`

<!-- pagebreak -->

# Bibliografía

Braubach, L., & Pokahr, A. (2019). ActoDatA: A multi-agent architecture for data analytics. Multiagent and Grid Systems, 15(3), 199–220.  
Chung, J.-W., et al. (2025). The ML.ENERGY Benchmark: Toward Automated Inference Energy Measurement and Optimization. arXiv (preprint).  
Kuzin, A., Ivanov, D., & Petrova, M. (2022). Multi-agent systems for tender classification. Journal of Intelligent Systems, 31(2), 123–137.  
Paik, H. (2024). Smart city infrastructure: A multi-agent perspective. International Journal of Urban Computing, 12(1), 45–59.  
Rodríguez, C., Degioanni, L., Kameni, L., Vidal, R., & Neglia, G. (2024). Evaluating the Energy Consumption of Machine Learning: Systematic Literature Review and Experiments. e-print.  
Yu, J. R., Chen, C. H., Huang, T. W., Lu, J. J., Chung, C. R., Lin, T. W., Wu, M. H., Tseng, Y. J., & Wang, H. Y. (2022). Energy Efficiency of Inference Algorithms for Clinical Laboratory Data Sets. Journal of Medical Internet Research, 24(1), e28036.  
Wooldridge, M. (2009). An Introduction to MultiAgent Systems. John Wiley & Sons.  
Patel, N., et al. (2023). Next Generation of Multi‑Agent Driven Smart City Applications and Research Paradigms. IEEE Access.  