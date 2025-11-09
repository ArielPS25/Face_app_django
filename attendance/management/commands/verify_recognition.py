from django.core.management.base import BaseCommand
from attendance.services import FaceRecognitionService
from attendance.models import PersonImage, Person
import json
import os


class Command(BaseCommand):
    help = 'Verifica el estado completo del sistema de reconocimiento facial'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 VERIFICACIÓN COMPLETA DEL SISTEMA'))
        self.stdout.write('=' * 60)
        
        # 1. Verificar servicio
        self.verificar_servicio()
        
        # 2. Verificar imágenes
        self.verificar_imagenes()
        
        # 3. Verificar encodings
        self.verificar_encodings()
        
        # 4. Recomendaciones
        self.mostrar_recomendaciones()

    def verificar_servicio(self):
        self.stdout.write('\n📡 SERVICIO DE RECONOCIMIENTO FACIAL')
        self.stdout.write('-' * 40)
        
        try:
            service = FaceRecognitionService()
            self.stdout.write(f'✅ Servicio inicializado correctamente')
            self.stdout.write(f'📊 Encodings cargados: {len(service.known_encodings)}')
            self.stdout.write(f'👥 Personas conocidas: {len(service.known_names)}')
            self.stdout.write(f'🆔 IDs de personas: {service.known_person_ids}')
            
            return service
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error inicializando servicio: {e}'))
            return None

    def verificar_imagenes(self):
        self.stdout.write('\n🖼️ ESTADO DE IMÁGENES')
        self.stdout.write('-' * 40)
        
        total_images = PersonImage.objects.count()
        images_with_encoding = PersonImage.objects.exclude(encoding='').count()
        images_without_encoding = PersonImage.objects.filter(encoding='').count()
        
        self.stdout.write(f'📊 Total de imágenes: {total_images}')
        self.stdout.write(f'✅ Con encoding: {images_with_encoding}')
        self.stdout.write(f'❌ Sin encoding: {images_without_encoding}')
        
        # Verificar archivos físicos
        missing_files = 0
        for img in PersonImage.objects.all():
            if not os.path.exists(img.image.path):
                missing_files += 1
                self.stdout.write(f'⚠️ Archivo faltante: {img.image.name}')
        
        if missing_files == 0:
            self.stdout.write('✅ Todos los archivos de imagen existen')
        else:
            self.stdout.write(f'❌ {missing_files} archivos de imagen faltantes')

    def verificar_encodings(self):
        self.stdout.write('\n🔢 DETALLE DE ENCODINGS POR PERSONA')
        self.stdout.write('-' * 40)
        
        for person in Person.objects.filter(is_active=True).order_by('apellidos', 'nombres'):
            images = person.images.all()
            images_with_enc = images.exclude(encoding='').count()
            
            status = '✅' if images_with_enc > 0 else '❌'
            self.stdout.write(f'{status} {person.nombres} {person.apellidos}:')
            self.stdout.write(f'    📷 {images.count()} imágenes, {images_with_enc} con encoding')
            
            for img in images:
                has_encoding = bool(img.encoding)
                size_info = ''
                if os.path.exists(img.image.path):
                    file_size = os.path.getsize(img.image.path) / 1024  # KB
                    size_info = f' ({file_size:.1f}KB)'
                
                enc_status = '✅' if has_encoding else '❌'
                self.stdout.write(f'      {enc_status} {img.image.name}{size_info}')

    def mostrar_recomendaciones(self):
        self.stdout.write('\n💡 RECOMENDACIONES')
        self.stdout.write('-' * 40)
        
        # Verificar si hay problemas
        images_without_encoding = PersonImage.objects.filter(encoding='').count()
        inactive_persons = Person.objects.filter(is_active=False).count()
        
        if images_without_encoding > 0:
            self.stdout.write(f'⚠️ Hay {images_without_encoding} imágenes sin encoding')
            self.stdout.write('   Ejecutar: python manage.py shell -c "..."  para generar encodings')
        
        if inactive_persons > 0:
            self.stdout.write(f'ℹ️ Hay {inactive_persons} personas inactivas (no se procesan)')
        
        # Verificar rendimiento
        total_encodings = PersonImage.objects.exclude(encoding='').count()
        if total_encodings > 20:
            self.stdout.write('⚡ Con más de 20 encodings, considera optimizaciones de rendimiento')
        
        # Estado general
        if images_without_encoding == 0:
            self.stdout.write(self.style.SUCCESS('🎉 ¡Sistema completamente operativo!'))
            self.stdout.write('✅ Todas las imágenes tienen encodings')
            self.stdout.write('✅ El reconocimiento facial debería funcionar correctamente')
            self.stdout.write('\n🚀 Para probar:')
            self.stdout.write('   1. Ir a http://127.0.0.1:8000/camera/')
            self.stdout.write('   2. Activar la cámara')
            self.stdout.write('   3. Mostrar rostro frente a la cámara')
        else:
            self.stdout.write(self.style.WARNING('⚠️ Sistema parcialmente operativo'))
            self.stdout.write('   Algunas imágenes necesitan procesamiento adicional')