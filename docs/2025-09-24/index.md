# 2025-09-24

## Resumen de Cambios (UI Web Dashboard)

- Añadido dashboard web sobre FastAPI con rutas `/` y `/experiments/{id}`.
- Integración de plantillas Jinja2 (`base.html`, `experiments.html`, `experiment_detail.html`).
- Estilos básicos en `style.css`.
- Funciones de utilidad para listar experimentos y resumir métricas (incluyendo energía) sin tocar la lógica de entrenamiento.
- Documentación nueva: `docs/web_ui.md`.
- Actualización de `docs/experiments.md` con referencia a la UI y notas de agregación.

## Justificación Metodológica

La interfaz facilita la inspección transparente de resultados experimentales, apoyando la reproducibilidad y la trazabilidad de métricas de eficiencia y sostenibilidad energética.

## Próximos Pasos Sugeridos

- (Opcional) Gráficas comparativas energía/tiempo por algoritmo y grupo.
- (Opcional) Auto-refresh parcial con HTMX.
- (Opcional) Filtrado por fecha o grupo.
