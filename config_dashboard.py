#!/usr/bin/env python3
"""
Dashboard de Configuración del Sistema Django Face Recognition
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_attendance_system.settings')
django.setup()

from django.conf import settings
from django.db import connection
from attendance.models import Person, PersonImage, Course, AttendanceRecord

def print_header(title):
    print("\n" + "=" * 70)
    print(f"🔍 {title}")
    print("=" * 70)

def show_environment_vars():
    print_header("VARIABLES DE ENTORNO")
    env_vars = [
        'USE_MYSQL', 'MYSQL_DATABASE', 'MYSQL_USER', 
        'MYSQL_PASSWORD', 'MYSQL_HOST', 'MYSQL_PORT'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'No configurado')
        if 'PASSWORD' in var and value != 'No configurado':
            value = '*' * len(value)
        print(f"   {var:15} : {value}")

def show_django_config():
    print_header("CONFIGURACIÓN DJANGO")
    
    print(f"   🐍 Python Version   : {sys.version.split()[0]}")
    print(f"   🎯 Django Version   : {django.get_version()}")
    print(f"   🔧 Debug Mode       : {settings.DEBUG}")
    print(f"   🌐 Allowed Hosts    : {settings.ALLOWED_HOSTS}")
    print(f"   📁 Base Directory   : {settings.BASE_DIR}")
    print(f"   🔐 Secret Key       : {'*' * 10}...{settings.SECRET_KEY[-6:]}")

def show_database_config():
    print_header("CONFIGURACIÓN DE BASE DE DATOS")
    
    db_config = settings.DATABASES['default']
    engine = db_config['ENGINE']
    
    print(f"   🗄️  Motor de BD      : {engine}")
    
    if 'mysql' in engine:
        print(f"   📊 Tipo             : MySQL")
        print(f"   📂 Base de Datos    : {db_config['NAME']}")
        print(f"   👤 Usuario          : {db_config['USER']}")
        print(f"   🔑 Contraseña       : {'*' * len(db_config['PASSWORD'])}")
        print(f"   🌐 Host             : {db_config['HOST']}")
        print(f"   🚪 Puerto           : {db_config['PORT']}")
        print(f"   ⚙️  Opciones        : {db_config.get('OPTIONS', {})}")
        
        # Probar conexión
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"   ✅ Estado          : Conectado")
            print(f"   📋 Versión MySQL   : {version}")
            print(f"   🏷️  BD Actual       : {current_db}")
            print(f"   📊 Tablas          : {len(tables)} tablas")
            
        except Exception as e:
            print(f"   ❌ Estado          : Error - {e}")
            
    elif 'sqlite' in engine:
        print(f"   📊 Tipo             : SQLite")
        print(f"   📁 Archivo          : {db_config['NAME']}")
        
        if os.path.exists(db_config['NAME']):
            size = os.path.getsize(db_config['NAME']) / (1024 * 1024)
            print(f"   📏 Tamaño          : {size:.2f} MB")
            print(f"   ✅ Estado          : Archivo existe")
        else:
            print(f"   ❌ Estado          : Archivo no encontrado")

def show_data_summary():
    print_header("RESUMEN DE DATOS")
    
    try:
        person_count = Person.objects.count()
        image_count = PersonImage.objects.count()
        attendance_count = AttendanceRecord.objects.count()
        course_count = Course.objects.count()
        
        print(f"   👥 Personas         : {person_count}")
        print(f"   🖼️  Imágenes        : {image_count}")
        print(f"   📝 Asistencias      : {attendance_count}")
        print(f"   📚 Cursos           : {course_count}")
        
        if person_count > 0:
            print(f"\n   👥 PERSONAS REGISTRADAS:")
            for person in Person.objects.all()[:5]:
                print(f"      - {person.nombres} {person.apellidos}")
            
            if person_count > 5:
                print(f"      ... y {person_count - 5} más")
                
    except Exception as e:
        print(f"   ❌ Error accediendo a datos: {e}")

def show_files_status():
    print_header("ESTADO DE ARCHIVOS")
    
    important_files = [
        'db.sqlite3',
        'dump_mysql_fixed.sql',
        'mysql_config.py',
        'use_mysql.bat',
        'use_sqlite.bat',
        'test_mysql.py',
        'import_to_mysql.py'
    ]
    
    for file in important_files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size / 1024  # KB
            print(f"   ✅ {file:20} : {size:6.1f} KB")
        else:
            print(f"   ❌ {file:20} : No encontrado")

def show_how_to_switch():
    print_header("CÓMO CAMBIAR CONFIGURACIÓN")
    
    current_use_mysql = os.getenv('USE_MYSQL', 'false').lower()
    
    if current_use_mysql == 'true':
        print(f"   🟢 ACTUALMENTE USANDO: MySQL RDS")
        print(f"   📝 Para cambiar a SQLite:")
        print(f"      $env:USE_MYSQL='false'")
        print(f"      python manage.py runserver")
    else:
        print(f"   🟡 ACTUALMENTE USANDO: SQLite")
        print(f"   📝 Para cambiar a MySQL:")
        print(f"      $env:USE_MYSQL='true'")
        print(f"      python manage.py runserver")
    
    print(f"\n   🚀 SCRIPTS DISPONIBLES:")
    print(f"      use_mysql.bat  - Activa MySQL automáticamente")
    print(f"      use_sqlite.bat - Activa SQLite automáticamente")
    print(f"      test_mysql.py  - Prueba conexión MySQL")

def main():
    print("🎯 DASHBOARD DE CONFIGURACIÓN DJANGO FACE RECOGNITION")
    
    show_environment_vars()
    show_django_config()
    show_database_config()
    show_data_summary()
    show_files_status()
    show_how_to_switch()
    
    print("\n" + "=" * 70)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 70)

if __name__ == "__main__":
    main()
    input("\n👆 Presiona Enter para salir...")