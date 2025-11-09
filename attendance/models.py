from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import os
import io


class Course(models.Model):
    """Model for managing courses"""
    
    # Opciones predefinidas para aulas
    AULA_CHOICES = [
        ('A-101', 'Aula A-101'),
        ('A-102', 'Aula A-102'),
        ('A-103', 'Aula A-103'),
        ('B-201', 'Aula B-201'),
        ('B-202', 'Aula B-202'),
        ('B-203', 'Aula B-203'),
        ('LAB-1', 'Laboratorio 1'),
        ('LAB-2', 'Laboratorio 2'),
        ('LAB-3', 'Laboratorio 3'),
        ('AULA-MAGNA', 'Aula Magna'),
        ('BIBLIOTECA', 'Biblioteca'),
        ('VIRTUAL', 'Aula Virtual'),
    ]
    
    # Opciones predefinidas para horarios
    HORARIO_CHOICES = [
        ('08:00-10:00', '08:00 - 10:00 AM'),
        ('10:00-12:00', '10:00 - 12:00 AM'),
        ('14:00-16:00', '14:00 - 16:00 PM'),
        ('16:00-18:00', '16:00 - 18:00 PM'),
        ('18:00-20:00', '18:00 - 20:00 PM'),
        ('20:00-22:00', '20:00 - 22:00 PM'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del curso")
    descripcion = models.TextField(blank=True, help_text="Descripción del curso")
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Código del curso")
    aula = models.CharField(max_length=20, choices=AULA_CHOICES, help_text="Aula asignada")
    sesion = models.CharField(max_length=50, blank=True, help_text="Sesión o turno")
    profesor = models.CharField(max_length=100, help_text="Nombre del profesor")
    horario = models.CharField(max_length=100, choices=HORARIO_CHOICES, help_text="Horario del curso")
    
    # Estados
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
    
    def __str__(self):
        return f"{self.nombre} ({self.aula})"
    
    def get_student_count(self):
        """Obtener número de estudiantes en el curso"""
        return Person.objects.filter(curso=self.nombre, is_active=True).count()


def person_image_path(instance, filename):
    """Generate file path for person images"""
    return f'person_images/{instance.person.name}/{filename}'


class Person(models.Model):
    """Model for storing person information and face encodings"""
    # Información básica
    nombres = models.CharField(max_length=100, help_text="Nombres del estudiante")
    apellidos = models.CharField(max_length=100, help_text="Apellidos del estudiante")
    email = models.EmailField(unique=True, help_text="Email institucional")
    
    # Información académica
    curso = models.CharField(max_length=50, help_text="Curso o grado")
    aula = models.CharField(max_length=20, help_text="Aula asignada")
    
    # Información adicional
    cedula = models.CharField(max_length=20, unique=True, blank=True, null=True, 
                             help_text="Número de cédula")
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    
    # Estados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def name(self):
        """Mantener compatibilidad con código existente"""
        return self.nombre_completo
    
    def get_course_aula(self):
        """Obtener el aula del curso al que pertenece el estudiante"""
        try:
            course = Course.objects.get(nombre=self.curso, is_active=True)
            return course.aula
        except Course.DoesNotExist:
            return self.aula or "No asignada"


class PersonImage(models.Model):
    """Model for storing multiple face images per person"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=person_image_path)
    encoding = models.TextField(blank=True, help_text="JSON encoded face encoding")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_primary', '-uploaded_at']
    
    def __str__(self):
        return f"{self.person.name} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        """Override save to resize and crop image to 400x400 square and generate face encoding"""
        if self.image:
            # Open the uploaded image
            img = Image.open(self.image)
            
            # Convert to RGB if necessary (handles RGBA, P mode images)
            if img.mode in ('RGBA', 'P', 'L'):
                img = img.convert('RGB')
            
            # Resize and crop to square (400x400)
            img = ImageOps.fit(
                img, 
                (400, 400), 
                Image.Resampling.LANCZOS,  # High quality resampling
                centering=(0.5, 0.5)  # Center the crop
            )
            
            # Save to BytesIO
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Replace the image field with resized version
            filename = os.path.splitext(self.image.name)[0] + '_400x400.jpg'
            self.image.save(
                filename,
                ContentFile(output.getvalue()),
                save=False
            )
            output.close()
        
        # Primero guardar el objeto para que tenga la imagen
        super().save(*args, **kwargs)
        
        # Generar encoding facial si no existe
        if self.image and not self.encoding:
            self.generate_face_encoding()
    
    def generate_face_encoding(self):
        """Generate face encoding for the image"""
        try:
            import face_recognition
            import json
            
            # Cargar la imagen
            image_path = self.image.path
            image = face_recognition.load_image_file(image_path)
            
            # Detectar rostros
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) > 0:
                # Generar encoding del primer rostro detectado
                face_encodings = face_recognition.face_encodings(image, face_locations)
                
                if len(face_encodings) > 0:
                    # Convertir a JSON y guardar
                    encoding_json = json.dumps(face_encodings[0].tolist())
                    self.encoding = encoding_json
                    # Usar update para evitar llamar save() recursivamente
                    PersonImage.objects.filter(id=self.id).update(encoding=encoding_json)
                    return True
            return False
        except Exception as e:
            print(f"Error generando encoding: {e}")
            return False


class AttendanceRecord(models.Model):
    """Model for storing attendance records"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='attendance_records')
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    confidence = models.FloatField(default=0.0, help_text="Face recognition confidence score")
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        unique_together = ['person', 'date']  # One attendance per person per day
    
    def __str__(self):
        return f"{self.person.name} - {self.date}"


class ParticipationRecord(models.Model):
    """Model for storing participation records (hand gestures)"""
    PARTICIPATION_TYPES = [
        ('hand_raised', 'Hand Raised'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('comment', 'Comment'),
    ]
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='participation_records')
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    participation_type = models.CharField(max_length=20, choices=PARTICIPATION_TYPES, default='hand_raised')
    confidence = models.FloatField(default=0.0, help_text="Hand detection confidence score")
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.person.name} - {self.participation_type} - {self.timestamp.strftime('%H:%M:%S')}"


class Session(models.Model):
    """Model for managing attendance sessions"""
    name = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"{self.name} - {self.date}"
    
    def get_attendance_count(self):
        """Get number of attendees for this session"""
        return AttendanceRecord.objects.filter(date=self.date).count()
    
    def get_participation_count(self):
        """Get number of participations for this session"""
        return ParticipationRecord.objects.filter(date=self.date).count()
