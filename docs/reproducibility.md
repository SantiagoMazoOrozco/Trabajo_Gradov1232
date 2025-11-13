# Reproducibilidad de Experimentos SMA

Este documento resume pasos exactos para recrear los resultados publicados (batch 20251027) y generar nuevas réplicas.

## 1. Entorno

Requisitos mínimos:
- Python 3.11 o superior
- JDK 21 (para ejecución JADE) *(opcional si solo se usan endpoints stub)*
- Maven 3.9.x (para compilar JADE si se modifica código Java)

### 1.1 Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 1.2 Variables opcionales
```bash
export CPU_POWER_W=65   # Ajuste según TDP CPU real
```

## 2. Estructura de Datos

Dataset sintético congelado: `data/raw/synthetic_classification.csv` (metadatos en `synthetic_classification.meta.json`). No modificar para mantener comparabilidad. Para escalar: ver `docs/dataset_scaling_plan.md`.

## 3. Ejecución de un Experimento Individual
```bash
bash scripts/run_experiment.sh   # Variante bash (control/treatment definido internamente o por parámetros)
# PowerShell (Windows): scripts/run_experiment.ps1 -Group control -Report -Monitored -MonitorSeconds 120 -Seed 42
```
Artefactos generados: `data/results/<experimentId>/` con subcarpetas `prep/`, `models/`, `eval/`, `monitor/`, `report/` y `meta.json`.

## 4. Ejecución de Lote (Control vs Treatment)
```bash
bash scripts/run_batch.sh            # Lote estándar; ajusta repeticiones dentro del script
# PowerShell: scripts/run_batch.ps1 -Repeats 10 -MonitorSeconds 60
```
Resultados en carpetas `batch_YYYYMMDD_HHMMSS_*` y comprimidos en `evidence_batch_YYYYMMDD_HHMMSS.zip`.

## 5. Agregación de Métricas
```bash
python python-analysis/aggregate_metrics.py
```
Salida: `data/results/aggregate_metrics.csv`

## 6. Análisis Estadístico
```bash
python python-analysis/stats_analysis.py
```
Salida: `data/results/stats_summary.json` y `data/results/stats_summary.md`.

## 7. Regeneración de Figuras (Tesis)
```bash
python python-analysis/generate_thesis_figures.py --input data/results/aggregate_metrics.csv --out docs/figures
```
Figuras: tiempo, energía/MB, registros/s por algoritmo y grupo.

## 8. Construcción del Documento LaTeX
```bash
# Requiere TeX Live instalado
pdflatex -interaction=nonstopmode docs/plantilla_trabajo_grado_filled.tex
pdflatex -interaction=nonstopmode docs/plantilla_trabajo_grado_filled.tex  # Segunda pasada para TOC
```

## 9. Versionado y Hash de Evidencia
Para garantizar integridad, registrar el hash del CSV agregado:
```bash
sha256sum data/results/aggregate_metrics.csv > data/results/aggregate_metrics.sha256
git add data/results/aggregate_metrics.sha256
```

## 10. Semillas y Determinismo
- Semilla primaria definida en script batch (ej. `SeedBase 42`).
- Cada repetición puede derivar una semilla distinta: `seed = base + réplica`.
- Registrar semillas en `meta.json` por experimento.

## 11. Validación Post-Ejecución
Checklist:
- `aggregate_metrics.csv` no vacío y contiene filas TRAIN_* y EVAL_*.
- `stats_summary.json` incluye p-values para métricas clave.
- Figuras generadas presentes y legibles.
- Documento PDF compila sin errores (margen, TOC, figuras referenciadas).

## 12. Escalamiento (Opcional)
Ver plan en `docs/dataset_scaling_plan.md` para generar dataset > 30k registros y evaluar impacto en métricas.

## 13. Dependencias Críticas
| Paquete | Uso |
|---------|-----|
| fastapi | API experimental / dashboard |
| psutil | Métricas de CPU/memoria |
| pandas | Manipulación de resultados |
| scikit-learn | Modelos RF/SVM (si se activan versiones reales) |
| prometheus-client | Exposición métricas adicionales |
| matplotlib | Generación de figuras |

## 14. Buenas Prácticas
- No editar manualmente `aggregate_metrics.csv`; regenerar siempre.
- Usar ramas para cambios experimentales y fusionar solo resultados verificados.
- Documentar hardware (CPU modelo, núcleos, frecuencia) en secciones futuras.

## 15. Contacto / Mantenimiento
Mantener este archivo actualizado si cambian scripts, rutas o parámetros críticos.

---
Última actualización: 2025-11-11
