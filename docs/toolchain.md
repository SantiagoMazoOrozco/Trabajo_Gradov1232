# Toolchain y Versionado

## Objetivo
Definir versiones fijas de herramientas para garantizar reproducibilidad experimental.

## Versiones Objetivo
| Herramienta | Versión | Comando Verificación |
|-------------|---------|----------------------|
| JDK | 17.x | `java -version` |
| JADE | 4.5.x | (Descarga jar y ejecutar) |
| Python | 3.11.x | `python --version` |
| scikit-learn | 1.5.1 | `python -c "import sklearn, sys; print(sklearn.__version__)"` |
| psutil | 5.9.8 | `python -c "import psutil; print(psutil.__version__)"` |

## Instalación (Windows PowerShell)
```powershell
# Python 3.11 si no está instalado (usar instalador oficial y agregar a PATH)
python --version

# Crear entorno virtual
python -m venv .venv
./.venv/Scripts/Activate.ps1

# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del ML
pip install -r requirements.txt

# Verificar
python -c "import sklearn, psutil; print(sklearn.__version__, psutil.__version__)"
```

## JADE
1. Descargar JADE (zip) desde: http://jade.tilab.com/ (si no está disponible usar mirror GitHub). 
2. Colocar `jade.jar` en una carpeta (por ejemplo `jade-platform/lib/`).
3. Añadir al classpath en futuros scripts/launchers.

Ejemplo futuro (no ejecutar aún):
```powershell
java -cp .;lib\jade.jar jade.Boot -gui
```

## Política de Cambios
- Cualquier cambio de versión requiere actualizar esta tabla y crear un nuevo tag Git.
- Ensayos comparativos deben indicar la versión exacta (copiar salida de comandos de verificación a logs si es crítico).

## Hardware / Ambiente
- Sistema operativo: Windows (documentar versión).
- Recomendación: Registrar CPU logical cores y RAM con script psutil al inicio de cada experimento.

## Captura de Configuración (Ejemplo JSON para logs)
```json
{
  "python_version": "3.11.6",
  "jdk_version": "17.0.10",
  "sklearn_version": "1.5.1",
  "psutil_version": "5.9.8",
  "logical_cores": 8,
  "ram_gb": 16
}
```
