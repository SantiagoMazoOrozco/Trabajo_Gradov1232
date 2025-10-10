# 2025-10-02

## Extensión de métricas de eficiencia

- API: nuevas métricas en entrenamiento: `n_train`, `mb_processed`, `records_per_s`, `data_mb_per_s`, `energy_j_per_record`, `efficiency_cpu_rps_per_pct`, `efficiency_mem_rps_per_mb`.
- Agregación: columnas añadidas para las métricas anteriores.
- Estadística: se agregan pruebas para `records_per_s` en TRAIN_RF y TRAIN_SVM.
- Reporte HTML: ahora muestra throughput, MB/s y J/record.
- UI Web: detalle de experimento incluye las nuevas métricas.
- Documentación: `docs/experiments.md` ampliado con definiciones.

Ver detalle de la actividad: [docs/actividades/2025-10-02-metricas-eficiencia](../actividades/2025-10-02-metricas-eficiencia/index.md)

Actividad relacionada (diseño de arquitectura y experimento): [docs/actividades/2025-10-02-diseno-arquitectura-experimento](../actividades/2025-10-02-diseno-arquitectura-experimento/index.md)

## Impacto en Macroproceso

Estas métricas cubren "Eficiencia del procesamiento de datos" (throughput), "Eficiencia por unidad de carga" (por CPU y memoria), y refinan la dimensión de sostenibilidad con `J/record` además de `J/MB`.

## Fase 2: Integración SMA/JADE

Se documenta la evidencia de la Fase 2 (orquestación vía CLI y actualización del Macroproceso):
- [docs/actividades/2025-10-02-fase2-arquitectura-sma](../actividades/2025-10-02-fase2-arquitectura-sma/index.md)
