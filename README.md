# Plataforma SMA para Orquestación de Experimentos de ML

## Resumen
Repositorio del trabajo de grado: construcción de una plataforma basada en Agentes (JADE) que orquesta un pipeline de Machine Learning (ingesta → preprocesamiento → entrenamiento → evaluación → métricas → exportación) con posibilidad de experimentación controlada.

## Estructura
```
baseline/           # Referencias, prototipos simples o comparaciones
jade-platform/      # Código JADE (Java) de los agentes
python-analysis/    # Scripts Python (generación dataset, entrenamiento, métricas)
data/raw/           # Datasets congelados (inmutables)
data/results/       # Resultados experimentales derivados (ignorados en Git)
docs/               # Documentación (diseño, diseño experimental, toolchain)
```

## Fase 0 (Preparación) Objetivos
1. Estructura de carpetas base.
2. Definir y congelar dataset inicial (sintético o público) con hash.
3. Documentar versiones de herramientas (JDK 17, JADE, Python 3.11, scikit-learn, psutil).
4. Plantilla de diseño experimental.
5. Asegurar reproducibilidad mínima (hash + metadatos dataset).

## Toolchain (Resumen)
| Herramienta | Versión esperada | Notas |
|-------------|------------------|-------|
| JDK         | 17.x (LTS)       | Requerido por JADE |
| JADE        | 4.5.x            | Middleware multi-agente |
| Python      | 3.11.x           | Scripts ML |
| scikit-learn| 1.5.1            | Modelos ML (RF, SVM) |
| psutil      | 5.9.8            | Métricas de recursos |

Detalles en `docs/toolchain.md`.

## Dataset Inicial
Se generará (o descargará) y se almacenará en `data/raw` junto a su archivo `.meta.json` con parámetros y hash SHA-256.

## Próximas Fases (Vista rápida)
- Fase 1: Modelado de agentes (Orchestrator, DataIngestion, Preprocessing, TrainingRF, TrainingSVM, Evaluation, Metrics, Export) + protocolo de mensajes.
- Fase 2: Implementación incremental y pruebas de comunicación ACL.

## Fase 1 – Cómo ejecutar en entorno controlado
Consulta el runbook detallado en `docs/runbook_fase1.md`.

Documentos relacionados:
- Arquitectura: `docs/architecture.md`
- Protocolo de mensajes: `docs/message-protocol.md`
- Metodología: `docs/methodology.md`
- Índice por fecha de documentación: `docs/INDEX_BY_DATE.md`

Atajo automático (PowerShell):
```
powershell -ExecutionPolicy Bypass -File .\scripts\run_experiment.ps1 -ExperimentId exp_demo_01
```

Manual (dos terminales):
```
.\.venv\Scripts\Activate.ps1
uvicorn python-analysis.api.main:app --host 127.0.0.1 --port 8000 --log-level warning
```

En otra terminal:
```
.\.venv\Scripts\Activate.ps1
python .\python-analysis\simulate_experiment.py
```

Resultados esperados en `data/results/<experimentId>/` (prep, models, eval, logs).

## Reproducir Entorno Python
(Ver también `requirements.txt` y `docs/toolchain.md`)
```
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Verificación Hash Dataset
```
Get-FileHash -Algorithm SHA256 data/raw/synthetic_classification.csv
```
Comparar con campo `hash_sha256` en `data/raw/synthetic_classification.meta.json`.

## Licencia
Uso académico.
