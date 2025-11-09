# Clean up migration - remove old 'name' field and fix data

from django.db import migrations, models


def fix_student_data(apps, schema_editor):
    """Fix the migrated student data"""
    Person = apps.get_model('attendance', 'Person')
    
    # Datos de ejemplo mejorados para los estudiantes existentes
    students_data = {
        'Ariel_Pesantez': {
            'nombres': 'Ariel',
            'apellidos': 'Pesántez',
            'email': 'ariel.pesantez@estudiante.edu.ec',
            'curso': '1ro BGU A',
            'aula': 'A-101'
        },
        'Bill_Gates': {
            'nombres': 'Bill',
            'apellidos': 'Gates',
            'email': 'bill.gates@estudiante.edu.ec',
            'curso': '2do BGU B',
            'aula': 'B-201'
        },
        'Elon_Musk': {
            'nombres': 'Elon',
            'apellidos': 'Musk',
            'email': 'elon.musk@estudiante.edu.ec',
            'curso': '3ro BGU A',
            'aula': 'A-301'
        },
        'Layla_Veliz': {
            'nombres': 'Layla',
            'apellidos': 'Véliz',
            'email': 'layla.veliz@estudiante.edu.ec',
            'curso': '1ro BGU B',
            'aula': 'B-101'
        }
    }
    
    for person in Person.objects.all():
        # Intentar encontrar el estudiante por el nombre original
        original_name = f"{person.nombres}_{person.apellidos}".replace(" ", "_")
        
        if original_name in students_data:
            data = students_data[original_name]
            person.nombres = data['nombres']
            person.apellidos = data['apellidos']
            person.email = data['email']
            person.curso = data['curso']
            person.aula = data['aula']
            person.save()


def reverse_fix_student_data(apps, schema_editor):
    """Reverse the data fix"""
    # No need to reverse, the old data will be lost anyway
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_person_update_fields'),
    ]

    operations = [
        # Paso 1: Arreglar los datos de estudiantes
        migrations.RunPython(fix_student_data, reverse_fix_student_data),
        
        # Paso 2: Eliminar el campo 'name' antiguo
        migrations.RemoveField(
            model_name='person',
            name='name',
        ),
    ]