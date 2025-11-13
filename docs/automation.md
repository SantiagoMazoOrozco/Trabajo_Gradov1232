# Automatización de índices diarios de documentación

Este proyecto incluye un script de PowerShell para generar carpetas por fecha bajo `docs/YYYY-MM-DD`, crear un `index.md` por día, un `daily-log-YYYY-MM-DD.md` opcional, y actualizar el índice maestro `docs/INDEX_BY_DATE.md`.

## Script

- Ruta: `scripts/generate_daily_docs.ps1`
- Requisitos: Git disponible en PATH.

### Uso básico

- Generar para hoy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate_daily_docs.ps1
```

- Generar para una fecha específica:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate_daily_docs.ps1 -Date "2025-09-18"
```

- Generar para un rango de fechas (incluye extremos):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/generate_daily_docs.ps1 -StartDate "2025-09-10" -EndDate "2025-09-18"
```

### Opciones

- `-NoDailyLog`: No crear `daily-log-YYYY-MM-DD.md`.
- `-DryRun`: Muestra acciones sin escribir archivos.
- `-CopyDocs`: Copia archivos cambiados de `docs/` al folder del día (omite `docs/YYYY-MM-DD/*` y `docs/INDEX_BY_DATE.md`). Útil para snapshots diarios.

### ¿Qué hace exactamente?

1. Usa `git log` para la(s) fecha(s) dada(s) y parsea los commits y archivos cambiados.
2. Crea `docs/YYYY-MM-DD/` si no existe.
3. (Opcional) Copia archivos de `docs/` modificados ese día al folder del día (`-CopyDocs`).
4. Escribe `docs/YYYY-MM-DD/index.md` con enlaces relativos a docs y a código tocado ese día.
5. Escribe `docs/YYYY-MM-DD/daily-log-YYYY-MM-DD.md` con resumen de commits (a menos que se pase `-NoDailyLog`).
6. Actualiza `docs/INDEX_BY_DATE.md` con enlaces en formato Markdown.

### Tareas en VS Code

Hay dos tareas definidas en `.vscode/tasks.json`:

- "Docs: Generate daily indices (today)": Ejecuta para la fecha actual.
- "Docs: Generate daily indices (range)": Solicita fecha inicial y final y ejecuta en rango.

Para ejecutarlas, abre la paleta de comandos (Ctrl+Shift+P) y corre "Tasks: Run Task".

### Notas

- Los enlaces en `index.md` ahora son Markdown con texto amigable (nombre de archivo) y rutas relativas correctas.
- El índice maestro usa enlaces Markdown `[YYYY-MM-DD](docs/YYYY-MM-DD/index.md)`.
- El script es idempotente: volver a ejecutar sobre la misma fecha sobrescribe los archivos del día de forma controlada.
