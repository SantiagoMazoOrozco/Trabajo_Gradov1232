# Arquitectura — Índice

Este índice organiza la documentación de arquitectura del prototipo SMA para evaluar eficiencia computacional y sostenibilidad energética durante el entrenamiento de clasificadores supervisados en entornos simulados.

## Documentos

- Arquitectura general y vistas principales: `architecture.md`
- Puente con JADE (lanzamiento, artefactos y acoplamientos): `bridge_jade.md`
- Protocolo de mensajes y eventos: `message-protocol.md`

## Vistas

- Contexto y componentes
- Procesos y etapas (PREPROCESS → TRAIN/EVAL)
- Observabilidad (Prometheus/Grafana) y agregación
- Despliegue local con Docker Compose

## Archivos y rutas relevantes

- Backend: `backend/api/main.py`
- Agentes/JADE: `agents/jade-platform/` y `scripts/run_jade_experiment.sh`
- Simulación y análisis: `python-analysis/*.py`
- Infraestructura de monitoreo: `infra/compose/*`
- Resultados: `data/results/`

> Referencias cruzadas: `docs/monitoring_spec.md`, `docs/energy_plan.md`, `docs/achievements/cumplimiento_objetivo_general.md`.
