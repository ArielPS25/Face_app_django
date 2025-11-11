@echo off
echo ===============================================
echo 🚀 ACTIVANDO CONFIGURACIÓN MYSQL
echo ===============================================

REM Configurar variables de entorno para MySQL
set USE_MYSQL=true
set MYSQL_DATABASE=nandu
set MYSQL_USER=admin
set MYSQL_PASSWORD=admin123
set MYSQL_HOST=nandu.czmoey4oapii.sa-east-1.rds.amazonaws.com
set MYSQL_PORT=3306

echo ✅ Variables de entorno configuradas para MySQL:
echo    - Base de datos: %MYSQL_DATABASE%
echo    - Usuario: %MYSQL_USER%
echo    - Host: %MYSQL_HOST%
echo    - Puerto: %MYSQL_PORT%

echo.
echo 📝 Ahora ejecuta: python manage.py runserver
echo    Django se conectará automáticamente a MySQL RDS
echo.
echo ⚠️  IMPORTANTE: Mantén esta ventana abierta mientras uses MySQL
pause