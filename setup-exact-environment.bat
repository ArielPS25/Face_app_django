@echo off
REM Script para replicar el entorno de desarrollo que funciona
REM Usar Python 3.11.9 (NO 3.13 - causa conflictos)

echo ================================================
echo CONFIGURACION DEL ENTORNO DJANGO FACE RECOGNITION
echo ================================================
echo.
echo IMPORTANTE: Este proyecto requiere Python 3.11.9
echo Python 3.13 NO es compatible y causa conflictos
echo.

REM Verificar version de Python
python --version | findstr "3.11" >nul
if errorlevel 1 (
    echo ERROR: Se requiere Python 3.11.x
    echo Tu version actual es:
    python --version
    echo.
    echo Por favor instala Python 3.11.9 desde: https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

echo ✓ Python 3.11 detectado correctamente
echo.

REM Crear entorno virtual
echo Creando entorno virtual...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo ✓ Entorno virtual creado
echo.

REM Activar entorno virtual y instalar dependencias
echo Instalando dependencias exactas...
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements-working.txt

if errorlevel 1 (
    echo ERROR: Fallo en la instalacion de dependencias
    echo Intentando instalacion alternativa...
    .\.venv\Scripts\pip.exe install dlib-20.0.0-cp311-cp311-win_amd64.whl
    .\.venv\Scripts\pip.exe install -r requirements-working.txt
)

echo.
echo ================================================
echo INSTALACION COMPLETADA
echo ================================================
echo.
echo Para activar el entorno virtual:
echo .\.venv\Scripts\Activate.ps1
echo.
echo Para ejecutar el servidor:
echo .\.venv\Scripts\python.exe manage.py runserver
echo.
echo Versiones instaladas:
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -c "import django; print(f'Django {django.__version__}')"
.\.venv\Scripts\python.exe -c "import cv2; print(f'OpenCV {cv2.__version__}')"

pause