# Hoja de Ruta Detallada (12 meses)

Este documento amplía la sección 4.3 del documento de tesis (`docs/plantilla_trabajo_grado_filled.md`) y detalla hitos, riesgos, dependencias y KPI para la evolución de la plataforma.

## Visión

Evolucionar el prototipo hacia un marco robusto de evaluación multi-dimensional (eficiencia, energía, resiliencia, escalabilidad y ética), con instrumentación reproducible y difusión científica.

## Fases y Entregables

1) 0–3 meses: Energía real y calibración.
- Integrar RAPL/powercap en backend y experimentos.
- Script de calibración proxy vs real; informe comparativo con <15% de error.
- Refactor de agregación para incluir Joules por ventana temporal.

2) 3–6 meses: Escalabilidad y modelos.
- Generador de datasets grandes; pipeline concurrente.
- Incluir XGBoost/LightGBM; benchmarks multi-modelo.

3) 6–9 meses: Resiliencia y autoscaling.
- Inyección de fallos; métricas MTTR y tasa de recuperación.
- Estrategias de auto-reconfiguración de agentes.

4) 9–12 meses: Analítica avanzada y difusión.
- Paneles Grafana completos (desempeño, energía, resiliencia).
- Análisis bayesiano y potencia estadística.
- Preprint/paper (arXiv/conferencia) y guía ética.

## KPI por Dimensión

- Energía: error proxy vs real (<10% a 12 meses).
- Eficiencia: >1.2x throughput tratamiento/control.
- Resiliencia: MTTR < 5s; recuperación ≥95%.
- Escalabilidad: dataset >500k filas.
- Reproducibilidad: script único end-to-end.
- Difusión: ≥2 publicaciones/preprints.

## Riesgos y Mitigación

- Permisos de hardware: usar contenedores privilegiados sólo en entornos controlados.
- Cuellos de botella E/S: profiling y caching intermedio.
- Retrasos de publicación: preparar preprint.

## Dependencias

- Acceso a hardware con RAPL habilitado.
- Recursos de cómputo para pruebas a gran escala.
- Acompañamiento de grupo de investigación (ética/metodología).

## Próximos Pasos Inmediatos

- Definir formato de series de energía en `logs/` (timestamps + valores).
- Extender `python-analysis/aggregate_metrics.py` para atribuir Joules por ventana de entrenamiento.
- Conectar paneles Grafana con Prometheus y CSV agregados.
