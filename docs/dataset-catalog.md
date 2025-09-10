# Catálogo de Datasets

| Nombre | Archivo | Tipo | Fuente / Generador | Hash (SHA-256) | Filas | Columnas | Notas |
|--------|---------|------|--------------------|----------------|-------|----------|-------|
| (pendiente) | (pendiente) | sintético/público | sklearn.make_classification / URL | (pendiente) | - | - | Inicial |

## Procedimiento de Registro
1. Colocar archivo crudo en `data/raw/`.
2. Generar metadatos `.meta.json` con: name, source/generator, params, rows, cols, created_utc, hash_sha256.
3. Añadir fila a la tabla con la información.
4. No modificar el CSV una vez registrado; cualquier cambio => nuevo nombre.

## Ejemplo de Metadatos (`.meta.json`)
```json
{
  "name": "synthetic_classification",
  "generator": "sklearn.make_classification",
  "params": {"n_samples":3000, "n_features":20, "n_informative":8},
  "rows": 3000,
  "cols": 21,
  "hash_sha256": "<hash>",
  "created_utc": "2025-09-09T10:00:00Z"
}
```
