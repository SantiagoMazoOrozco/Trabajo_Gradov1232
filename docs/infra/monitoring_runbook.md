# Runbook de Monitoreo Profundo

Este runbook complementa `infra/monitoring_quickstart.md` con procedimientos detallados para operación, validación, recolección de evidencia y solución de problemas.

## 1. Objetivos
- Exponer métricas de desempeño y resiliencia del backend (FastAPI + entrenamiento/evaluación).
- Centralizar observabilidad con Prometheus y Grafana (tableros reproducibles).
- Generar evidencia (screenshots + artefactos) para la tesis y replicabilidad.

## 2. Componentes
| Servicio    | Puerto | Función                               | Fuente/Path                      |
|-------------|--------|---------------------------------------|----------------------------------|
| Backend     | 8000   | API + /health + /metrics              | `backend/api/main.py`            |
| Prometheus  | 9090   | Scrape + consultas                    | `infra/compose/prometheus.yml`   |
| Grafana     | 3000   | Visualización + dashboards            | `infra/grafana/*`                |
| JADE (opc.) | 1099   | Plataforma multi-agente (experimentos)| `infra/docker/jade.Dockerfile`   |

## 3. Métricas Clave (nombres orientativos)
- `train_requests_total`: contador de invocaciones de entrenamiento.
- `train_duration_seconds_*`: histograma de duración.
- `train_last_cpu_percent`, `train_last_mem_mb`: gauges de recursos.
- `eval_accuracy`, `eval_f1`: métricas de calidad del modelo.
- `recoveries_total`, `failures_total`, `retry_attempts_total`: resiliencia.

Validar presencia:
```bash
curl -fsS http://localhost:8000/metrics | grep -E 'train_duration_seconds|eval_accuracy|failures_total'
```

## 4. Procedimiento Operativo
### 4.1 Arranque
```bash
bash scripts/start_stack.sh --build   # primera vez (construye imágenes)
```
Esperar salud:
```bash
curl -fsS http://localhost:8000/health
```
### 4.2 Generación de Carga
Ejecutar 2–3 experimentos por grupo para rellenar histogramas y series:
```bash
bash scripts/run_experiment.sh --group control --monitor-seconds 15 --report
bash scripts/run_experiment.sh --group treatment --monitor-seconds 15 --report
bash scripts/run_batch.sh --repeats 3 --monitor-seconds 10
```
### 4.3 Agregación y Análisis
```bash
bash scripts/aggregate_metrics.sh
bash scripts/stats_analysis.sh
```
### 4.4 Captura de Evidencia
Tomar capturas de:
1. Dashboard completo (overview).
2. Panel de histograma de duración de entrenamiento.
3. Panel de métricas de evaluación (accuracy/f1).
4. Panel de CPU/Memoria.
5. Vista Prometheus con consulta `train_duration_seconds_count`.
6. Endpoint `/metrics` raw (primeras líneas).

Guardar en `docs/figures/monitoring/` con nombres: `grafana_overview.png`, `prom_query_train_duration.png`, etc.

### 4.5 Apagado
```bash
bash scripts/stop_stack.sh
```

## 5. Smoke Automático
Usar:
```bash
bash scripts/monitoring_smoke.sh
```
Verifica salud, corre carga mínima y agrega resultados.

## 6. Troubleshooting Detallado
| Problema | Síntoma | Acción |
|----------|---------|--------|
| Backend no expone métricas | 404 en `/metrics` | Revisar `requirements.txt` y reconstruir (`start_stack.sh --build`). |
| Dashboard vacío | Paneles sin datos | Aumentar número de experimentos (batch) y refrescar 5s → 1min. |
| Grafana sin dashboard | "Not found" | Confirmar provisioning: archivos en `infra/grafana/provisioning/dashboards`. Reiniciar grafana. |
| Latencias elevadas | Respuesta lenta | Revisar uso de CPU/Mem; correlacionar con entrenamiento concurrente. |
| Prometheus no scrapea | Serie `up` = 0 | Verificar `prometheus.yml` target host/port y salud del backend. |
| Contenedores reinician | Logs con OOM/Reinicios | Ajustar recursos Docker o reducir carga simultánea. |

## 7. Buenas Prácticas
- No almacenar datos brutos generados temporalmente: se ignoran en `data/results/` por `.gitignore`.
- Limitar experimentos largos antes de capturas para mantener contenedores ligeros.
- Usar tags de commit para marcar sesiones de evidencia (ej: `monitoring-capture-YYYYMMDD`).

## 8. Extensiones Futuras
- Añadir alertas Prometheus (reglas en `infra/compose/prometheus-alerts.yml`).
- Exportar dashboard JSON versionado (ya en repo) + script de snapshot.
- Integrar Jaeger/OTel para trazas si se requiere análisis de latencia inter-procesos.

## 9. Checklist Rápido
1. Stack arriba ✔
2. `/health` OK ✔
3. `/metrics` contiene series clave ✔
4. Dashboard con datos > 3 puntos por panel ✔
5. Evidencias guardadas en `docs/figures/monitoring/` ✔
6. Stack apagado sin errores ✔

## 10. Referencias
- `backend/api/main.py` (instrumentación)
- `infra/compose/docker-compose.yml`
- `infra/grafana/provisioning/`
- `scripts/monitoring_smoke.sh`

---
Última actualización: $(date +%Y-%m-%d)
