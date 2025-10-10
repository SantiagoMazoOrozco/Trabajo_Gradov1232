# Puente de integración con JADE (CLI)

Este documento describe cómo integrar la arquitectura SMA (en JADE o plataforma similar) con el API experimental basado en FastAPI mediante un CLI simple (`python-analysis/agent_cli.py`).

## Idea general

- Los agentes JADE pueden lanzar procesos externos (por ejemplo, con `java.lang.ProcessBuilder`) y comunicar parámetros por argumentos o por archivos JSON.
- `agent_cli.py` actúa como un puente: recibe parámetros, llama al API REST (`/preprocess`, `/train`, `/evaluate`) y devuelve JSON por stdout y opcionalmente a archivos (`--out`).
- Esto evita acoplar Java↔Python directamente y facilita pruebas y depuración aisladas.

## Requisitos previos

- API corriendo localmente: `http://127.0.0.1:8000` (o ajuste `API_BASE`)
- Entorno: Python 3.11 con dependencias de `requirements.txt`.

## Comandos disponibles

- Preprocesamiento
  - Invoca `/preprocess` con `dataRef` y `prepConfig`.
  - Ejemplo (PowerShell):

```powershell
python python-analysis/agent_cli.py preprocess `
  --experiment-id exp_demo `
  --data data/raw/synthetic_classification.csv `
  --scale true --test-size 0.2 --seed 42 `
  --out prepRef.json
```

- Entrenamiento (RF o SVM)

```powershell
python python-analysis/agent_cli.py train `
  --experiment-id exp_demo --algo RF --seed 42 `
  --prep-ref-file prepRef.json `
  --out train_rf.json
```

- Evaluación

```powershell
python python-analysis/agent_cli.py evaluate `
  --experiment-id exp_demo `
  --model-ref-file train_rf.json `
  --metrics accuracy f1 `
  --confusion-matrix true `
  --out eval_rf.json
```

Notas:
- `--payload-file` permite pasar la solicitud completa desde un JSON, si desea un control total desde JADE.
- La salida `--out` guarda solo la parte útil: `prepRef`, `{modelRef, train_metrics}` o `eval_metrics`.

## Integración desde JADE (pseudo-código)

```java
Process p = new ProcessBuilder(
  "python", "python-analysis/agent_cli.py", "train",
  "--experiment-id", expId,
  "--algo", "RF",
  "--prep-ref-file", "prepRef.json",
  "--out", "train_rf.json"
).inheritIO().start();
int code = p.waitFor();
if (code != 0) { /* manejar error */ }
// Leer train_rf.json y continuar flujo
```

## Buenas prácticas
- Utilizar `--conversation-id` para correlacionar llamadas con mensajes ACL.
- Ajustar `API_BASE` por agente o por entorno si el API vive en otra máquina/puerto.
- Mantener `meta.json` por experimento con `group` (control|treatment) para agregación posterior.
- Registrar eventos en `events.jsonl` si se orquesta desde Java, siguiendo los nombres actuales (PREPROCESS_START, RETRY_*, FAILURE_*, *_DONE, etc.).

## Relación con documentación
- `docs/experiments.md` incluye el flujo general de ejecución; aquí se muestra el modo CLI específico para integración con JADE.
