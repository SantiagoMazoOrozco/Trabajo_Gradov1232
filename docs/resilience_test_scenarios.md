# Escenarios de Pruebas de Resiliencia

## 1. Objetivo
Medir la capacidad de adaptación y recuperación de la arquitectura SMA frente a fallos y degradaciones controladas, y compararla contra la arquitectura centralizada.

## 2. Métricas Clave
| Métrica | Definición | Unidad |
|---------|-----------|-------|
| fault_injected_count | Número total de fallos inducidos | conteo |
| fault_recovered_count | Número total de recuperaciones exitosas | conteo |
| recovery_success_rate | fault_recovered_count / fault_injected_count | proporción |
| recovery_time_ms_mean | Tiempo promedio de recuperación | ms |
| recovery_time_ms_p95 | Percentil 95 de tiempo de recuperación | ms |
| throughput_delta_pct | Cambio % en records_per_s post-fallo | % |
| cpu_spike_duration_ms | Duración de pico CPU tras recuperación | ms |

## 3. Tipos de Fallos
| Tipo | Descripción | Técnica de Inyección | Esperado |
|------|-------------|----------------------|----------|
| Reinicio agente | Terminar proceso agente Trainer | Señal SIGTERM + restart wrapper | Reaparece agente < 2s |
| Latencia mensajería | Retraso artificial ACL | Sleep en handler / cola intermediaria | Aumento recovery_time_ms |
| Pérdida de mensaje | Dropped ACL ocasional | Filtro aleatorio (p<0.05) | Reintentos, idempotencia |
| Caída API | Paro temporal endpoint `/train` | Simulación error HTTP 503 | Reintento exponencial backoff |
| Saturación CPU | Carga sintética (loop intenso) | Thread busy 1 núcleo | Degradación throughput < 30% |
| Fuga memoria | Incremento artificial buffer | Objeto grande mantenido | Mem_peak detectado, eventual GC |

## 4. Procedimiento General
1. Seleccionar escenario y número de repeticiones (≥ 5 por tipo de fallo).
2. Iniciar experimento con monitoreo activado.
3. Inyectar fallo en timestamp T.
4. Registrar:
   - Timestamp fallo
   - Timestamp recuperación (servicio/agente operativo)
   - Métricas de rendimiento pre y post ventana (±5s).
5. Persistir resultados en filas RESILIENCE_* dentro de `aggregate_metrics.csv` (extender script para capturar). 
6. Calcular métricas derivadas y añadir a panel Grafana de Resiliencia.

## 5. Instrumentación Requerida
- Wrapper supervisor de agentes: reinicio automático y hook de logging.
- Middleware ACL opcional para latencia/pérdida (simulación en Python o filtro JADE custom).
- Módulo de inyección: `scripts/inject_fault.py` con argumentos `--type` y parámetros.
- Logs estructurados: `fault_event.json` por experimento.

## 6. Panel Grafana (Diseño)
| Gráfico | Descripción |
|---------|-------------|
| Línea recovery_time_ms_mean | Evolución por escenario / experimento |
| Barras recovery_success_rate | Comparación control vs tratamiento |
| Heatmap throughput_delta_pct | Impacto por tipo de fallo |
| Tabla eventos | Últimos N fallos con tiempos |

## 7. Criterios de Éxito
| Criterio | Valor Objetivo |
|----------|---------------|
| recovery_success_rate | ≥ 0.95 |
| recovery_time_ms_mean | < 2000 ms (reinicio agente) |
| throughput_delta_pct | Recuperación a ±10% baseline en < 10s |
| Memoria tras fuga | Retorno a ±15% pico inicial |

## 8. Riesgos
| Riesgo | Mitigación |
|--------|-----------|
| Inyección excesiva degrada todo el lote | Limitar a ≤ 1 fallo simultáneo |
| Colisión de reinicios | Asegurar exclusión mutua en script injection |
| Métricas inconsistentes (timestamps desalineados) | Sincronizar reloj y usar `time.monotonic()` |
| Fuga real provoca OOM | Establecer tamaño máximo buffer de prueba |

## 9. Roadmap
| Semana | Acción |
|--------|-------|
| 1 | Implementar wrapper reinicio agente y logging básico |
| 2 | Inyectar latencia y pérdida mensaje (middleware ACL) |
| 3 | Script saturación CPU y caída API controlada |
| 4 | Captura de métricas y panel Grafana inicial |
| 5 | Optimización tiempos de recuperación y documentación resultados |

## 10. Extensiones Futuras
- Correlación resiliencia vs energía (energía extra durante recuperación).
- Escenarios multi-fallo (fallo compuesto: latencia + reinicio).
- Modelo predictivo de riesgo de fallo usando métricas previas.

Última actualización: 2025-11-11
