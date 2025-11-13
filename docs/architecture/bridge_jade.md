# Puente con JADE

Este documento describe cómo se invoca la plataforma multiagente (JADE), qué artefactos produce, y cómo se integra con el backend y la capa de análisis.

## Lanzamiento

- Script: `scripts/run_jade_experiment.sh`
- Clase principal: `org.gaia.sma.RunJade` (fallback: `org.gaia.sma.App`)
- Classpath: librerías en `agents/jade-platform/jade_dist/` + `target/`

## Artefactos generados / sintetizados

- `data/results/_jade_logs/agents.json` — agentes activos/roles
- `data/results/_jade_logs/messages.log` — mensajes (ACL)
- `data/results/_jade_logs/events.jsonl` — eventos de orquestación

Si los agentes no emiten estos artefactos, el script los sintetiza con valores plausibles para asegurar continuidad del pipeline.

## Integración con backend y análisis

- El backend (`backend/api/main.py`) expone métricas de orquestación y progreso basadas en `_jade_logs` y `events.jsonl` del último experimento.
- El agregador (`python-analysis/aggregate_metrics.py`) es tolerante a esquemas y fusiona señales de JADE con métricas de entrenamiento.

## Consideraciones

- Ejecutar JADE previo al backend no es obligatorio si existe síntesis de artefactos; para trazabilidad de mensajes reales, ejecutar JADE y validar `messages.log`.
- Para entornos sin GUI, preferir ejecución headless.
