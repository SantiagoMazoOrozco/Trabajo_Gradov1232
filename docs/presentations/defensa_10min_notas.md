# Notas del orador — Defensa 10 min

Tiempo objetivo: 10:00 (±0:15)

## Slide 1 — Portada (0:30)
- Presentarte y enunciar en una frase el aporte: “Marco SMA reproducible para evaluar eficiencia y sostenibilidad en ML”.

## Slide 2 — Agenda (0:30)
- Explica que seguirás un ritmo de 1 idea/slide y que hay backups para preguntas.

## Slide 3 — Problema y motivación (1:00)
- Puntos clave: eficiencia + sostenibilidad importan; SMA puede ayudar; falta evidencia comparativa con energía.

## Slide 4 — Objetivo general (0:40)
- Leer/para-frasear el objetivo y remarcar “entrenamiento”, “RF/SVM”, “escenarios controlados”.

## Slide 5 — Objetivos específicos (0:40)
- Mapea rápido a cómo se cumplió (implementar, evaluar, analizar).

## Slide 6 — Metodología (1:10)
- Cómo/Por qué/Para qué. 10 repeticiones por grupo; permutaciones ≥5000; proxy energético documentado.

## Slide 7 — Arquitectura y stack (1:20)
- JADE + FastAPI + Prometheus/Grafana; flujo PREPROCESS→TRAIN→EVAL; agentes coordinan.

## Slide 8 — Datos, experimento y métricas (1:10)
- Dataset sintético reproducible; métricas: time_ms, cpu, memoria, records/s, J/MB; J = W×s.

## Slide 9–10 — Resultados (2:00)
- Mensaje clave: p ≥ 0.05 (no diferencias significativas).  
- Sugerir razones: escala, overhead de coordinación.

## Slide 11 — Análisis/validez (1:00)
- Permutaciones, tamaños de efecto, amenazas: constructo (proxy), interna (SO), externa (dataset).

## Slide 12 — Conclusiones (0:40)
- SMA funcional y reproducible; marco listo para escalar y medir con RAPL; resultados actuales no significativos.

## Slide 13 — Aportes (0:40)
- Arquitectura + scripts + dashboards + normalizaciones; checklist y capítulos listos.

## Slide 14 — Futuro y cierre (0:20)
- Integrar RAPL/powercap, escalar datasets/concurrencia, resiliencia/elasticidad.  
- Invitar a preguntas.

---

# Preguntas frecuentes y respuestas breves

- ¿Por qué SMA/JADE?  
  Modularidad, resiliencia y orquestación distribuida; JADE es estable y permite agentes con bajo acoplamiento.

- ¿Por qué RF/SVM y no deep learning?  
  Representativos, reproducibles, rápidos; adecuan la primera evaluación de arquitectura.

- ¿Por qué no hubo diferencias significativas?  
  Escala actual (dataset y concurrencia) + overhead; se necesita mayor volumen/particionamiento y medición directa.

- ¿Cómo miden energía sin RAPL?  
  Proxy watts-first (`CPU_POWER_W × uso CPU`), transparente y calibrable; plan de integrar RAPL/powercap.

- ¿Validez externa?  
  Limitada por dataset sintético; el marco es generalizable a datasets reales.

- ¿Reproducibilidad?  
  Checklist en `docs/appendix/reproducibility_checklist.md`, artefactos versionados en `data/results/*`, scripts `scripts/*`.

- ¿Riesgos éticos?  
  Control humano significativo; transparencia en mediciones y reporte.

- ¿Hardware/entorno?  
  JDK 21, Maven 3.9.6, JADE 4.6.0; FastAPI; Prometheus+Grafana; proxy energético configurado con `CPU_POWER_W`.
