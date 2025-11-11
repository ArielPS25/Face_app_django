@echo off
echo ===============================================
echo 📁 ACTIVANDO CONFIGURACIÓN SQLITE
echo ===============================================

REM Limpiar variables de entorno de MySQL
set USE_MYSQL=false
set MYSQL_DATABASE=
set MYSQL_USER=
set MYSQL_PASSWORD=
set MYSQL_HOST=
set MYSQL_PORT=

echo ✅ Variables de entorno configuradas para SQLite
echo    - Usando base de datos local: db.sqlite3
echo.
echo 📝 Ahora ejecuta: python manage.py runserver
echo    Django se conectará automáticamente a SQLite local
echo.
pause