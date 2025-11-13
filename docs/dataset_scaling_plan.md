# Plan de Escalamiento de Dataset

## 1. Objetivo
Aumentar el volumen y complejidad de los datos para revelar diferencias de eficiencia, escalabilidad y energía entre arquitectura centralizada y SMA.

## 2. Estrategia de Generación Sintética
| Tamaño | Filas | Columnas (features) | Clases | Observaciones |
|--------|-------|---------------------|--------|---------------|
| Base | 3,000 | 20 + label | 2 | Actual dataset |
| Medio | 30,000 | 50 + label | 2 / 4 | Evaluar saturación CPU memoria |
| Alto | 100,000 | 100 + label | 2 / 4 | Stress entrenamiento + memoria |
| Externo (opcional) | 250,000 | 150 + label | 2 / multi | Requiere supervisión (tiempo) |

### 2.1 Parámetros (scikit-learn `make_classification`)
- `n_informative`: 30% de features.
- `n_redundant`: 10%.
- `n_repeated`: 5%.
- `class_sep`: variar 1.0 (base), 0.8 (medio), 0.5 (alto) para dificultad.
- `weights`: balanceado primero; luego introducir desbalance 70/30.

### 2.2 Guardado
Ruta: `data/raw/` como `synthetic_classification_<size>.csv` con meta JSON: `synthetic_classification_<size>.meta.json`.

## 3. Dataset Real (Opcional)
| Fuente | Tipo | Requisitos |
|--------|------|-----------|
| UCI (ej. Credit Approval) | Tabular | Licencia abierta |
| Kaggle (ej. Telco Churn) | Tabular | Términos de uso; anonimizar si es necesario |
| Interno académico | Log eventos | Autorizar y documentar ética |

## 4. Métricas de Escalamiento
| Métrica | Definición | Objetivo |
|---------|-----------|----------|
| time_ms | Tiempo de entrenamiento | Crecimiento sub-lineal en SMA |
| cpu_avg | % CPU promedio | Explorar saturación vs coordinación |
| mem_peak_mb | Memoria pico | Control de overhead SMA |
| records_per_s | Throughput | Identificar caída vs tamaño |
| energy_j_per_mb (directo) | Eficiencia energética | Validar escalado |

## 5. Procedimiento Experimental por Tamaño
1. Generar dataset y metadatos.
2. Ejecutar lote (≥10 repeticiones) control y tratamiento.
3. Recolectar métricas y figuras.
4. Análisis incremental (comparar medianas y tamaños de efecto vs tamaño anterior).
5. Registrar impacto en energy (J/MB) y throughput.

## 6. Potenciales Riesgos
| Riesgo | Mitigación |
|--------|-----------|
| Memoria insuficiente | Monitorear; reducir batch size entrenamiento |
| Tiempo excesivo | Agendar ejecuciones nocturnas; usar semillas consistentes |
| Overhead agentes > Beneficio | Profiling interacciones; reducir mensajes innecesarios |

## 7. Roadmap
| Semana | Acción |
|--------|-------|
| 1 | Generar dataset 30k y correr lote piloto |
| 2 | Ajustar hiperparámetros (RF n_estimators, SVM kernel) para carga |
| 3 | Generar dataset 100k + lote comparativo |
| 4 | Validar proxy energías vs directo; documentar tendencias |
| 5 | Integrar dataset real pequeño para prueba reproductibilidad |

## 8. Extensiones Futuras
- Particionamiento de dataset y agentes especializados por shard.
- Evaluación de escalado horizontal (más procesos / nodos simulados).
- Incorporación de carga concurrente (lanzar múltiples entrenamientos en paralelo coordinados por SMA).

Última actualización: 2025-11-11
