#!/usr/bin/env python3
"""
Script para mostrar la configuración actual de Django
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_attendance_system.settings')

# Detectar si USE_MYSQL está configurado
use_mysql_env = os.getenv('USE_MYSQL', 'No configurado')
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN DJANGO")
print("=" * 60)

django.setup()

def show_current_config():
    """Mostrar la configuración actual"""
    
    print(f"🌐 VARIABLES DE ENTORNO:")
    print(f"   USE_MYSQL: {use_mysql_env}")
    print(f"   MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE', 'No configurado')}")
    print(f"   MYSQL_USER: {os.getenv('MYSQL_USER', 'No configurado')}")
    print(f"   MYSQL_HOST: {os.getenv('MYSQL_HOST', 'No configurado')}")
    print(f"   MYSQL_PORT: {os.getenv('MYSQL_PORT', 'No configurado')}")
    
    print(f"\n📊 CONFIGURACIÓN DJANGO ACTUAL:")
    db_config = settings.DATABASES['default']
    
    print(f"   Motor de BD: {db_config['ENGINE']}")
    
    if 'mysql' in db_config['ENGINE']:
        print(f"   🗄️  BASE DE DATOS: MySQL")
        print(f"   📂 Nombre: {db_config['NAME']}")
        print(f"   👤 Usuario: {db_config['USER']}")
        print(f"   🌐 Host: {db_config['HOST']}")
        print(f"   🚪 Puerto: {db_config['PORT']}")
        print(f"   🔧 Opciones: {db_config.get('OPTIONS', 'Ninguna')}")
        
        # Probar conexión
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"   ✅ Estado: Conectado a MySQL {version}")
            
            # Mostrar información adicional
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"   📋 BD Actual: {current_db}")
            
        except Exception as e:
            print(f"   ❌ Estado: Error de conexión - {e}")
            
    elif 'sqlite' in db_config['ENGINE']:
        print(f"   🗄️  BASE DE DATOS: SQLite")
        print(f"   📁 Archivo: {db_config['NAME']}")
        
        # Verificar si el archivo existe
        if os.path.exists(db_config['NAME']):
            size = os.path.getsize(db_config['NAME']) / (1024 * 1024)  # MB
            print(f"   📏 Tamaño: {size:.2f} MB")
            print(f"   ✅ Estado: Archivo existe")
        else:
            print(f"   ❌ Estado: Archivo no encontrado")
    
    print(f"\n🔧 CONFIGURACIÓN ADICIONAL:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   SECRET_KEY: {'*' * 10}...{settings.SECRET_KEY[-10:]}")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")

if __name__ == "__main__":
    show_current_config()
    
    print(f"\n📝 CÓMO CAMBIAR LA CONFIGURACIÓN:")
    print(f"   Para MySQL: $env:USE_MYSQL='true'")
    print(f"   Para SQLite: $env:USE_MYSQL='false'")
    
    input(f"\n👆 Presiona Enter para salir...")