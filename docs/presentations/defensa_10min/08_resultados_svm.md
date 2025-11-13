# 8) Resultados — SVM (6:45–7:45)

- Hallazgo clave: bajo la carga actual no se observaron diferencias significativas entre control y SMA (p ≥ 0.05) en las métricas principales.
- Enfoque: comparar tiempo de entrenamiento y energía normalizada.

Tiempo de entrenamiento (ms)

![TRAIN_SVM time_ms](../../figures/train_time_ms_svm.png)

Energía normalizada (J/MB)

![TRAIN_SVM energy_j_per_mb](../../figures/train_energy_j_per_mb_svm.png)

Notas
- Barras con IC95% y distribución ordenada por mediana (cuando aplica).
- Resultados reproducibles desde `data/results/aggregate_metrics.csv` y `data/results/stats_summary.{md,json}`.
- Variante watts-first disponible (W/MB): `../../figures/train_watts_per_mb_svm.png`.
