import os
import json
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from attendance.models import Person, PersonImage
from attendance.services import FaceRecognitionService
import face_recognition
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Carga automáticamente las imágenes de estudiantes desde attendance/images/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Sobrescribir personas existentes',
        )

    def handle(self, *args, **options):
        """Comando principal para cargar imágenes de estudiantes"""
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando carga de imágenes de estudiantes...'))
        
        # Ruta a la carpeta de imágenes
        images_path = os.path.join(settings.BASE_DIR, 'attendance', 'images')
        
        if not os.path.exists(images_path):
            self.stdout.write(
                self.style.ERROR(f'❌ La carpeta {images_path} no existe')
            )
            return
        
        # Inicializar servicio de reconocimiento facial
        face_service = FaceRecognitionService()
        
        # Contadores
        personas_creadas = 0
        imagenes_procesadas = 0
        errores = 0
        
        # Recorrer carpetas de personas
        for person_name in os.listdir(images_path):
            person_folder = os.path.join(images_path, person_name)
            
            if not os.path.isdir(person_folder):
                continue
            
            self.stdout.write(f'📁 Procesando: {person_name}')
            
            # Verificar si la persona ya existe
            person, person_created = Person.objects.get_or_create(
                name=person_name,
                defaults={
                    'email': f'{person_name.lower().replace(" ", "_")}@estudiante.com',
                    'is_active': True
                }
            )
            
            if person_created:
                personas_creadas += 1
                self.stdout.write(f'  ✅ Persona creada: {person_name}')
            elif options['overwrite']:
                # Eliminar imágenes existentes si se especifica overwrite
                person.images.all().delete()
                self.stdout.write(f'  🔄 Sobrescribiendo imágenes de: {person_name}')
            else:
                self.stdout.write(f'  ⚠️  Persona ya existe: {person_name} (usa --overwrite para sobrescribir)')
                continue
            
            # Procesar imágenes de la persona
            images_for_person = 0
            for filename in os.listdir(person_folder):
                filepath = os.path.join(person_folder, filename)
                
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                    continue
                
                try:
                    # Generar encoding de la imagen
                    self.stdout.write(f'    🔍 Procesando imagen: {filename}')
                    encoding = self.generate_face_encoding(filepath)
                    
                    if encoding is None:
                        self.stdout.write(
                            self.style.WARNING(f'    ⚠️  No se detectó rostro en: {filename}')
                        )
                        errores += 1
                        continue
                    
                    # Crear PersonImage
                    person_image = PersonImage.objects.create(
                        person=person,
                        encoding=json.dumps(encoding)
                    )
                    
                    # Guardar imagen
                    with open(filepath, 'rb') as img_file:
                        person_image.image.save(
                            filename,
                            File(img_file),
                            save=True
                        )
                    
                    images_for_person += 1
                    imagenes_procesadas += 1
                    self.stdout.write(f'    ✅ Imagen procesada: {filename}')
                    
                except Exception as e:
                    errores += 1
                    self.stdout.write(
                        self.style.ERROR(f'    ❌ Error procesando {filename}: {str(e)}')
                    )
            
            if images_for_person > 0:
                self.stdout.write(f'  📊 Total imágenes para {person_name}: {images_for_person}')
        
        # Recargar encodings en el servicio
        face_service.load_known_faces()
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE CARGA'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'👥 Personas creadas: {personas_creadas}')
        self.stdout.write(f'🖼️  Imágenes procesadas: {imagenes_procesadas}')
        self.stdout.write(f'❌ Errores: {errores}')
        self.stdout.write(self.style.SUCCESS('✅ Carga completada exitosamente!'))
        
        if imagenes_procesadas > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n💡 Las imágenes han sido cargadas y están listas para el reconocimiento facial.'
                )
            )

    def generate_face_encoding(self, image_path):
        """Genera encoding facial desde archivo de imagen"""
        try:
            # Cargar imagen
            image = face_recognition.load_image_file(image_path)
            
            # Detectar rostros y generar encodings
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                return encodings[0].tolist()  # Convertir a lista para JSON
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error generando encoding para {image_path}: {e}")
            return None