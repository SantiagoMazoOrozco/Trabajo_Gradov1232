# Sección de Resultados

> Archivo generado (borrador estructurado). Completar con valores finales, figuras y citas formales.  
> Fuente de datos primaria: `data/results/aggregate_metrics.csv` y artefactos en `data/results/batch_*/`.

## 1. Objetivo de la Sección
Presentar y analizar los resultados cuantitativos obtenidos al comparar la arquitectura centralizada (control) contra el Sistema Multiagente (treatment) durante el entrenamiento de algoritmos de clasificación supervisada (Random Forest y SVM), enfatizando eficiencia computacional y sostenibilidad (proxy energético), así como métricas de rendimiento de los modelos.

## 2. Configuración Experimental Resumida
- **Algoritmos evaluados:** Random Forest (RF), Support Vector Machine (SVM).
- **Escenarios:** control (arquitectura centralizada) vs treatment (SMA/JADE).
- **Repeticiones batch principal:** 10 por grupo (ver paquete `evidence_batch_YYYYMMDD_HHMMSS.zip`).
- **Scripts de ejecución:** `scripts/run_batch.*`, `scripts/run_experiment.*`.
- **Generación de métricas:** agregación con `python-analysis/aggregate_metrics.py` y análisis con `python-analysis/stats_analysis.py` (≥5000 permutaciones). 
- **Proxy energético:** `avg_watts` ≈ `CPU_POWER_W * (cpu_avg/100)` o lectura RAPL futura (pendiente integrar lectura directa si se habilita hardware).

## 3. Métricas y Definiciones
| Métrica | Descripción | Unidad | Fuente / Cálculo |
|---------|-------------|--------|------------------|
| `time_ms` | Tiempo total de etapa (prep / train / eval) | ms | Cronometría interna | 
| `cpu_avg` | Uso promedio de CPU durante la etapa | % | Monitor interno / psutil |
| `mem_peak_mb` | Pico de memoria residente | MB | psutil / tracking proceso |
| `records_per_s` | Registros procesados por segundo (entrenamiento) | reg/s | `n_train / time_s` |
| `data_mb_per_s` | MB procesados por segundo | MB/s | `MB_procesados / time_s` |
| `watts_per_mb` | Potencia normalizada por MB procesado | W/MB | `avg_watts / MB_procesados` |
| `energy_j_total` | Energía total (aprox.) | Joules | `avg_watts * time_s` |
| `accuracy`, `f1` | Métricas de desempeño del modelo | - | scikit-learn (set de validación) |

## 4. Resumen Descriptivo
Los siguientes descriptivos (medianas y medias) se calculan a partir del conjunto balanceado del batch 2025-10-27 (10 repeticiones por grupo):

### 4.1 Descriptivos (batch 20251027, medianas y medias)
| Stage | Group | time_ms (med/mean) | cpu_avg% (med/mean) | mem_peak_mb (med/mean) | records_per_s (med/mean) | watts_per_mb (med/mean) |
|---|---|---:|---:|---:|---:|---:|
| TRAIN_RF | control | 1781.030/1785.152 | 30.345/32.238 | 190.769/191.081 | 1348.189/1346.414 | 47.675/52.559 |
| TRAIN_RF | treatment | 1773.894/1769.241 | 30.640/32.163 | 193.727/193.864 | 1353.601/1357.479 | 50.305/51.785 |
| TRAIN_SVM | control | 203.090/203.252 | 27.000/31.025 | 190.769/191.231 | 11817.402/11808.020 | 4.992/5.738 |
| TRAIN_SVM | treatment | 203.642/203.600 | 27.125/29.025 | 193.790/193.877 | 11785.376/11787.840 | 5.029/5.375 |

## 5. Análisis Inferencial
- **Procedimiento:** permutación (N=5000) sobre la variable `group` para cada combinación (etapa, métrica). 
- **Hipótesis nula (H0):** No hay diferencia en la distribución de la métrica entre control y treatment.
- **Criterio:** p < 0.05 → rechazo de H0.

### 5.1 Resumen de p-values
Resultados de pruebas de permutación (N≈5000) entre grupos:

### 5.1.1 Resumen de p-values (permutación)
| Stage | Métrica | p-value | Interpretación |
|---|---|---:|---|
| TRAIN_RF | time_ms | 0.4788 | No significativo |
| TRAIN_SVM | time_ms | 0.5081 | No significativo |
| TRAIN_RF | records_per_s | 0.5766 | No significativo |
| TRAIN_SVM | records_per_s | 0.5044 | No significativo |
| TRAIN_RF | energy_j_per_mb | 0.4868 | No significativo |
| TRAIN_SVM | energy_j_per_mb | 0.8785 | No significativo |

### 5.2 Tamaños de Efecto (Opcional)
Se calcularon tamaños de efecto con Cliff's Delta (δ) en el batch balanceado. Interpretación (absoluto |δ|): pequeño ≈ 0.147, medio ≈ 0.33, grande ≈ 0.474.

| Stage | Métrica | Cliff's δ | Magnitud |
|---|---|---:|---|
| TRAIN_RF | time_ms | 0.24 | Medio |
| TRAIN_RF | energy_j_per_mb | -0.08 | Pequeño/Despreciable |
| TRAIN_RF | records_per_s | -0.24 | Medio |
| TRAIN_SVM | time_ms | -0.50 | Grande |
| TRAIN_SVM | energy_j_per_mb | -0.04 | Pequeño/Despreciable |
| TRAIN_SVM | records_per_s | 0.50 | Grande |

