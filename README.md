# Cómo iniciar (Quick Start)
## Ejemplo de uso
Para iniciar el sistema, puedes usar los siguientes comandos:
./start.sh --seed

# forzar modo local y sembrar experimento
./start.sh --local --seed

# script de demostración (start + seed + abre navegador si posible)
./demo.sh

# detener todo (compose y/o uvicorn en background)
./stop.sh

```
# Plataforma SMA para Orquestación de Experimentos de ML

## Inicio rápido (visual)

Para una guía paso a paso con diagramas y ejemplos prácticos (comandos y enlaces listos para usar), consulta:

- docs/guia_visual_grafana.md — cómo arrancar la pila, ver CPU/RAM/Watts y usar el modo Live en Grafana.
- docs/como_correr_experimentos.md — cómo lanzar experimentos (control/treatment), usar seeds, ejecutar batch, agregar métricas y análisis estadístico.

Estas guías incluyen capturas/diagramas (Mermaid), snippets de curl/bash y resolución de problemas.

## Resumen
Repositorio del trabajo de grado: construcción de una plataforma basada en Agentes (JADE) que orquesta un pipeline de Machine Learning (ingesta → preprocesamiento → entrenamiento → evaluación → métricas → exportación) con posibilidad de experimentación controlada.

## Trabajo de Grado: Macroproceso
- Documento de mapeo y cumplimiento: `docs/macroprocess_mapping.md` (guía principal para auditar y defender el trabajo)

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
| JDK         | 21.x (LTS)       | Requerido por JADE; instalado localmente (ver nota técnica en docs/Macroproceso.txt) |
| JADE        | 4.6.0            | Middleware multi-agente (jar instalado manualmente en Maven local) |
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
- Plan de reestructuración (estructura objetivo y fases): `docs/RESTRUCTURE_PLAN.md`
- Archivo cronológico (anotaciones por fecha): `docs/INDEX_BY_DATE.md` (referencia histórica)
- Automatización de índices diarios: `docs/automation.md`
- Plan de integración con BAF: `docs/baf_integration_plan.md`
 - Guía de experimentos (ejecución y análisis): `docs/experiments.md`

Atajo automático (PowerShell):
```
powershell -ExecutionPolicy Bypass -File .\scripts\run_experiment.ps1 -ExperimentId exp_demo_01
```
uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --log-level warning
```

En otra terminal:
```
.\.venv\Scripts\Activate.ps1
python .\python-analysis\simulate_experiment.py
```

Resultados esperados en `data/results/<experimentId>/` (prep, models, eval, logs).

## Preparación para monitoreo y contenedores
Previo a instrumentar con Prometheus/Grafana y contenerizar, se está reorganizando el repo para una estructura más clara.


 ## Ejecutar Pipeline de Experimentos
 ### Dashboard y Monitoreo (Prometheus + Grafana)

 Se añadió una pila ligera de monitoreo en `infra/compose/`.

 Componentes:
 - `prometheus` (escucha en `:9090`)
 - `grafana` (escucha en `:3000`, credenciales por defecto `admin/admin`)
 - Backend FastAPI local (puerto dinámico 8000..8010) descubierto desde `data/results/_server_state/uvicorn_dashboard.json`.

 Prometheus usa `file_sd` leyendo `data/results/_server_state/prom_targets.json` generado por `scripts/start_stack.sh`. En Linux se resuelve el host mediante la IP de `docker0` (ej. `172.17.0.1`).

 Pasos para levantar todo:
 ```bash
 # En la raíz del repositorio
 bash scripts/start_stack.sh --build

 # Ver puerto backend elegido
 jq -r .port data/results/_server_state/uvicorn_dashboard.json

 # Probar health y metrics
 PORT=$(jq -r .port data/results/_server_state/uvicorn_dashboard.json)
 curl -fsS http://127.0.0.1:$PORT/health
 curl -fsS http://127.0.0.1:$PORT/metrics | head

 # Acceder a Grafana
 # http://localhost:3000  (usuario: admin / contraseña: admin)
 ```

 Dashboard inicial autoprovisionado: "SMA Overview" (accuracy, F1, duración de entrenamiento). Para poblar métricas actualizadas ejecuta uno o más experimentos:
 ```bash
 PORT=$(jq -r .port data/results/_server_state/uvicorn_dashboard.json)
 API_PORT=$PORT bash scripts/run_experiment.sh --group control --monitor-seconds 5 --report
 API_PORT=$PORT bash scripts/run_experiment.sh --group treatment --monitor-seconds 5 --report

 # Re‑agregar y recalcular estadísticas
 bash scripts/aggregate_metrics.sh
 bash scripts/stats_analysis.sh
 ```

 Si `eval_accuracy` aparece vacío en Prometheus inmediatamente después de iniciar, ejecuta al menos un experimento para que la serie se exponga (el endpoint `/metrics` publica valores en función de los datos agregados disponibles).

 Apagar la pila:
 ```bash
 docker compose -f infra/compose/docker-compose.yml down
 ```

 Regenerar sin reconstruir imágenes:
 ```bash
 bash scripts/start_stack.sh
 ```

### Modo aislado (recomendado para mediciones estables)

Levanta backend, Prometheus y Grafana en contenedores con límites de CPU/Mem y publica el backend en un puerto libre del host:

```bash
bash scripts/start_stack.sh --build --isolated
```

Tras arrancar verás una línea como:

```
Stack started (isolated). Services: backend:8004 (container published), prometheus:9090, grafana:3000
```

Además, el puerto publicado queda en:

