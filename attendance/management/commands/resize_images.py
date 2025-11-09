from django.core.management.base import BaseCommand
from django.conf import settings
from attendance.models import PersonImage
from PIL import Image, ImageOps
import os


class Command(BaseCommand):
    help = 'Redimensiona todas las imágenes existentes a 400x400 cuadradas'

    def handle(self, *args, **options):
        images = PersonImage.objects.all()
        
        if not images.exists():
            self.stdout.write(self.style.WARNING('No hay imágenes para procesar.'))
            return
        
        self.stdout.write(f'🖼️ Procesando {images.count()} imágenes...')
        
        processed = 0
        errors = 0
        
        for person_image in images:
            try:
                # Verificar si el archivo existe
                if not person_image.image or not os.path.exists(person_image.image.path):
                    self.stdout.write(
                        self.style.ERROR(f'❌ Archivo no encontrado: {person_image}')
                    )
                    errors += 1
                    continue
                
                # Verificar si ya fue procesada (tiene el sufijo)
                if '_400x400' in person_image.image.name:
                    self.stdout.write(f'⏭️ Ya procesada: {person_image}')
                    continue
                
                # Abrir y procesar imagen
                with Image.open(person_image.image.path) as img:
                    # Convertir a RGB si es necesario
                    if img.mode in ('RGBA', 'P', 'L'):
                        img = img.convert('RGB')
                    
                    # Redimensionar y recortar a cuadrado
                    img_resized = ImageOps.fit(
                        img, 
                        (400, 400), 
                        Image.Resampling.LANCZOS,
                        centering=(0.5, 0.5)
                    )
                    
                    # Generar nuevo nombre de archivo
                    original_path = person_image.image.path
                    dir_name = os.path.dirname(original_path)
                    base_name = os.path.splitext(os.path.basename(original_path))[0]
                    new_filename = f"{base_name}_400x400.jpg"
                    new_path = os.path.join(dir_name, new_filename)
                    
                    # Guardar imagen redimensionada
                    img_resized.save(new_path, format='JPEG', quality=85, optimize=True)
                    
                    # Actualizar el campo image en la base de datos
                    relative_path = os.path.relpath(new_path, settings.MEDIA_ROOT)
                    person_image.image.name = relative_path
                    person_image.save(update_fields=['image'])
                    
                    # Eliminar archivo original si es diferente
                    if original_path != new_path and os.path.exists(original_path):
                        os.remove(original_path)
                    
                    processed += 1
                    self.stdout.write(f'✅ Procesada: {person_image} -> {new_filename}')
                    
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error procesando {person_image}: {str(e)}')
                )
        
        # Resumen
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(f'📊 RESUMEN:')
        self.stdout.write(f'✅ Procesadas exitosamente: {processed}')
        self.stdout.write(f'❌ Errores: {errors}')
        self.stdout.write(f'📁 Total: {images.count()}')
        
        if processed > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 ¡{processed} imágenes redimensionadas a 400x400!')
            )
        
        if errors > 0:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️ {errors} imágenes tuvieron errores.')
            )