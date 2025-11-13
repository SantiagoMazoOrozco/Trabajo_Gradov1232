# Metodología

Este capítulo responde de forma directa a: cómo fue (el método), por qué se usó (justificación) y para qué se usó (propósito y alcance), y desarrolla el enfoque cuantitativo–cualitativo, el diseño, la operacionalización de variables, los instrumentos de medición, el plan analítico, así como consideraciones de resiliencia, escalabilidad, validez y ética.

## Cómo fue (qué hicimos y cómo se ejecutó)

- Enfoque mixto con primacía cuantitativa y complemento cualitativo:
  - Cuantitativo: medición sistemática para contrastar la hipótesis principal y estimar efectos de la arquitectura sobre variables de eficiencia y energía bajo condiciones controladas o equivalentes.
  - Cualitativo (interpretativo): análisis documental para comprender implicaciones éticas, contextuales y sociotécnicas de los SMA.
- Tipo y diseño:
  - Investigación aplicada (prototipo operativo con utilidad práctica).
  - Diseño experimental o cuasiexperimental: comparación entre grupo de control (arquitectura centralizada) y grupo de tratamiento (SMA en JADE) con cargas y condiciones equiparables.
- Procedimiento resumido:
  1) Generación de dataset sintético reproducible (semillas y parámetros fijados).
  2) Ejecución del pipeline PREPROCESS → TRAIN → EVAL en modo control y en modo SMA (tratamiento).
  3) Instrumentación con Prometheus (raspado de métricas) y registro de eventos/metadata por corrida.
  4) Agregación de métricas a CSV y derivación de indicadores compuestos (incluyendo energía “watts-first” y Joules por MB).
  5) Análisis descriptivo y pruebas comparativas; visualización en Grafana y reportes por ejecución.
- Enfoque cualitativo: análisis de contenido temático sobre documentación académica, industrial y regulatoria para identificar categorías (eficacia, resiliencia, sostenibilidad, ética energética, gobernanza), dilemas y contextos sociotécnicos.

## Por qué se usó (justificación del método)

- Primacía cuantitativa:
  - Permite probar la hipótesis principal y establecer relaciones causales entre tipo de arquitectura (VI) y métricas de eficiencia/energía (VD).
  - Facilita generalización y comparación con resultados cuantificables (tiempo, throughput, CPU, memoria, energía).
- Investigación aplicada y diseño (cuasi)experimental:
  - Alineado con la meta de construir y evaluar una solución práctica (prototipo SMA) y atribuir efectos a la arquitectura bajo condiciones controladas o equiparables.
- Complemento cualitativo:
  - Esencial para comprender transformaciones, riesgos y dimensiones éticas que los números no capturan (significados, tensiones, gobernanza, aceptación).
- Dimensión energética (Green Computing):
  - Relevante para sostenibilidad tecnológica; normalizaciones (J/MB, W/registro) permiten comparar escenarios y cargas heterogéneas de forma justa.
- SMA como tratamiento:
  - Los SMA prometen adaptabilidad y resiliencia ante fallos/cambios; el diseño permite evaluar si esas propiedades impactan eficiencia y consumo en la práctica.

## Para qué se usó (objetivo práctico y evaluaciones)

- Medir el efecto de la arquitectura SMA vs. una arquitectura centralizada sobre:
  - Eficiencia de procesamiento (tiempo, throughput, CPU, memoria) y métricas derivadas (eficiencia por %CPU y por MB).
  - Eficiencia energética (J/MB, W promedio y normalizados).
  - Propiedades operativas clave: adaptabilidad/resiliencia (respuesta a eventos y recuperaciones) y escalabilidad (comportamiento ante mayor volumen de datos).
- Generar evidencia para la toma de decisiones de arquitectura en contextos de entrenamiento de ML orientados a eficiencia y sostenibilidad.

## Enfoque metodológico detallado

- Enfoque: mixto (cuantitativo predominante + cualitativo interpretativo).
- Tipo: investigación aplicada.
- Diseño: experimental o cuasiexperimental con grupos control (centralizado) y tratamiento (SMA) bajo condiciones equivalentes.

## Operacionalización de variables

- Variable Independiente (VI): Tipo de arquitectura
  - Control: arquitectura centralizada (grupo de control).
  - Tratamiento: Sistema Multiagente (SMA) en JADE (grupo de tratamiento).
- Variables Dependientes (VD): Eficiencia y Energía
  - Eficiencia de procesamiento:
    - Tiempo total de ejecución (ms o s equivalente).
    - Rendimiento (throughput) en registros por ms (o por s, según exposición de métricas) y por algoritmo.
    - Uso promedio de CPU (%).
    - Uso de memoria (MB, pico o promedio según métrica recogida).
    - Eficiencia por unidad de carga: registros procesados por segundo y por %CPU.
    - Eficiencia por consumo de memoria: registros por MB utilizado.
  - Eficiencia energética (Green Computing):
    - Consumo estimado en Joules por MB procesado: J = W × s; normalizado por MB procesados.
    - Fuente de potencia (watts-first): RAPL/powercap cuando está disponible; proxy de potencia CPU calibrable cuando no.
- Adaptabilidad y Resiliencia
  - Tiempo de respuesta ante eventos dinámicos (s).
  - Tasa de éxito en reconfiguración autónoma (%).
  - Número de fallos recuperados automáticamente (conteo).
  - Eficiencia adaptativa: tiempo promedio de recuperación / eventos adaptativos resueltos.
- Escalabilidad
  - Capacidad de mantener métricas ante incrementos significativos del volumen de datos (filas/MB).

## Instrumentos, datos y procedimiento

- Instrumentos: Prometheus (raspado 1 s), Grafana (dashboards versionados), backend de métricas, scripts de ejecución, agregación y análisis.
- Datos: dataset sintético reproducible; resultados por ejecución (meta, eventos, reportes); CSV consolidado con métricas y derivadas.
- Procedimiento (resumen):
  1) Preparación del entorno y dataset.
  2) Corridas control y tratamiento con parámetros equivalentes.
  3) Medición, agregación y derivación de indicadores compuestos.
  4) Análisis descriptivo y contrastivo; visualización y reporte.

## Plan de análisis

- Descriptivo: tendencias y estadísticos (medias, p50/p95, varianza) por algoritmo y grupo.
- Pruebas de hipótesis: t-test o Mann-Whitney según supuestos; intervalos de confianza; tamaño de efecto (Cohen’s d) para magnitud práctica.
- Visualización: paneles Grafana (tiempo real y post-mortem) y reportes por ejecución.

## Validez y ética

- Validez interna: control de semillas/dataset/carga; condiciones equiparables.
- Validez de constructo: métricas de energía normalizadas (J/MB) y su interpretación según perfil de I/O.
- Validez externa: generalización limitada por dataset sintético; se proyectan evaluaciones con datos reales.
- Ética energética: transparencia en suposiciones (RAPL/proxy), reporte responsable y reproducible.

## Notas y consideraciones

- Cuando la telemetría energética directa no es viable, se emplea un proxy de potencia CPU calibrable; los Joules se derivan con la duración medida.
- Las unidades (reg/ms vs reg/s) se documentan y, cuando procede, se normalizan para comparabilidad.

## Referencias cruzadas

- Arquitectura y SMA: ver documentación de arquitectura y puente JADE.
- Observabilidad y energía: ver especificación de monitoreo y plan energético.
- Cumplimiento de objetivos: ver capítulos de cumplimiento del objetivo general y objetivos específicos.
