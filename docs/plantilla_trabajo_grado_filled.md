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
---

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

# Dedicatoria (opcional)

> A mi familia, por su apoyo incondicional durante todo el proceso.

<!-- pagebreak -->

# Agradecimientos (opcional)

A la Universidad Nacional de Colombia – Sede Manizales, al Departamento de Informática y Computación, y al grupo GAIA por el acompañamiento académico y técnico. Al profesor {{ advisor_name }} por su dirección y valiosas sugerencias.

<!-- pagebreak -->

# Resumen y Abstract

## Resumen (en español)

**Título en español:** {{ title }}

La rápida expansión de los datos y las exigencias de procesamiento han evidenciado las limitaciones de arquitecturas centralizadas para analítica y Machine Learning (ML). Este trabajo diseña e implementa un prototipo de arquitectura basada en Sistemas Multiagente (SMA), soportada en JADE, para orquestar y evaluar el entrenamiento de algoritmos de clasificación supervisada (Random Forest y Support Vector Machine), con énfasis en eficiencia computacional y sostenibilidad energética. Se comparan dos condiciones experimentales: arquitectura centralizada (control) y arquitectura SMA (tratamiento), en escenarios simulados, controlados y replicables. Las métricas cuantitativas incluyen: tiempo de ejecución (ms), rendimiento (registros/s), uso promedio de CPU (%), memoria pico (MB) y consumo energético estimado (J/MB). La recolección y agregación de resultados se automatiza con scripts Python; el monitoreo y visualización se instrumenta con Prometheus y Grafana. El análisis estadístico (pruebas de permutación y contraste inferencial) sugiere, con la configuración actual, ausencia de diferencias significativas (p ≥ 0.05) entre control y tratamiento; sin embargo, la plataforma demuestra viabilidad para estudios rigurosos, reproducibles y extensibles, aportando evidencia y herramientas para evaluar eficiencia, resiliencia y sostenibilidad en ML distribuido. Se discuten implicaciones técnicas, éticas y operativas, y se proponen líneas de trabajo futuro.

**Palabras clave:** Sistemas Multiagente, JADE, Machine Learning, Eficiencia Computacional, Sostenibilidad Energética, Random Forest, SVM.

## Abstract (in English)

**Title in English:** Computational Efficiency and Energy Sustainability of Supervised ML Classification Algorithms: A Multi‑Agent Approach

The rapid growth of data and processing demands has exposed the limitations of centralized architectures for Analytics and Machine Learning (ML). This work designs and implements a Multi‑Agent System (MAS) prototype—based on JADE—to orchestrate and evaluate the training of supervised classification algorithms (Random Forest and Support Vector Machine), focusing on computational efficiency and energy sustainability. Two experimental conditions are compared: centralized architecture (control) and MAS‑based architecture (treatment), under simulated, controlled, and replicable settings. Quantitative metrics include execution time (ms), throughput (records/s), average CPU usage (%), peak memory (MB), and estimated energy consumption (J/MB). Result collection and aggregation are automated with Python scripts; monitoring and visualization are instrumented with Prometheus and Grafana. Statistical analysis (permutation tests and inferential comparisons) suggests, with the current configuration, no significant differences (p ≥ 0.05) between control and treatment; however, the platform proves viable for rigorous, reproducible, and extensible studies, providing evidence and tools to assess efficiency, resilience, and sustainability in distributed ML. Technical, ethical, and operational implications are discussed, along with future work.

**Keywords:** Multi‑Agent Systems, JADE, Machine Learning, Computational Efficiency, Energy Sustainability, Random Forest, SVM.

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
| 2 | Flujo experimental orquestado | [ ] |
| 3 | Distribución time_ms TRAIN_RF | [ ] |
| 4 | Distribución time_ms TRAIN_SVM | [ ] |
| 5 | Energía/MB TRAIN_RF | [ ] |
| 6 | Energía/MB TRAIN_SVM | [ ] |
| 7 | Accuracy RF | [ ] |
| 8 | Accuracy SVM | [ ] |

# Lista de tablas

