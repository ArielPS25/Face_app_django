from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Person, PersonImage, AttendanceRecord, ParticipationRecord, Session
from attendance.services import FaceRecognitionService
import json
import os
from datetime import date, time


class Command(BaseCommand):
    help = 'Demo del sistema de matrícula - crear datos de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Crear estudiantes de demo y sesión de prueba',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Mostrar estadísticas del sistema',
        )

    def handle(self, *args, **options):
        if options['demo']:
            self.crear_demo()
        elif options['stats']:
            self.mostrar_estadisticas()
        else:
            self.stdout.write('Uso: python manage.py demo_system --demo | --stats')

    def crear_demo(self):
        """Crear datos de demo para el sistema"""
        self.stdout.write(self.style.SUCCESS('🎓 Creando datos de demo...'))
        
        # Crear sesión de demo
        session, created = Session.objects.get_or_create(
            name="Sesión Demo - Matemáticas",
            date=date.today(),
            defaults={
                'start_time': time(8, 0),
                'end_time': time(10, 0)
            }
        )
        
        if created:
            self.stdout.write(f'✅ Sesión creada: {session.name}')
        
        # Crear algunos estudiantes adicionales de demo
        demo_students = [
            {
                'nombres': 'Ana María',
                'apellidos': 'García López',
                'email': 'ana.garcia@estudiante.edu.ec',
                'curso': '2do BGU A',
                'aula': 'A-201',
                'cedula': '1234567890',
                'telefono': '0987654321'
            },
            {
                'nombres': 'Carlos Eduardo',
                'apellidos': 'Mendoza Silva',
                'email': 'carlos.mendoza@estudiante.edu.ec',
                'curso': '1ro BGU C',
                'aula': 'C-101',
                'cedula': '0987654321',
                'telefono': '0976543210'
            },
            {
                'nombres': 'María Fernanda',
                'apellidos': 'Rodríguez Torres',
                'email': 'maria.rodriguez@estudiante.edu.ec',
                'curso': '3ro BGU B',
                'aula': 'B-301',
                'cedula': '1122334455',
                'telefono': '0965432109'
            }
        ]
        
        created_count = 0
        for student_data in demo_students:
            try:
                student, created = Person.objects.get_or_create(
                    email=student_data['email'],
                    defaults=student_data
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'✅ Estudiante creado: {student.nombre_completo}')
                    
                    # Crear registro de asistencia demo
                    AttendanceRecord.objects.get_or_create(
                        person=student,
                        session=session,
                        date=date.today(),
                        defaults={'timestamp': timezone.now()}
                    )
                    
                    # Crear registro de participación demo
                    ParticipationRecord.objects.get_or_create(
                        person=student,
                        session=session,
                        date=date.today(),
                        defaults={
                            'timestamp': timezone.now(),
                            'participation_type': 'hand_raised'
                        }
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creando {student_data["nombres"]}: {e}')
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'🎉 ¡Demo creado! {created_count} nuevos estudiantes con registros')
            )
        else:
            self.stdout.write(
                self.style.WARNING('ℹ️ Todos los estudiantes demo ya existen')
            )

    def mostrar_estadisticas(self):
        """Mostrar estadísticas completas del sistema"""
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DEL SISTEMA'))
        self.stdout.write('=' * 50)
        
        # Estadísticas de estudiantes
        total_estudiantes = Person.objects.count()
        estudiantes_activos = Person.objects.filter(is_active=True).count()
        estudiantes_con_foto = Person.objects.filter(images__isnull=False).distinct().count()
        
        self.stdout.write(f'👥 Total de estudiantes: {total_estudiantes}')
        self.stdout.write(f'✅ Estudiantes activos: {estudiantes_activos}')
        self.stdout.write(f'📷 Estudiantes con foto: {estudiantes_con_foto}')
        
        # Estadísticas por curso
        cursos = Person.objects.values_list('curso', flat=True).distinct()
        self.stdout.write(f'📚 Cursos registrados: {len(cursos)}')
        for curso in cursos:
            count = Person.objects.filter(curso=curso).count()
            self.stdout.write(f'   • {curso}: {count} estudiantes')
        
        # Estadísticas por aula
        aulas = Person.objects.values_list('aula', flat=True).distinct()
        self.stdout.write(f'🏫 Aulas registradas: {len(aulas)}')
        for aula in aulas:
            count = Person.objects.filter(aula=aula).count()
            self.stdout.write(f'   • {aula}: {count} estudiantes')
        
        # Estadísticas de imágenes
        total_imagenes = PersonImage.objects.count()
        imagenes_con_encoding = PersonImage.objects.exclude(encoding='').count()
        
        self.stdout.write(f'🖼️ Total de imágenes: {total_imagenes}')
        self.stdout.write(f'🔍 Con encoding facial: {imagenes_con_encoding}')
        
        # Estadísticas de asistencia
        total_asistencias = AttendanceRecord.objects.count()
        asistencias_hoy = AttendanceRecord.objects.filter(date=date.today()).count()
        
        self.stdout.write(f'📅 Total registros de asistencia: {total_asistencias}')
        self.stdout.write(f'📅 Asistencias hoy: {asistencias_hoy}')
        
        # Estadísticas de participación
        total_participaciones = ParticipationRecord.objects.count()
        participaciones_hoy = ParticipationRecord.objects.filter(date=date.today()).count()
        
        self.stdout.write(f'🙋 Total registros de participación: {total_participaciones}')
        self.stdout.write(f'🙋 Participaciones hoy: {participaciones_hoy}')
        
        # Estadísticas de sesiones
        total_sesiones = Session.objects.count()
        sesiones_activas = Session.objects.filter(is_active=True).count()
        
        self.stdout.write(f'📝 Total de sesiones: {total_sesiones}')
        self.stdout.write(f'🟢 Sesiones activas: {sesiones_activas}')
        
        self.stdout.write('=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ Estadísticas generadas'))
        
        # Mostrar algunos estudiantes recientes
        self.stdout.write(self.style.SUCCESS('\n👥 ÚLTIMOS ESTUDIANTES REGISTRADOS'))
        self.stdout.write('-' * 50)
        
        recent_students = Person.objects.order_by('-created_at')[:5]
        for student in recent_students:
            self.stdout.write(
                f'📝 {student.nombres} {student.apellidos}\n'
                f'   📧 {student.email}\n'
                f'   📚 {student.curso} - {student.aula}\n'
                f'   📅 Registrado: {student.created_at.strftime("%d/%m/%Y %H:%M")}\n'
            )