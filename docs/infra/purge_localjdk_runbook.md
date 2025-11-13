# Runbook: Purga de `.localjdk` del historial Git

Este procedimiento reescribe el historial para eliminar el directorio `.localjdk/` y sus contenidos. Úsalo solo si estás seguro; requiere force-push y coordinación con colaboradores.

## 0) Preparación
- Verifica que `.gitignore` ya excluye `.localjdk/` (sí, está configurado).
- Asegura que tu working tree esté limpio o stashea cambios.
- Haz un backup/clon temporal por seguridad.

## 1) Opción preferida: `git filter-repo`
Instala `git-filter-repo` (si no lo tienes):
```bash
pipx install git-filter-repo || pip install --user git-filter-repo
```
Ejecuta la purga (en la raíz del repo):
```bash
git filter-repo --force --invert-paths --path .localjdk --path-glob '.localjdk/**'
```
Opcional: compacta y repara referencias:
```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```
Publica los cambios:
```bash
git push --force-with-lease origin main
```

## 2) Fallback: `git filter-branch` (más lento, legacy)
```bash
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch .localjdk || true' \
  --prune-empty --tag-name-filter cat -- --all

git reflog expire --expire=now --all
git gc --prune=now --aggressive

git push --force-with-lease origin --all
git push --force-with-lease origin --tags
```

## 3) Post-purga: pasos para colaboradores
- PR de anuncio con link a este runbook.
- Cada colaborador debe re-clonar o resetear:
```bash
git fetch --all
# Si no hay commits propios locales:
git reset --hard origin/main
# Recomendado: hacer un clon nuevo en una carpeta limpia
```

## 4) Verificación
- Confirmar que `.localjdk` no aparece:
```bash
git log -- .localjdk || echo "sin referencias"
```
- Revisión del tamaño del repo (`git count-objects -vH`).

## 5) Notas
- Evitar añadir toolchains locales al repo; se ignoran en `.gitignore` (`.localjdk/`, `.localmaven/`, `.localtmp/`).
- Si el repo usa protecciones de branch, coordina con un administrador para permitir el force-push temporal.

---
Última actualización: 2025-11-11
