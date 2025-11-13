# 3) Objetivos e hipótesis (1:30–2:15)

## Objetivo general
Diseñar e implementar un prototipo de arquitectura basada en Sistemas Multiagente (SMA) para evaluar la eficiencia computacional y la sostenibilidad energética durante el entrenamiento de algoritmos de Machine Learning supervisado de clasificación, en entornos simulados de analítica de datos.  
(Fuente: Macroproceso §4)

## Objetivos específicos (resumen)
1) Modelar la arquitectura de un prototipo SMA para ingesta, preprocesamiento y preparación de datos de entrenamiento.  
2) Implementar el prototipo integrando al menos dos algoritmos (Random Forest y Support Vector Machine) sobre JADE.  
3) Evaluar la eficiencia computacional y la sostenibilidad energética frente a una arquitectura centralizada durante la fase de entrenamiento, midiendo tiempo, throughput, uso de CPU/memoria y energía normalizada (watts-first: W y W/MB).  
4) Analizar los resultados para validar eficiencia y sostenibilidad y sintetizar implicaciones técnicas/éticas/operativas.  
(Fuente: Macroproceso §5)

## Hipótesis y variables
- H0: No hay diferencias significativas entre control (centralizado) y treatment (SMA) en las métricas principales (p. ej., W/MB, time_ms).  
- H1: El SMA reduce el costo energético (W/MB) y/o el tiempo (time_ms) respecto al control.  
- Variable independiente: tipo de arquitectura (control vs SMA).  
- Variables dependientes: time_ms, records_per_s, cpu_avg, mem_peak_mb, avg_watts (W), watts_per_mb (W/MB), watts_per_record (W/registro).

## Criterios de evaluación
- Evidencia cuantitativa: pruebas de permutación (≥5000) por etapa/métrica; nivel de significancia p < 0.05; tamaño de efecto.  
- Evidencia visual: barras con IC95% y tendencias ("picos"); tablas resumen reproducibles desde CSV.  

> Figura opcional: mini-tabla de métricas (`docs/figures/summary_table_metrics.png`) o control-only. 