Nota: Aunque algunas métricas muestran |δ| en rangos medio/grande, los intervalos de confianza de Cohen's d (cohens_d_ci.csv) cruzan 0 de forma amplia en todos los casos, lo cual es consistente con los p-values de permutación no significativos (Sec. 5.1). Esto sugiere alta variabilidad y/o tamaño muestral limitado para efectos pequeños.

## 6. Interpretación de Hallazgos
- Observaciones generales sobre diferencias (o su ausencia) en tiempo, CPU, memoria y potencia normalizada.
- Comentario sobre robustez (número de permutaciones y consistencia de medianas).
- Discusión de por qué la arquitectura multiagente no muestra (o sí muestra) ventajas claras bajo la carga y dataset actual (hipótesis: overhead de coordinación, dataset demasiado pequeño para observar escalado, etc.).

## 7. Figura / Visualizaciones
Incorporar figuras desde `data/results/batch_*/figures/`:
- Distribución de `time_ms` por grupo y modelo.
- Boxplot de `watts_per_mb`.
- Barras de `records_per_s`.

(Referenciar cada figura: Figura 1, Figura 2, ... con descripción.)

Figuras disponibles en `data/results/batch_20251027_145840/figures/`:
- TRAIN_RF_time_ms.png (Figura 1)
- TRAIN_SVM_time_ms.png (Figura 2)
- TRAIN_RF_energy_j_per_mb.png (Figura 3)
- TRAIN_SVM_energy_j_per_mb.png (Figura 4)
- EVAL_RF_accuracy.png, EVAL_RF_f1.png (Figuras 5–6)
- EVAL_SVM_accuracy.png, EVAL_SVM_f1.png (Figuras 7–8)

Visualizaciones embebidas (ruta relativa desde este documento):

![Figura 1 — TRAIN_RF time_ms](../data/results/batch_20251027_145840/figures/TRAIN_RF_time_ms.png)
![Figura 2 — TRAIN_SVM time_ms](../data/results/batch_20251027_145840/figures/TRAIN_SVM_time_ms.png)
![Figura 3 — TRAIN_RF energía/MB](../data/results/batch_20251027_145840/figures/TRAIN_RF_energy_j_per_mb.png)
![Figura 4 — TRAIN_SVM energía/MB](../data/results/batch_20251027_145840/figures/TRAIN_SVM_energy_j_per_mb.png)

## 8. Discusión sobre Sostenibilidad
- Limitaciones del proxy energético (TDP vs medición real).
- Riesgo de sub/ sobreestimar energía con cargas pequeñas.
- Plan para integrar lectura directa (RAPL / powercap) en trabajo futuro.

## 9. Alineación con Objetivos Específicos
| Objetivo | Evidencia en esta sección | Estado |
|----------|---------------------------|--------|
| OE2 (Implementación SMA + RF/SVM) | Artefactos de entrenamiento y métricas RF/SVM | Cumplido |
| OE3 (Evaluar eficiencia y sostenibilidad) | Métricas tiempo, CPU, memoria, watts_per_mb, energy_j_total | Cumplido |
| OE4 (Analizar e interpretar) | Secciones 5–8 | En progreso (completar redacción final) |

## 10. Amenazas a la Validez
| Tipo | Riesgo | Mitigación |
|------|--------|------------|
| Interna | Variabilidad de carga de SO | Repeticiones balanceadas, permutaciones | 
| Constructo | Proxy energético aproximado | Documentado, futura integración RAPL |
| Externa | Dataset sintético limitado | Extender a datasets reales multivariados |
| Conclusión | p-values no significativos con n=10 | Aumentar repeticiones / tamaños de dataset |

## 11. Resumen Ejecutivo
En el escenario evaluado (dataset sintético, 10 repeticiones por grupo), no se observaron diferencias estadísticamente significativas entre la arquitectura centralizada y el SMA para las métricas principales de entrenamiento (tiempo, registros/segundo y potencia normalizada por MB) en RF y SVM (p ≥ 0.05 en todas). Si bien algunos tamaños de efecto (Cliff's δ) alcanzan magnitudes medias o grandes en time_ms y records_per_s, los intervalos de confianza de Cohen's d abarcan 0 y corroboran la ausencia de evidencia concluyente. La interpretación más probable es que el beneficio del SMA no emerge bajo esta carga; para revelarlo sería necesario escalar volumen de datos, concurrencia y/o complejidad del pipeline, además de incorporar medición energética directa (RAPL/powercap) para reducir la incertidumbre del proxy.

---
Nota para integración LaTeX: las tablas generadas automáticamente están disponibles en `docs/_auto_results_tables.tex` y pueden incluirse en el documento principal con `\input{docs/_auto_results_tables.tex}`.

---
_Última actualización (auto): YYYY-MM-DD. Completar y luego enlazar desde el documento principal de tesis._

## Referencias cruzadas
- Metodología (cómo fue, por qué y para qué): `docs/achievements/metodologia.md`
- Cumplimiento del cronograma (cómo y por qué se lograron las actividades): `docs/achievements/cumplimiento_cronograma.md`
- Resultados esperados y aporte específico: `docs/achievements/resultados_aporte.md`
- Lista de reproducibilidad: `docs/appendix/reproducibility_checklist.md`
