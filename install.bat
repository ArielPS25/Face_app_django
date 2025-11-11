@echo off
echo ===============================================
echo 🚀 INSTALADOR DJANGO FACE RECOGNITION SYSTEM
echo ===============================================

echo 🔍 Verificando Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo 📝 Instala Python 3.8-3.11 desde https://python.org
    pause
    exit /b 1
)

echo.
echo 📁 Creando entorno virtual...
if exist .venv (
    echo ⚠️  El entorno virtual ya existe
) else (
    python -m venv .venv
    echo ✅ Entorno virtual creado
)

echo.
echo 🔌 Activando entorno virtual...
call .venv\Scripts\activate.bat

echo.
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

echo.
echo 📋 Instalando dependencias básicas...
pip install cmake wheel setuptools

echo.
echo 🎯 Instalando requirements...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Hubo errores en la instalación
    echo 🔧 Intentando instalación alternativa para dlib...
    
    echo 📥 Instalando dlib por separado...
    pip install dlib==19.24.0
    
    echo 📥 Reintentando requirements...
    pip install -r requirements.txt
)

echo.
echo 🗄️  Configurando base de datos...
python manage.py migrate

echo.
echo 👤 ¿Quieres crear un superusuario? (s/n)
set /p create_user=
if /i "%create_user%"=="s" (
    python manage.py createsuperuser
)

echo.
echo ===============================================
echo ✅ INSTALACIÓN COMPLETADA
echo ===============================================
echo.
echo 📝 Comandos útiles:
echo    Activar entorno: .venv\Scripts\activate
echo    Ejecutar servidor: python manage.py runserver
echo    Panel admin: http://127.0.0.1:8000/admin/
echo.
echo 🎉 ¡Tu sistema está listo!
echo.
pause