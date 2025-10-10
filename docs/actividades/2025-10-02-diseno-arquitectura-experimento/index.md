# Actividad 2: Diseño de la Arquitectura del SMA y del Experimento (2025-10-02)

Estado: Completado (Fase 1 funcional)

## Evidencias principales
- `docs/architecture.md`: agentes, responsabilidades, flujo, contratos, requisitos no funcionales e integración con Python/REST.
- `docs/experiment-design.md`: plantilla de diseño experimental (factores, métricas, repeticiones, procedimiento), alineada con el Macroproceso.
- `docs/message-protocol.md`: contratos de mensajes y payloads (Prep, Train, Eval, etc.)
- Orquestación ejecutable:
  - `python-analysis/simulate_experiment.py`: simula interacciones entre agentes (Preprocessing, Training RF/SVM, Evaluation), con logs estructurados.
  - `python-analysis/api/main.py`: endpoints REST para preprocess, train, evaluate, con métricas de eficiencia y energía.
  - `scripts/run_experiment.ps1` y `scripts/run_batch.ps1`: ejecución reproducible, grupos control vs. treatment, semillas y reports.
- UI Web (`/`, `/experiments/{id}`): navegación de resultados, demostrando trazabilidad end-to-end.

## Alcance de esta fase
- Mock funcional (con FastAPI y scripts Python) que refleja el modelo multiagente planificado.
- Estructura de nombres de agentes parametrizable (`python-analysis/agent_config.json`) para futura integración JADE.
- Persistencia por experimento en `data/results/<id>/` con logs JSON línea.

## Qué queda opcional para una fase 2
- Integración real con JADE como orquestador/actores (el mock ya está listo para ser llamado desde JADE por REST/CLI).
- Métricas de adaptabilidad/resiliencia en escenarios con fallos inducidos (ya hay RETRY/FAILURE en logs; faltaría protocolo de tests de resiliencia y su análisis).
- Gráficas en la UI (Chart.js) y filtros por grupo.

## Cómo reproducir
1) Ejecutar un experimento de ejemplo (ver `docs/experiments.md`).
2) Verificar que se generan `prep/`, `models/`, `eval/`, `logs/`, `report/` en `data/results/<id>/`.
3) Abrir la UI y navegar.

## Conclusión
Se cumple la actividad en su alcance de Fase 1: arquitectura definida y operativa, con flujo end-to-end, contratos y documentación; queda terreno preparado para integrar una plataforma SMA (JADE) sin rehacer componentes.
