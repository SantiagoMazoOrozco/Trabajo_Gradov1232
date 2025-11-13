# Defensa (10 minutos + 5 Q&A)

Nota de tiempo: Contenido planificado para ~9:30 con 30 s de buffer. Regla: 1 idea/slide, 1 figura/slide, 2–3 bullets cortos, takeaway explícito.

---

## Slide 1 — Título y one‑liner (0:00–0:45)
- Título: “Eficiencia y Sostenibilidad Computacional de Algoritmos de Machine Learning …”
- One‑liner (aporte): “Marco SMA reproducible para evaluar eficiencia y sostenibilidad en ML”.
- Agenda en una línea: Problema → Método → Resultados → Impacto.

Takeaway: Aporto una plataforma experimental SMA, reproducible y monitoreada, para medir eficiencia/energía en ML.

---

## Slide 2 — Problema y motivación (0:45–1:30)
- ML debe evaluarse por precisión + eficiencia + sostenibilidad.
- Brecha: No hay arquitecturas SMA generalizables que integren todo el pipeline con sostenibilidad energética.
- Soporte: Referencias clave (citadas en `docs/bibliography_apa.md`/`refs.bib`).

Takeaway: Falta un marco práctico y replicable para medir eficiencia/energía más allá de la precisión.

---

## Slide 3 — Objetivos e hipótesis (1:30–2:15)
- Objetivo general: Prototipo SMA para evaluar eficiencia y sostenibilidad energética en entrenamiento supervisado.
- Específicos: (1) Implementar SMA con RF y SVM; (2) Evaluar Watts (promedio) y W/MB vs. baseline centralizado.
- Hipótesis: Bajo la carga actual, SMA no empeora significativamente tiempo ni W/MB vs. centralizado.

Takeaway: Defino objetivos medibles y una hipótesis falsable sobre eficiencia/energía.

---

## Slide 4 — Contribución y arquitectura (2:15–3:30)
- Arquitectura: SMA en JADE (Java) + Backend FastAPI con métricas Prometheus.
- Innovación: Integración modular Prometheus/Grafana + métrica energía normalizada (watts‑first proxy).
- Diagrama: desde `docs/architecture.md` (o figura en `docs/figures/`).

Takeaway: Una plataforma SMA modular y replicable que instrumenta todo el pipeline con métricas.

---

## Slide 5 — Metodología y dataset (3:30–4:45)
- Diseño: Control (centralizado) vs. Tratamiento (SMA), N≥10 repeticiones, semilla fija.
- Dataset: Sintético y reproducible (`python-analysis/generate_dataset.py`).
- Protocolo: Scripts versionados (`scripts/run_experiment.sh`, `scripts/run_batch.sh`).

Takeaway: Experimentos controlados y completamente reproducibles con pipelines automatizados.

---

## Slide 6 — Métricas e instrumentación (4:45–5:45)
- Métricas: time_ms, throughput (records/s), cpu_avg, mem_peak_mb.
- Sostenibilidad: Potencia promedio (W) y potencia normalizada (W/MB), enfoque watts‑first: P_avg ≈ CPU_POWER_W × (cpu_avg/100).
- Monitoreo: Prometheus/Grafana; especificación en `docs/monitoring_spec.md`.

Takeaway: Instrumentación consistente para rendimiento y energía normalizada.

---

## Slide 7 — Resultados (RF) (5:45–6:45)
- Figura hero: Tiempo (ms) RF — `docs/thesis_results_section.md` / generado por `python-analysis/generate_thesis_figures.py`.
- Figura hero: W/MB RF (barras) y tendencia (opcional).
- Hallazgo: p ≥ 0.05 (sin diferencia significativa) vs. centralizado.

Takeaway: Para RF, SMA ≈ baseline en tiempo y J/MB bajo esta carga.

---

## Slide 8 — Resultados (SVM) (6:45–7:45)
- Figura hero: Tiempo (ms) SVM.
- Figura hero: W/MB SVM (barras) y tendencia (opcional).
- Hallazgo: p ≥ 0.05 (sin diferencia significativa) vs. centralizado.

Takeaway: Para SVM, no hay degradación significativa en eficiencia/energía.

---

## Slide 9 — Validación y estadística (7:45–8:30)
- Pruebas de permutación (N≥5000) y control de α=0.05 (`python-analysis/stats_analysis.py`).
- Resultados: p ≥ 0.05 en métricas principales.
- Amenazas a la validez: proxy energético; dataset sintético/tamaño.

Takeaway: Resultados robustos bajo el análisis elegido, con amenazas conocidas y acotadas.

---

## Slide 10 — Limitaciones y lecciones (8:30–9:15)
- Límites: dataset y carga; energía estimada (no medida directa).
- Lecciones: plataforma SMA funcional, reproducible y escalable.
- Qué no funcionó: [mencionar breve si aplica].

Takeaway: La plataforma está lista para escalar y mejorar la medición energética.

---

## Slide 11 — Conclusiones e impacto/futuro (9:15–10:00)
- Conclusión: Base experimental reproducible para medir eficiencia y sostenibilidad en ML.
- Impacto: Mejora de procesos de evaluación con métricas comparables.
- Próximos pasos: RAPL/powercap, datasets mayores/concurrencia, resiliencia (`docs/future_work_roadmap.md`).

Takeaway: La contribución habilita evaluación práctica y extensible hacia medición directa y escalabilidad.

---

# Respaldo (Q&A)

- Reproducibilidad: scripts (`scripts/run_*`), reportes (`python-analysis/report_run.py`), tablas auto‑generadas (`docs/_auto_results_tables.*`).
- Setup/stack: `infra/compose/`, `scripts/start_stack.sh`, monitoreo (`docs/grafana/`, `docs/monitoring_spec.md`).
- Estadística: `python-analysis/stats_analysis.py`, `docs/stats_report.md`.
- Energía: justificación del proxy watts‑first; plan para medición directa (RAPL/powercap).
- Costos/tiempo: tiempos por corrida, recursos usados; escalabilidad del SMA.
- Amenazas/validez: interna/externa; sesgo del dataset; plan de mitigación.
- Comparativas: baselines/ablations si están en `docs/experiments.md`.

---

## Notas de delivery
- Terminar en 9:30 para buffer. Cierre memorizado (30–40 s).
- Cada figura con etiquetas claras y un caption con el efecto (Δ% y p‑valor si aplica).
- Frases guía de transición: “¿Por qué importa?” al pie de cada slide.
