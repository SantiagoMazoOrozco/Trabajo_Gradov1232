# Runbook Fase 1: Ejecución controlada

Este runbook describe cómo ejecutar la API experimental (preprocess/train/evaluate) y un flujo E2E controlado en Windows PowerShell, asegurando reproducibilidad y mínima interferencia.

## 1) Checklist de entorno controlado
- Cerrar aplicaciones pesadas (navegadores con muchas pestañas, IDEs extra, juegos, etc.).
- Conectar a corriente (sin modo ahorro) y seleccionar plan de energía “Alto rendimiento”.
- Desactivar temporalmente sincronizaciones/cargas intensivas (OneDrive, descargas, indexado pesado).
- Usar el dataset congelado de `data/raw/` y no modificarlo.
- Ejecutar en un entorno virtual (venv) limpio y con `requirements.txt` instalado.
- Fijar semillas (ya está en el código) y repetir corridas para promediar (sugerido ≥ 10).

## 2) Preparar entorno (una vez por máquina)
```powershell
# (opcional) Python 3.11 recomendado
# winget install -e --id Python.Python.3.11

# En la raíz del repo
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea scripts: el comando `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` habilita solo la sesión actual.

## 3) Levantar la API y correr el experimento (manual)
Abrir 2 terminales PowerShell en la raíz del repo:

Terminal A (API):
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn python-analysis.api.main:app --host 127.0.0.1 --port 8000 --log-level warning
```

Terminal B (simulación):
```powershell
.\.venv\Scripts\Activate.ps1
python .\python-analysis\simulate_experiment.py
```

Salidas esperadas:
- `data/results/exp_local_demo/prep/` archivos `X_train/X_test/y_train/y_test`.
- `data/results/exp_local_demo/models/` modelos `rf.pkl` y `svm.pkl`.
- `data/results/exp_local_demo/eval/confusion_matrix.csv`.
- `data/results/exp_local_demo/logs/events.jsonl` con eventos JSON línea.

## 4) Ejecución automática (script PowerShell)
Puedes usar el script `scripts/run_experiment.ps1` que:
- Verifica/instala dependencias en el venv.
- Inicia el servidor FastAPI (si no está corriendo), espera `/health`.
- Ejecuta la simulación E2E.
- Detiene el servidor al finalizar.

Uso:
```powershell
# Opción 1: Proporcionar un ID
powershell -ExecutionPolicy Bypass -File .\scripts\run_experiment.ps1 -ExperimentId exp_demo_01

# Opción 2: Sin parámetros (usa timestamp)
powershell -ExecutionPolicy Bypass -File .\scripts\run_experiment.ps1
```

## 5) Verificación de reproducibilidad
- Verificar hash del dataset crudo:
```powershell
Get-FileHash -Algorithm SHA256 .\data\raw\synthetic_classification.csv
```
Comparar con `data/raw/synthetic_classification.meta.json` → `hash_sha256`.

- Versiones de librerías (dentro del venv):
```powershell
python -c "import sklearn, psutil, fastapi; import sys; print(sys.version); print(sklearn.__version__, psutil.__version__, fastapi.__version__)"
```

## 6) Métricas y trazabilidad
- `train_metrics`: tiempo (ms), CPU promedio (%), pico de memoria (MB). Energía queda como TODO (requiere potencia promedio del hardware o medición externa).
- Logs estructurados en `data/results/<exp>/logs/events.jsonl` con campos `timestamp`, `experimentId`, `event` y payloads.
- Artefactos versionados con hash (modelos `.pkl`).

## 7) Repeticiones y control estadístico
- Ejecutar el script varias veces cambiando `-ExperimentId` para generar carpetas separadas.
- Consolidar métricas en un CSV/JSON de análisis (se recomienda crear un script de agregación en Fase 2).
- Para comparaciones centralizado vs SMA, conservar el mismo `dataset`, `semillas` y `config`.

## 8) Limpieza
- Para borrar resultados de una corrida: eliminar `data/results/<experimentId>/`.
- El venv puede removerse eliminando `.venv/` (requerirá reinstalar dependencias después).

## 9) Notas
- Todos los tiempos en UTC ISO-8601.
- El API usa puerto `127.0.0.1:8000`; ajusta si está ocupado.
- Este runbook cubre una simulación E2E sin JADE; la integración con JADE vendrá en la siguiente etapa.
