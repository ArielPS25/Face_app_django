#!/usr/bin/env python3
"""
Script de verificación post-instalación
Verifica que todas las dependencias estén correctamente instaladas
"""

import sys
import importlib
import subprocess

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and 8 <= version.minor <= 11:
        print("   ✅ Versión compatible")
        return True
    else:
        print("   ⚠️  Versión no recomendada (usa Python 3.8-3.11)")
        return False

def check_package(package_name, import_name=None, show_version=True):
    """Verificar si un paquete está instalado"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        
        if show_version and hasattr(module, '__version__'):
            version = module.__version__
            print(f"   ✅ {package_name}: {version}")
        else:
            print(f"   ✅ {package_name}: Instalado")
        return True
        
    except ImportError:
        print(f"   ❌ {package_name}: No instalado")
        return False

def check_opencv():
    """Verificación especial para OpenCV"""
    try:
        import cv2
        print(f"   ✅ OpenCV: {cv2.__version__}")
        
        # Probar captura de video
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print(f"   ✅ Cámara: Disponible")
            cap.release()
        else:
            print(f"   ⚠️  Cámara: No disponible (normal en algunos entornos)")
        
        return True
    except ImportError:
        print(f"   ❌ OpenCV: No instalado")
        return False

def check_dlib():
    """Verificación especial para dlib"""
    try:
        import dlib
        print(f"   ✅ dlib: Instalado correctamente")
        
        # Probar detector de caras
        detector = dlib.get_frontal_face_detector()
        print(f"   ✅ Detector de caras: Funcional")
        return True
        
    except ImportError:
        print(f"   ❌ dlib: No instalado")
        return False
    except Exception as e:
        print(f"   ⚠️  dlib: Instalado pero con errores - {e}")
        return False

def check_django():
    """Verificar Django y configuración"""
    try:
        import django
        from django.conf import settings
        
        print(f"   ✅ Django: {django.get_version()}")
        
        # Verificar configuración
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_attendance_system.settings')
        django.setup()
        
        # Verificar base de datos
        from django.db import connection
        db_config = settings.DATABASES['default']
        engine = db_config['ENGINE']
        
        if 'sqlite' in engine:
            print(f"   ✅ Base de datos: SQLite")
        elif 'mysql' in engine:
            print(f"   ✅ Base de datos: MySQL")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Django: Error - {e}")
        return False

def main():
    """Función principal de verificación"""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN POST-INSTALACIÓN")
    print("=" * 60)
    
    all_good = True
    
    # Verificar Python
    print("\n🐍 PYTHON:")
    all_good &= check_python_version()
    
    # Verificar Django
    print("\n🎯 DJANGO:")
    all_good &= check_django()
    
    # Verificar paquetes principales
    print("\n📦 PAQUETES PRINCIPALES:")
    packages = [
        ('django-widget-tweaks', 'widget_tweaks'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('Pillow', 'PIL'),
    ]
    
    for pkg_name, import_name in packages:
        all_good &= check_package(pkg_name, import_name)
    
    # Verificar computer vision
    print("\n👁️  COMPUTER VISION:")
    all_good &= check_opencv()
    all_good &= check_dlib()
    all_good &= check_package('face-recognition', 'face_recognition')
    all_good &= check_package('mediapipe', 'mediapipe')
    
    # Verificar base de datos
    print("\n🗄️  BASE DE DATOS:")
    mysql_installed = check_package('mysql-connector-python', 'mysql.connector', False)
    mysqlclient_installed = check_package('mysqlclient', 'MySQLdb', False)
    
    if not mysql_installed and not mysqlclient_installed:
        print("   ⚠️  Ningún driver MySQL instalado (solo SQLite disponible)")
        all_good = False
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ Todos los componentes están instalados correctamente")
        print("\n📝 Próximos pasos:")
        print("   1. python manage.py migrate")
        print("   2. python manage.py createsuperuser")
        print("   3. python manage.py runserver")
    else:
        print("⚠️  VERIFICACIÓN CON PROBLEMAS")
        print("❌ Algunos componentes necesitan atención")
        print("\n📝 Soluciones:")
        print("   - Revisa INSTALACION.md para solución de problemas")
        print("   - Usa requirements-minimal.txt si hay issues con dlib")
        print("   - Instala dependencias del sistema faltantes")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\n👆 Presiona Enter para salir...")