| Nº | Título | Página |
|---:|--------|:-----:|
| 1 | Definición de métricas de eficiencia y energía | [ ] |
| 2 | Variables experimentales y clasificación | [ ] |
| 3 | Resumen descriptivo entrenamiento RF y SVM | [ ] |
| 4 | p-values pruebas de permutación | [ ] |
| 5 | Tamaños de efecto (Cliff's δ) | [ ] |
| 6 | Mapeo objetivos → evidencia | [ ] |

# Lista de símbolos y abreviaturas

## Fórmulas y símbolos (latinos)

| Símbolo | Definición | Fórmula / Descripción | Unidad |
|:-------:|------------|-----------------------|:------:|
| t_ms | Tiempo de etapa | Tiempo medido de ejecución | ms |
| t_s | Tiempo en segundos | t_ms / 1000 | s |
| n_train | Registros de entrenamiento | Tamaño subset entrenamiento | reg |
| MB_proc | Datos procesados | Memoria estimada X_train + y_train | MB |
| P_avg | Potencia promedio CPU | Medida (RAPL) o TDP * (cpu_avg/100) | W |
| E_total | Energía total | P_avg * t_s | J |
| E_MB | Energía por MB | E_total / MB_proc | J/MB |
| rec_s | Registros por segundo | n_train / t_s | reg/s |
| MB_s | MB por segundo | MB_proc / t_s | MB/s |
| eff_cpu | Eficiencia CPU | rec_s / cpu_avg | reg·s⁻¹·%CPU⁻¹ |
| eff_mem | Eficiencia memoria | rec_s / mem_peak_mb | reg·s⁻¹·MB⁻¹ |
| E_rec | Energía por registro | E_total / n_train | J/reg |

## Abreviaturas

| Abreviatura | Término |
|:-----------:|---------|
| SMA | Sistema Multiagente |
| MAS | Multi-Agent System (inglés) |
| ML | Machine Learning |
| RF | Random Forest |
| SVM | Support Vector Machine |
| CPU | Central Processing Unit |
| RAM | Random Access Memory |
| TDP | Thermal Design Power |
| API | Application Programming Interface |
| ACL | Agent Communication Language |
| RAPL | Running Average Power Limit |
| CI/CD | Continuous Integration / Continuous Delivery |
| MB | Megabytes |
| J | Joules |
| W | Watts |

<!-- pagebreak -->

# Introducción

El crecimiento exponencial de datos en sensores y plataformas digitales exige arquitecturas capaces de escalar, adaptarse y ser resilientes. Los Sistemas Multiagente (SMA) ofrecen autonomía, comunicación y proactividad, adecuándose a entornos dinámicos y distribuidos. Este trabajo propone una plataforma SMA experimental, modular y replicable para evaluar algoritmos de ML supervisado (RF y SVM) con un enfoque integral en eficiencia computacional y sostenibilidad energética. Además de precisión, se consideran métricas como tiempo, throughput, uso de CPU y memoria, y energía (J/MB), con análisis estadístico para contrastar un grupo de control centralizado frente a un tratamiento SMA. La propuesta aborda un vacío identificado en la literatura: la falta de marcos integrales que combinen eficiencia, adaptabilidad y sostenibilidad en evaluaciones controladas de ML distribuido.

<!-- pagebreak -->

# 1. Presentación del trabajo de grado

## 1.1 Planteamiento del problema o situación abordada

Las soluciones centralizadas para ML presentan límites de escalabilidad, tolerancia a fallos y adaptabilidad bajo cargas crecientes y heterogéneas. Se requiere evaluar arquitecturas alternativas, como los SMA, que permitan comparar eficiencia y sostenibilidad energética en condiciones controladas y replicables, con trazabilidad end‑to‑end y capacidad de extensión modular.

## 1.2 Objetivo general

Diseñar e implementar un prototipo de arquitectura basada en Sistemas Multiagente (SMA) para evaluar la eficiencia computacional y la sostenibilidad energética durante el entrenamiento de algoritmos de Machine Learning supervisado de clasificación, en entornos simulados de analítica de datos.

## 1.3 Objetivos específicos

1. Modelar la arquitectura de un SMA que orqueste ingesta, preprocesamiento y preparación de datos para entrenamiento.  
2. Implementar el prototipo SMA integrando al menos RF y SVM en la fase de entrenamiento, utilizando JADE.  
3. Evaluar eficiencia computacional y sostenibilidad energética frente a una arquitectura centralizada, midiendo tiempo, throughput, CPU, memoria y energía (J/MB).  
4. Analizar e interpretar resultados cuantitativos para validar eficiencia y sostenibilidad, identificando implicaciones técnicas, éticas y operativas.

## 1.4 Metodología

**Enfoque:** cuantitativo principal con complemento cualitativo (reflexión ética y sostenibilidad).  
**Diseño experimental:** comparación control (centralizado) vs tratamiento (SMA) con repeticiones ≥ 10 por escenario.  
**Variables dependientes:** tiempo (ms), throughput (reg/s), cpu_avg (%), mem_peak_mb (MB), energía estimada (J/MB), métricas de desempeño (accuracy, f1).  
**Adaptabilidad y resiliencia:** métricas de fallos recuperados, tasa de reconfiguración, tiempo medio de recuperación (futuro: instrumentación ampliada).  
**Escalabilidad:** evaluación proyectada incrementando volumen y complejidad (trabajo futuro).  
**Instrumentación:** FastAPI (servicios), JADE (orquestación), Prometheus/Grafana (telemetría), scripts Python (simulación, agregación, análisis estadístico).  
**Análisis estadístico:** pruebas de permutación (N ≥ 5000) y tamaños de efecto (Cliff's δ, Cohen's d CI).  
**Ética y sostenibilidad:** registro de artefactos, transparencia metodológica, discusión de control humano significativo, impacto energético.  
**Reproducibilidad:** dataset sintético congelado, semillas fijas, toolchain documentado (Java 21, JADE 4.6.0, Python libs).  

### 1.4.1 Dataset y control experimental

- Fuente: `data/raw/synthetic_classification.csv` (generador controlado).  
- Metadatos: `synthetic_classification.meta.json` y catálogo en `docs/dataset-catalog.md`.  
- División reproducible train/test; semillas documentadas en `meta.json` por experimento.  

### 1.4.2 Cálculo de métricas energéticas

1. `t_s = time_ms / 1000`  
2. `P_avg ≈ CPU_POWER_W * (cpu_avg / 100)` (proxy; alternativa futura: lectura RAPL)  
3. `E_total = P_avg * t_s`  
4. `E_MB = E_total / MB_proc`  
5. Derivadas: `rec_s`, `MB_s`, `eff_cpu`, `eff_mem`, `E_rec`.

## 1.5 Ejemplo de presentación y citación de figuras, tablas y cuadros

Las figuras se mencionan en el texto y se ubican en la misma página o la siguiente. Las tablas llevan título en la parte superior y numeración consecutiva. Ejemplo: *Figura 3 muestra la distribución de tiempos de entrenamiento para Random Forest en ambos grupos.*

<!-- pagebreak -->

# 2. Revisión de literatura

La literatura reporta aplicaciones de SMA en analítica distribuida y dominios complejos (Braubach & Pokahr, 2019; Kuzin et al., 2022; Paik, 2024) y estudios sobre eficiencia energética de algoritmos ML (Yu et al., 2022; Rodríguez et al., 2024; Chung et al., 2025). Persisten vacíos en: (i) integración sistemática de métricas de eficiencia, resiliencia y sostenibilidad en una sola plataforma experimental, (ii) comparaciones reproducibles multi‑algoritmo con instrumentación homogénea, (iii) incorporación explícita de consideraciones éticas (control humano, transparencia, impacto ambiental) junto a métricas técnico‑energéticas. Este trabajo aporta una infraestructura modular que responde a esos vacíos y sienta bases para escalamiento y extensión.

<!-- pagebreak -->

# 3. Desarrollo

## 3.1 Arquitectura técnica

La arquitectura separa orquestación (JADE) de servicios de cómputo e instrumentación (FastAPI), apoyada por una capa de datos y telemetría.

- **Agentes JADE:** Orchestrator, Ingest/Prep, Trainer, Evaluator, Metrics/Monitor. Comunicación ACL y mensajes JSON; estados por experimento.  
- **API FastAPI:** Endpoints `/preprocess`, `/train`, `/evaluate`, `/metrics` (Prometheus).  
- **Telemetría:** Prometheus (scraping programado), Grafana (paneles temáticos: desempeño, eficiencia, energía, resiliencia).  
- **Persistencia:** Estructura jerárquica en `data/results/<experimentId>/` (prep, models, eval, logs, monitor, report).  
- **Automatización:** Scripts (`run_experiment.*`, `run_batch.*`, `aggregate_metrics.py`, `stats_analysis.py`) y generación de índices documentales diarios.  
- **Proxy energético:** Derivado de TDP y uso CPU; extensible a medición directa.  

## 3.2 Flujo experimental

1. Configuración (grupo, semilla, dataset).  
2. Preprocesamiento (split, escalado, persistencia).  
3. Entrenamiento (RF/SVM) – captura de métricas base.  
4. Evaluación (accuracy, f1).  
5. Agregación y exportación (CSV, reportes HTML, figuras).  
6. Análisis estadístico (permutaciones, efectos).  
7. Visualización continua (Grafana).  
8. Empaquetado de evidencia y actualización de índices.  

## 3.3 Estrategia de medición y energía

Métricas recogidas en tiempo real y posteriormente derivadas para indicadores de eficiencia y sostenibilidad. Limitaciones: el proxy puede infra‑representar variaciones finas de energía; justifica integración de RAPL/powercap.

## 3.4 Resultados (síntesis)

Escenario batch (10 repeticiones por grupo) no evidenció diferencias significativas (p ≥ 0.05) en `time_ms`, `records_per_s`, `energy_j_per_mb` para RF y SVM. Algunos tamaños de efecto no triviales obligan a escalados mayores para confirmar tendencias. La plataforma cumple su rol de soporte comparativo y de generación de evidencia trazable.

## 3.5 Alineación técnica con objetivos

Ver Tabla 6 (mapeo) y Anexo A (detalle). Todos los objetivos específicos se encuentran marcados como cumplidos en la verificación automática (Macroproceso.txt).

<!-- pagebreak -->

# 4. Conclusiones y recomendaciones

## 4.1 Conclusiones

- La arquitectura SMA es funcional, reproducible y extensible para experimentos de eficiencia y sostenibilidad en ML supervisado.  
- Con la carga y dataset actual no se observan diferencias significativas entre control y SMA.  
- El principal aporte inmediato es metodológico: infraestructura unificada para instrumentación y análisis reproducible.  
- La aproximación energética proxy es suficiente para comparaciones iniciales, pero debe evolucionar a medición directa.  

## 4.2 Recomendaciones

1. Integrar medición energética directa (RAPL/powercap).  
2. Escalar datasets, concurrencia y complejidad del pipeline (más etapas, más modelos).  
3. Incorporar fallos inducidos para evaluar resiliencia, elasticidad y recuperación.  
4. Ampliar análisis estadístico (bayesiano, potencia estadística, intervalos bootstrap).  
5. Documentar exhaustivamente parámetros de hardware y versión de dependencias en cada batch.  

<!-- pagebreak -->

## 4.3 Trabajo Futuro y Hoja de Ruta

Se propone una hoja de ruta incremental de 12 meses para evolucionar la plataforma desde prototipo experimental hacia un marco robusto de evaluación multi‑dimensional (eficiencia, energía, resiliencia, escalabilidad y calidad ética):

| Fase | Horizonte | Objetivos Clave | Entregables | Métricas / KPI | Riesgos / Mitigación |
|:----:|-----------|-----------------|-------------|----------------|----------------------|
| 1 | 0–3 meses | Medición energética directa; validación proxy vs RAPL; refactor agregación | Integración RAPL/powercap; script calibración; informe comparación | Δ error proxy (<15%); cobertura >90% experimentos con energía real | Falta permisos kernel → usar contenedores privilegiados controlados |
| 2 | 3–6 meses | Escalabilidad dataset y concurrencia; nuevos modelos (XGBoost, LightGBM) | Generador datasets grandes; pipelines paralelos; benchmarks multi‑modelo | Throughput ↑ ≥50%; Latencia estable (<10% var) | Cuellos de botella E/S → profiling y caching intermedio |
| 3 | 6–9 meses | Resiliencia y tolerancia a fallos; autoscaling de agentes | Inyección de fallos; métricas MTTR, tasa recuperación; módulo auto‑reconfiguración | MTTR < 5s; Recuperación ≥95% tareas | Fallos no controlados → sandbox + límites de recursos |
| 4 | 9–12 meses | Analítica avanzada y ética; difusión científica | Paneles Grafana completos; análisis bayesiano; paper conferencia; guía ética | Paper aceptado; Panel energía (5+ visualizaciones) | Retrasos publicación → preparar preprint arXiv |

### Prioridades Transversales

- Observabilidad refinada (trazabilidad por experimento y etapa).  
- Gestión de configuraciones reproducibles (infra como código + contenedores inmutables).  
- Automatización CI/CD: validación estadística mínima y actualización de figuras en cada release.  
- Documentación viva (actualización automática índices y changelog experimental).  

### Indicadores Estratégicos

| Dimensión | Indicador | Línea Base | Meta 12m |
|-----------|-----------|-----------|----------|
| Energía | Error proxy vs medición real | ~30% estimado | <10% |
| Eficiencia | Registros/s tratamiento vs control | Paridad | >1.2x |
| Resiliencia | MTTR agente crítico | N/D | <5s |
| Escalabilidad | Tamaño dataset máximo | 50k | >500k |
| Reproducibilidad | Script único end‑to‑end | Parcial | Completo |
| Difusión | Publicaciones / preprints | 0 | ≥2 |

### Dependencias Clave

- Acceso estable a hardware para medición energética.  
- Recursos de cómputo para pruebas de gran escala (CPU y memoria).  
- Colaboración con grupo de investigación para revisión ética y validación metodológica.  

### Impacto Esperado

La hoja de ruta consolidará evidencia rigurosa sobre compromisos y sinergias entre eficiencia y sostenibilidad en arquitecturas distribuidas basadas en SMA. Permitirá, además, posicionar la plataforma como referencia académica y aplicable a dominios donde la optimización energética es crítica.

<!-- pagebreak -->

# Anexos

## Anexo A. Mapeo de artefactos a objetivos y actividades

| Objetivo / Actividad | Descripción | Evidencia principal | Estado |
|----------------------|-------------|---------------------|:------:|
| Obj. General | Arquitectura SMA + evaluación eficiencia/energía | Código JADE (`agents/jade-platform`), API FastAPI (`backend/api/main.py`), métricas agregadas | Cumplido |
| Obj. Esp. 1 | Modelado arquitectura SMA | `docs/architecture.md`, agentes JADE, `message-protocol.md` | Cumplido |
| Obj. Esp. 2 | Implementación RF y SVM en prototipo | Entrenamiento en API, scripts `run_experiment.*` | Cumplido |
| Obj. Esp. 3 | Evaluación eficiencia y sostenibilidad | `aggregate_metrics.csv`, figuras en `figures/`, `stats_summary.*` | Cumplido |
| Obj. Esp. 4 | Análisis e interpretación | `thesis_results_section.md`, `conclusions_implications_future_work.md` | Cumplido |
| Act. 1 | Revisión literatura | `docs/experiments.md`, referencias, sección 2 | Completa |
| Act. 2 | Diseño arquitectura/experimento | `architecture.md`, `experiment-design.md` | Completa |
| Act. 3 | Implementación prototipos | Código agentes + API + scripts | Completa |
| Act. 4 | Recolección / preprocesamiento | Dataset sintético + pipelines | Completa |
| Act. 5 | Análisis datos | `stats_analysis.py`, `stats_summary.*` | Completa |
| Act. 6 | Visualización hallazgos | Figuras, paneles Grafana | Completa |
| Act. 7 | Redacción resultados | `thesis_results_section.md` | Completa |
| Act. 8 | Conclusiones e implicaciones | `conclusions_implications_future_work.md` | Completa |

## Anexo B. Evidencia generada (verificación 2025-11-11)

- Agregado de métricas: `data/results/aggregate_metrics.csv`  
- Resumen estadístico: `data/results/stats_summary.json` y `.md`  
- Paquete de evidencia: `data/results/evidence_batch_20251027_145840.zip`  
- Figuras por batch: `data/results/batch_20251027_145840/figures/`  
- Reportes HTML por experimento: `data/results/batch_20251027_145840_*/report/report.html`  
- Sección de resultados: `docs/thesis_results_section.{md,tex}`  
- Conclusiones e implicaciones: `docs/conclusions_implications_future_work.md`  

## Anexo C. Procedimiento reproducible resumido

1. Preparar entorno Python (`requirements.txt`).  
2. Opcional: exportar `CPU_POWER_W` para proxy energético.  
3. Ejecutar lote: tarea VS Code “Experiments: Run batch (bash)” o `scripts/run_batch.sh`.  
4. Agregar métricas: `python-analysis/aggregate_metrics.py`.  
5. Análisis estadístico: `python-analysis/stats_analysis.py`.  
6. Consultar reportes y figuras en `data/results/`.  
7. Generar índices diarios de documentación (tareas Docs).  

<!-- pagebreak -->

# Bibliografía

(Estilo aproximado APA — ajustar a norma institucional final.)

Braubach, L., & Pokahr, A. (2019). ActoDatA: A multi-agent architecture for data analytics. *Multiagent and Grid Systems, 15*(3), 199–220.

Chung, J.-W., Liu, J., Ma, J. J., Wu, R., Kweon, O. J., Xia, Y., Wu, Z., & Chowdhury, M. (2025). *The ML.ENERGY Benchmark: Toward Automated Inference Energy Measurement and Optimization*. arXiv preprint.

Kuzin, A., Ivanov, D., & Petrova, M. (2022). Multi-agent systems for tender classification. *Journal of Intelligent Systems, 31*(2), 123–137.

Paik, H. (2024). Smart city infrastructure: A multi-agent perspective. *International Journal of Urban Computing, 12*(1), 45–59.

Rodríguez, C., Degioanni, L., Kameni, L., Vidal, R., & Neglia, G. (2024). *Evaluating the Energy Consumption of Machine Learning: Systematic Literature Review and Experiments*. e-print manuscript.

Yu, J. R., Chen, C. H., Huang, T. W., Lu, J. J., Chung, C. R., Lin, T. W., Wu, M. H., Tseng, Y. J., & Wang, H. Y. (2022). Energy efficiency of inference algorithms for clinical laboratory data sets: Green artificial intelligence study. *Journal of Medical Internet Research, 24*(1), e28036.

Wooldridge, M. (2009). *An Introduction to MultiAgent Systems* (2nd ed.). Wiley.

Patel, N., et al. (2023). Next generation of multi-agent driven smart city applications and research paradigms. *IEEE Access*.

De Grande, P., & Eguía, M. (2007). Modelos y teorías. Sistemas multiagente y mercado de trabajo. *8° Congreso Nacional de Estudios del Trabajo (ASET)*.

González Pérez, J. L., & Martínez Miranda, M. A. (2018). Uso de sistemas multiagentes para el aprendizaje automático. *Ciencia e Ingeniería, 19*(2), 239–247.

IBM. (s.f.). ¿Qué es un sistema multiagente? Recuperado de https://www.ibm.com

KPMG. (s.f.). La IA multiagente revoluciona las operaciones de negocio. *KPMG Tendencias*.

Red Hat. (2024). ¿Qué es la inteligencia artificial con agentes? Recuperado de https://www.redhat.com

Focalx. (s.f.). La IA en los Sistemas Multiagente. Recuperado de [sitio web].

IEBS Business School. (2024). Qué son los agentes de IA y los sistemas multiagente. Recuperado de [sitio web].

Wooldridge, M. (2009). *An Introduction to MultiAgent Systems*. Wiley.

(Depurar entradas duplicadas y normalizar URLs y fechas de acceso en versión final.)

---
**Notas finales:**  
- Este archivo consolida las secciones solicitadas de la plantilla institucional.  
- Los marcadores `{{ }}` pueden procesarse con Pandoc/templating o reemplazarse manualmente previo a la compilación PDF.  
- Ajustar numeración/paginación final tras generación automática de la tabla de contenido y listas de figuras/tablas.
