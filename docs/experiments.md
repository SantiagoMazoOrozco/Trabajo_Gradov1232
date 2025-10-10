# Experimentos: ejecución, agregación y análisis

## 1) Ejecución individual

- VS Code → Tasks → "Experiments: Run single (treatment, monitored)"
- PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_experiment.ps1 -ExperimentId exp_demo -Group treatment -Monitored -MonitorSeconds 120 -Report -Seed 42
```

Artefactos: `data/results/<exp>/` (prep/, models/, eval/, logs/, monitor/, report/)

Nota: la UI web ahora permite navegar estos artefactos en `http://127.0.0.1:8000/` (ver `docs/web_ui.md`).

## 2) Lote (control vs treatment)

- VS Code → Tasks → "Experiments: Run batch (control vs treatment)"
- PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_batch.ps1 -Repeats 10 -SeedBase 42 -MonitorSeconds 60
```

Esto corre 10 control y 10 treatment con distintas semillas, agrega y ejecuta análisis.

## 3) Agregar métricas

```powershell
.\.venv\Scripts\python.exe .\python-analysis\aggregate_metrics.py
```

Salida: `data/results/aggregate_metrics.csv` con columnas: experimentId, group, stage, time_ms, cpu_avg, mem_peak_mb, energy_j_total, energy_j_per_mb, accuracy, f1.

Notas:
- Se ignoran carpetas sin `logs/events.jsonl` o que comienzan con `_`.
- Experimentos antiguos sin `meta.json` con campo `group` no se incluyen.

## 4) Análisis estadístico (permutation test)

```powershell
.\.venv\Scripts\python.exe .\python-analysis\stats_analysis.py
```

Salida: `data/results/stats_summary.md` y `.json` con p-values comparando grupos (A vs B) por etapa/métrica.

Interpretación rápida:
- p-value < 0.05: diferencia estadísticamente significativa.
- Revisa también los tamaños de efecto (medias A/B) y la consistencia entre métricas.

## 5) Semillas y reproducibilidad

- `-Seed` en ejecución individual, `-SeedBase` en lote (se deriva por repetición y grupo).
- Semillas quedan registradas en `data/results/<exp>/meta.json` junto con el grupo y parámetros de entorno.

## 7) Proxy de energía y variable CPU_POWER_W

- Durante el entrenamiento, se estima la energía consumida como:
	- energy_j_total = CPU_POWER_W × (cpu_avg/100) × (time_ms/1000)
	- energy_j_per_mb = energy_j_total / MB_procesados
- CPU_POWER_W define la potencia promedio del CPU (en vatios). Si no se especifica, se usa 35 W por defecto.
- Para ajustar el proxy a tu hardware en PowerShell:

```powershell
$env:CPU_POWER_W = 50
```

- La métrica aparece en el reporte por experimento y en el agregado/analítica estadística.

Métricas derivadas adicionales (entrenamiento):
- `records_per_s`: throughput en registros por segundo (n_train / tiempo_s)
- `data_mb_per_s`: MB procesados por segundo (MB / tiempo_s)
- `energy_j_per_record`: energía por registro (J / n_train)
- `efficiency_cpu_rps_per_pct`: records/s por 1% CPU (records_per_s / cpu_avg)
- `efficiency_mem_rps_per_mb`: records/s por MB de pico (records_per_s / mem_peak_mb)

## 8) UI Web (Dashboard)

- Navegación: abrir `http://127.0.0.1:8000/` mientras el servidor FastAPI esté corriendo.
- Listado de experimentos, métricas de energía y evaluación, eventos brutos.
- Consultar detalles: `/experiments/<experimentId>`.
- Documentación: `docs/web_ui.md`.

## Integración con JADE vía CLI

Para que agentes en JADE (u otra plataforma JVM) puedan invocar el pipeline sin acoplarse al REST, se incluye un puente de línea de comandos:

- Script: `python-analysis/agent_cli.py`
- Documentación: `docs/bridge_jade.md`

Ejemplos (PowerShell):

```powershell
python python-analysis/agent_cli.py preprocess --experiment-id exp_demo --data data/raw/synthetic_classification.csv --scale true --test-size 0.2 --seed 42 --out prepRef.json
python python-analysis/agent_cli.py train --experiment-id exp_demo --algo RF --seed 42 --prep-ref-file prepRef.json --out train_rf.json
python python-analysis/agent_cli.py evaluate --experiment-id exp_demo --model-ref-file train_rf.json --metrics accuracy f1 --confusion-matrix true --out eval_rf.json
```

Use la variable de entorno `API_BASE` si el servicio corre en otra dirección.

## 6) Consejos

- Mantén `.venv` activo y las dependencias de `requirements.txt` instaladas.
- Usa `-Quiesce` y `-HighPriority` si buscas reducir ruido del sistema.
- Ajusta `MonitorSeconds` para capturar suficiente señal en entrenamiento.