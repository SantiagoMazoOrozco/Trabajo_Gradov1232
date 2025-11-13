# Roadmap — Próximas 4 semanas (hasta cierre de semestre)

Fecha de inicio: 2025-11-11

## Semana 1
- Integrar lectura de potencia/energía (RAPL/powercap) bajo Linux:
  - Implementar lector en python-analysis (fallback al proxy actual)
  - Variable de configuración y validación en 1–2 corridas
- Instrumentar métricas de resiliencia:
  - Contar eventos de fallo inducido/simulado y recuperación
  - Registrar `recovery_time_ms_mean/p95`, `recovery_success_rate`
- Decidir estado de `backend/api/` (restaurar endpoints mínimos o documentar deprecación)

## Semana 2
- Ejecutar batch ampliado (≥20 por grupo) con energía real y resiliencia activa
- Agregar nuevas figuras (violines/boxplots) y actualizar `aggregate_metrics.csv`
- Recalcular p-values y tamaños de efecto; actualizar `docs/_auto_results_tables.*`

## Semana 3
- Redacción final de Resultados y Discusión (actualizar `thesis_results_section.md`)
- Conclusiones y Trabajos futuros (ampliar `conclusions_implications_future_work.md`)
- Añadir sección de ética y sostenibilidad (`docs/ethics_and_sustainability.md`)

## Semana 4
- Validación cruzada y revisión (QA de scripts, reproducibilidad en limpio)
- Preparación de la presentación final (versión PDF)
- Checklist de entrega institucional y empaquetado de evidencia (ZIP)

## Hitos de verificación
- H1 (fin Semana 1): energía real integrada; resiliencia instrumentada
- H2 (fin Semana 2): batch ampliado + análisis actualizado
- H3 (fin Semana 3): redacción consolidada
- H4 (fin Semana 4): entrega final lista