```
cat data/results/_server_state/backend_host_port.txt
```

Usa ese puerto para la API Base en el dashboard (variable `apiBase`). Por defecto el dashboard provisionado ya apunta a `http://localhost:8004`. Si el puerto difiere, edítala en la parte superior del dashboard o navega directamente a:

```
http://localhost:<PUERTO>/control
```

Live (tiempo real):

```
curl "http://localhost:<PUERTO>/trigger/live-start?seconds=30"
```

Verás moverse los paneles "Live Avg Watts" y "Live Records/s" con actualización de 1s.

### Mapeo Objetivos ↔ Métricas ↔ Paneles

Esta es la correspondencia directa entre los objetivos del proyecto y lo que verás en el dashboard provisionado:

- Calidad del modelo
	- Métricas: `eval_accuracy_by_group{group=...}`, `eval_f1_by_group{group=...}`
	- Paneles: "Accuracy by Group", "F1 by Group"
- Eficiencia de entrenamiento y uso de recursos
	- Métricas: `train_cpu_avg_percent_last`, `train_mem_peak_mb_last`, `train_records_per_s_last`, `train_data_mb_per_s_last`, `train_energy_j_total_last`, `train_energy_j_per_mb_last`
	- Paneles: fila "Training Efficiency (Last Session)" (estadísticos tipo Stat)
- Resiliencia (fallos y recuperaciones)
	- Métricas: `failures_total`, `recoveries_total`, `recovery_rate` (0..1)
	- Paneles: fila "Resilience" → "Failures (total)", "Recoveries (total)", "Recovery rate (%)"
- Operatividad/Disponibilidad del servicio de métricas
	- Métricas: `up{job="app"}`, `scrape_duration_seconds{job="app"}`
	- Paneles: "Target up (app)", "Scrape duration (app)"
- Replicabilidad/volumen experimental
	- Métrica: `experiments_total`
	- Panel: "Experiments (total)"
- Eficiencia comparativa por algoritmo
	- Métricas etiquetadas por `algo`: `train_duration_seconds_last{algo}`, `train_cpu_avg_percent_last_by_algo{algo}`, `train_mem_peak_mb_last_by_algo{algo}`, `train_records_per_s_last_by_algo{algo}`, `train_energy_j_total_last_by_algo{algo}`, `train_energy_j_per_mb_last_by_algo{algo}`
	- Paneles: Fila "Training by Algorithm (Last Session)" (duración timeseries + stats CPU/Mem/Records/Energy/Energy J/MB)

Notas:
- `recovery_rate` se reporta en el rango [0..1]; el panel muestra el porcentaje (`recovery_rate * 100`).
- Si aún no hay filas `RESILIENCE` en `aggregate_metrics.csv`, `failures_total` y `recoveries_total` serán 0.
- Las series "last" (ej. `train_*_last`) reflejan la última sesión de entrenamiento encontrada en los datos agregados.
- Las series etiquetadas por algoritmo (`{algo="rf"}`, `{algo="svm"}`) se generan tomando la última fila `TRAIN_<ALGO>` disponible en el CSV agregado.
- Página principal: lista de experimentos recientes, botones de "Simular nuevo" (preprocess → train RF/SVM → evaluate) y "Refrescar", y enlaces para descargar CSV.
- Detalle de experimento: métricas de entrenamiento y evaluación, y accesos directos a artefactos (X_train/X_test, confusion matrix, eventos).
Arranque local (Linux/macOS):

```bash
Luego abre: http://127.0.0.1:8000/

Con contenedores (opcional):

```bash
cd infra/compose
docker compose up --build
```

- Backend: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin). El dashboard "SMA-ML Monitoring Overview" se autoprovisiona.
- Documentos curados: http://localhost:8000/project-docs

JADE container (agentes)
------------------------
Si quieres ejecutar la plataforma JADE como contenedor (recomendado para pruebas locales aisladas), sigue estos pasos desde la raíz del repo:

1) Construir la imagen JADE (usa el Dockerfile en `infra/docker/jade.Dockerfile`):

```bash
cd infra/compose
docker compose build jade
```

2) Levantar todo el stack (incluye `jade`, `backend`, `prometheus`, `grafana`):

```bash
docker compose up --build
```

3) Notas:
- El contenedor JADE usa `/app/data` para leer/escribir datasets y resultados; queda montado a `./data` del repo.
- Se exponen puertos 1099/7778 (ajustables) y el servicio depende del `backend` para integración con la API.
- Si la compilación falla por dependencias de Maven, revisa `agents/jade-platform/pom.xml` y asegura que el repositorio Maven tenga acceso a los artefactos (JADE 4.6.0) o instala localmente el jar.

Prueba rápida (smoke test):
```bash
bash scripts/smoke_jade.sh
```
Este script levanta solo el servicio `jade`, espera a que el healthcheck reporta `healthy` (puertos 1099/7778 abiertos) y muestra logs en caso de fallo.

Descargas:

- CSV agregado: http://localhost:8000/download/aggregate
- Artefactos por experimento: http://localhost:8000/download/experiment/<exp_id>/<ruta_relativa>
- Bundle ZIP: http://localhost:8000/download/experiment/<exp_id>/bundle

Notas:

- Si Prometheus/Grafana no están corriendo, la UI sigue funcionando y el endpoint `/metrics` tiene fallback de texto para no romper.
- Los paneles de Grafana se actualizarán a medida que se ejecuten entrenamientos/evaluaciones y existan series Prometheus.
- Para argumentación integral, revisar también `docs/presentation_guide.md` (en la sección Documentos de la UI).

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
