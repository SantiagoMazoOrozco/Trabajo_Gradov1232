# Catálogo de Datasets

| Nombre | Archivo | Tipo | Fuente / Generador | Hash (SHA-256) | Filas | Columnas | Notas |
|--------|---------|------|--------------------|----------------|-------|----------|-------|
| synthetic_classification | synthetic_classification.csv | sintético | sklearn.make_classification | 9969bedfaea6d914479d46de9abb98d96d4ba9e1a635e9d9606834ca094ed57a | 3000 | 21 | Dataset inicial |

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
