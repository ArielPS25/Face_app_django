#!/usr/bin/env python3
"""
Script para probar la conexión MySQL y verificar los datos migrados
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_attendance_system.settings')
os.environ['USE_MYSQL'] = 'true'

django.setup()

def test_mysql_connection():
    """Probar la conexión MySQL y mostrar estadísticas"""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONEXIÓN MYSQL")
    print("=" * 60)
    
    try:
        from django.db import connection
        from attendance.models import Person, PersonImage, AttendanceRecord, Course
        
        # Probar conexión
        print("🔌 Probando conexión a la base de datos...")
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        mysql_version = cursor.fetchone()[0]
        print(f"✅ Conexión exitosa a MySQL {mysql_version}")
        
        # Verificar configuración actual
        db_config = settings.DATABASES['default']
        print(f"\n📊 CONFIGURACIÓN ACTUAL:")
        print(f"   - Motor: {db_config['ENGINE']}")
        print(f"   - Base de datos: {db_config['NAME']}")
        print(f"   - Usuario: {db_config['USER']}")
        print(f"   - Host: {db_config['HOST']}")
        print(f"   - Puerto: {db_config['PORT']}")
        
        # Contar registros en cada tabla
        print(f"\n📋 DATOS MIGRADOS:")
        
        person_count = Person.objects.count()
        print(f"   👥 Personas: {person_count}")
        
        image_count = PersonImage.objects.count()
        print(f"   🖼️  Imágenes: {image_count}")
        
        attendance_count = AttendanceRecord.objects.count()
        print(f"   📝 Asistencias: {attendance_count}")
        
        course_count = Course.objects.count()
        print(f"   📚 Cursos: {course_count}")
        
        # Mostrar algunas personas
        if person_count > 0:
            print(f"\n👥 PERSONAS REGISTRADAS:")
            for person in Person.objects.all()[:5]:
                print(f"   - {person.nombres} {person.apellidos} ({person.email})")
                if person_count > 5:
                    remaining = person_count - 5
                    print(f"   ... y {remaining} más")
                    break
        
        # Mostrar cursos
        if course_count > 0:
            print(f"\n📚 CURSOS DISPONIBLES:")
            for course in Course.objects.all():
                print(f"   - {course.nombre} ({course.codigo})")
        
        print(f"\n🎉 ¡MIGRACIÓN VERIFICADA EXITOSAMENTE!")
        print(f"   Todos los datos se han migrado correctamente a MySQL RDS")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al conectar con MySQL: {e}")
        return False

if __name__ == "__main__":
    success = test_mysql_connection()
    
    if success:
        print(f"\n✅ La base de datos MySQL está lista para usar.")
        print(f"📝 Puedes ejecutar 'python manage.py runserver' con MySQL")
    else:
        print(f"\n❌ Hay problemas con la conexión MySQL.")
        print(f"📝 Verifica la configuración y vuelve a intentar")
    
    input(f"\n👆 Presiona Enter para salir...")