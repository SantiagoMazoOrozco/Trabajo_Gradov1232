# CI/CD Pipeline Outline (GitHub Actions)

## Objetivo
Automatizar validaciones, ejecución de experimentos de smoke, generación de figuras y construcción del PDF de la tesis.

## Jobs propuestos
1. `lint-and-test` (Python)
   - Setup Python 3.11
   - pip install -r requirements.txt
   - flake8/ruff opcional, pytest si hay tests
2. `smoke-experiments`
   - Ejecutar `scripts/run_batch.sh` con repeticiones bajas (e.g., 2 por grupo)
   - `python python-analysis/aggregate_metrics.py`
   - `python python-analysis/stats_analysis.py`
   - Subir `data/results/aggregate_metrics.csv` y `stats_summary.md` como artifacts
3. `generate-figures`
   - `python python-analysis/generate_thesis_figures.py --input data/results/aggregate_metrics.csv --out docs/figures`
   - Subir `docs/figures/*.png` como artifacts
4. `build-thesis-pdf`
   - Instalar TeX Live (caché recomendado)
   - `pdflatex docs/plantilla_trabajo_grado_filled.tex` (2 pasadas)
   - Publicar PDF como artifact

## Gatillos
- `on: [push, pull_request]` a ramas `main` y `thesis/*`
- Manual dispatch para `build-thesis-pdf`

## Secrets / Consideraciones
- Si se usa JADE real, el job requiere JDK y Maven (setup-java action) y más tiempo.
- En runners Linux, `/sys/class/powercap` no estará disponible; mantener pruebas con proxy energético.
- Limitar duración del smoke para no exceder minutos del runner.

## YAML de ejemplo (resumen)
```yaml
name: ci
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: echo "(opcional) ejecutar linters/tests"

  smoke-experiments:
    runs-on: ubuntu-latest
    needs: lint-and-test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: bash scripts/run_batch.sh
      - run: python python-analysis/aggregate_metrics.py
      - run: python python-analysis/stats_analysis.py
      - uses: actions/upload-artifact@v4
        with:
          name: results
          path: |
            data/results/aggregate_metrics.csv
            data/results/stats_summary.md

  generate-figures:
    runs-on: ubuntu-latest
    needs: smoke-experiments
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python python-analysis/generate_thesis_figures.py --input data/results/aggregate_metrics.csv --out docs/figures
      - uses: actions/upload-artifact@v4
        with:
          name: figures
          path: docs/figures/*.png

  build-thesis-pdf:
    runs-on: ubuntu-latest
    needs: generate-figures
    steps:
      - uses: actions/checkout@v4
      - name: Install TeX Live
        run: sudo apt-get update && sudo apt-get install -y texlive-latex-recommended texlive-fonts-recommended texlive-latex-extra
      - run: pdflatex -interaction=nonstopmode docs/plantilla_trabajo_grado_filled.tex
      - run: pdflatex -interaction=nonstopmode docs/plantilla_trabajo_grado_filled.tex
      - uses: actions/upload-artifact@v4
        with:
          name: thesis-pdf
          path: docs/plantilla_trabajo_grado_filled.pdf
```

## Notas
- Añadir caché para TeX Live si el tiempo es un problema (actions/cache).
- Si se requiere JADE: `actions/setup-java@v4` y Maven 3.9.x; instalar jade jar local si fuera necesario.
- Ajustar rutas si el workspace del runner cambia.

Última actualización: 2025-11-11
