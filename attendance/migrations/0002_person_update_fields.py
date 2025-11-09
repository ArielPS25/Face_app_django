# Generated migration for Person model update
# This migration transforms the existing 'name' field into 'nombres' and 'apellidos'

from django.db import migrations, models
import django.utils.timezone


def split_names_forward(apps, schema_editor):
    """Split existing name field into nombres and apellidos"""
    Person = apps.get_model('attendance', 'Person')
    
    for person in Person.objects.all():
        name_parts = person.name.strip().split()
        if len(name_parts) >= 2:
            # Si hay al menos 2 partes, tomar la primera como nombres y el resto como apellidos
            person.nombres = name_parts[0]
            person.apellidos = ' '.join(name_parts[1:])
        else:
            # Si solo hay una parte, usar como nombres y poner "Sin Apellido" como apellidos
            person.nombres = name_parts[0] if name_parts else 'Sin Nombre'
            person.apellidos = 'Sin Apellido'
        
        # Si no hay email, crear uno basado en el nombre
        if not person.email:
            person.email = f"{person.nombres.lower().replace(' ', '.')}.{person.apellidos.lower().replace(' ', '.')}@estudiante.edu.ec"
        
        person.save()


def split_names_reverse(apps, schema_editor):
    """Reverse: combine nombres and apellidos back into name field"""
    Person = apps.get_model('attendance', 'Person')
    
    for person in Person.objects.all():
        person.name = f"{person.nombres} {person.apellidos}"
        person.save()


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
    ]

    operations = [
        # Paso 1: Agregar nuevos campos temporalmente como opcionales
        migrations.AddField(
            model_name='person',
            name='nombres',
            field=models.CharField(default='', help_text='Nombres del estudiante', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='apellidos',
            field=models.CharField(default='', help_text='Apellidos del estudiante', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='curso',
            field=models.CharField(default='Sin Asignar', help_text='Curso o grado', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='aula',
            field=models.CharField(default='Sin Asignar', help_text='Aula asignada', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='cedula',
            field=models.CharField(blank=True, help_text='Número de cédula', max_length=20, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='person',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='telefono',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='direccion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Paso 2: Ejecutar función para dividir nombres existentes
        migrations.RunPython(split_names_forward, split_names_reverse),
        
        # Paso 3: Hacer el email único después de asegurar que todos tienen uno
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(help_text='Email institucional', unique=True),
        ),
        
        # Paso 4: Actualizar metadatos del modelo
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['apellidos', 'nombres'], 'verbose_name': 'Estudiante', 'verbose_name_plural': 'Estudiantes'},
        ),
    ]