# Diseño Experimental (Plantilla)

## 1. Objetivo General
(Definir la meta principal del experimento con agentes y ML.)

## 2. Preguntas de Investigación
- RQ1: ...
- RQ2: ...

## 3. Hipótesis
- H1: ...
- H2: ...

## 4. Variables
### 4.1 Independientes (Factores)
| Factor | Descripción | Niveles Iniciales |
|--------|-------------|-------------------|
| Modelo | Algoritmo de clasificación | RF, SVM |
| n_estimators | Árboles en RandomForest | 50, 100 |
| kernel | Kernel en SVM | rbf, linear |
| batch_size | Tamaño de lote de mensajes | 10, 50 |
| concurrency | Nº agentes entrenando en paralelo | 1, 2 |

### 4.2 Dependientes (Métricas)
| Métrica | Descripción | Unidad |
|---------|-------------|--------|
| accuracy | Exactitud global | proporción |
| f1 | F1-score macro | proporción |
| train_time | Tiempo entrenamiento modelo | ms |
| cpu_usage | Uso medio CPU durante etapa | % |
| mem_peak | Memoria pico proceso | MB |

### 4.3 Controladas
- Semilla aleatoria.
- Dataset congelado.
- Hardware.

## 5. Tratamientos
(Definir combinaciones seleccionadas; puede ser factorial completo o fraccionado.)

## 6. Diseño
- Tipo: (ej. factorial 2^k parcial)
- Repeticiones por tratamiento: (ej. 5)
- Orden: aleatorizado.

## 7. Procedimiento
1. Registrar configuración hardware/software.
2. Cargar dataset.
3. Lanzar Orchestrator + agentes.
4. Ejecutar pipeline para cada tratamiento.
5. Loggear eventos estructurados JSON línea.
6. Persistir métricas en `data/results/` (ignoradas por Git).

## 8. Criterios de Parada
- Timeout global (p.ej. 15 min por tratamiento).
- Fallos consecutivos > N.

## 9. Formato de Registro (Ejemplo)
```json
{
  "timestamp": "2025-09-09T12:00:10Z",
  "experimentId": "exp001",
  "treatment": {"model": "RF", "n_estimators": 100},
  "agent": "TrainingRF",
  "event": "MODEL_TRAINED",
  "metrics": {"f1": 0.87, "train_time_ms": 453}
}
```

## 10. Riesgos y Mitigación
| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Variabilidad hardware | Sesgos en tiempo | Registrar recursos y repetir |
| Desincronización agentes | Bloqueos | Timeouts y watchdog |

## 11. Versionado del Documento
Incrementar sección de cambios con cada actualización relevante.
