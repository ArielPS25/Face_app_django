#!/usr/bin/env python3
"""
Script para actualizar configuración de Django para MySQL
Genera configuración automática para settings.py
"""

def generate_mysql_settings():
    """Genera la configuración MySQL para Django"""
    
    mysql_config = """
# =============================================
# CONFIGURACIÓN MYSQL PARA DJANGO
# Reemplazar la sección DATABASES en settings.py
# =============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'face_attendance_db',
        'USER': 'tu_usuario_mysql',
        'PASSWORD': 'tu_password_mysql',
        'HOST': 'localhost',  # O tu host MySQL
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# =============================================
# CONFIGURACIÓN PARA AWS RDS (Opcional)
# =============================================
"""
    
    aws_rds_config = """
# Para AWS RDS MySQL:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'face_attendance_db',
        'USER': 'tu_usuario_rds',
        'PASSWORD': 'tu_password_rds',
        'HOST': 'tu-instancia.xxxxxxx.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'ssl': {'ssl-disabled': False},
        },
    }
}
"""

    requirements_addition = """
# =============================================
# AGREGAR A requirements.txt
# =============================================
mysqlclient>=2.2.0
# o alternativamente:
# PyMySQL>=1.0.0
"""

    commands = """
# =============================================
# COMANDOS PARA INSTALAR MYSQL CLIENT
# =============================================

# Opción 1: mysqlclient (recomendado)
pip install mysqlclient

# Opción 2: PyMySQL (si mysqlclient da problemas)
pip install PyMySQL

# Si usas PyMySQL, agregar en settings.py:
import pymysql
pymysql.install_as_MySQLdb()

# =============================================
# COMANDOS MYSQL PARA CREAR BASE DE DATOS
# =============================================

# 1. Conectar a MySQL:
mysql -u root -p

# 2. Crear base de datos:
CREATE DATABASE face_attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 3. Crear usuario (opcional):
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'tu_password_seguro';
GRANT ALL PRIVILEGES ON face_attendance_db.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;

# 4. Importar el dump:
mysql -u django_user -p face_attendance_db < dump_mysql.sql

# =============================================
# VERIFICAR MIGRACIÓN EN DJANGO
# =============================================

# 1. Probar conexión:
python manage.py dbshell

# 2. Ver tablas:
python manage.py inspectdb

# 3. Si hay problemas, generar nuevas migraciones:
python manage.py makemigrations --empty attendance
python manage.py migrate --fake-initial
"""
    
    # Escribir archivos de configuración
    with open('mysql_django_config.txt', 'w', encoding='utf-8') as f:
        f.write(mysql_config)
        f.write(aws_rds_config)
        f.write(requirements_addition)
        f.write(commands)
    
    print("📄 Archivo de configuración generado: mysql_django_config.txt")
    print("\n✅ CONFIGURACIÓN MYSQL LISTA")
    print("="*50)
    print("1. Instalar: pip install mysqlclient")
    print("2. Crear BD: CREATE DATABASE face_attendance_db;")
    print("3. Importar: mysql -u usuario -p face_attendance_db < dump_mysql.sql")
    print("4. Actualizar DATABASES en settings.py")
    print("5. Probar: python manage.py dbshell")

if __name__ == "__main__":
    generate_mysql_settings()