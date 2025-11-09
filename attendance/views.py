from django.shortcuts import render, get_object_or_404, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Count, Q
from datetime import date, datetime, timedelta
import cv2
import json
import threading
import time
import logging

from .models import Person, PersonImage, AttendanceRecord, ParticipationRecord, Session, Course
from .services import FaceRecognitionService, HandGestureService
from .forms import PersonForm, SessionForm, EstudianteForm, CourseForm

logger = logging.getLogger(__name__)

# Global variables for camera and services
camera = None
face_service = None
hand_service = None
camera_thread = None
is_camera_running = False
latest_frame = None

# Configuración balanceada rendimiento/funcionalidad
VIDEO_SCALE = 0.25  # reduce resolución (más rápido)
FRAME_SKIP = 3  # procesa 1 de cada 3 frames (balance)
MIN_CONFIDENCE_TIME = 1  # segundos para confirmar reconocimiento
PARTICIPATION_COOLDOWN = 30  # segundos entre participaciones de la misma persona
HAND_DETECTION_THRESHOLD = 5  # segundos para mantener detección de mano
DRAWING_SKIP = 1  # dibuja visualizaciones en cada frame

detection_results = {
    'faces': [],
    'hands': [],
    'attendance_today': set(),
    'participation_today': set(),
    'last_detections': {},
    'personas_detectadas': {},  # {person_id: timestamp_deteccion}
    'mano_levantada': {},  # {person_id: timestamp_mano_levantada}
    'ultima_participacion': {},  # {person_id: timestamp_ultima_participacion}
}


@login_required
def home(request):
    """Home page with dashboard"""
    today = date.today()
    
    # Get today's statistics
    attendance_count = AttendanceRecord.objects.filter(date=today).count()
    participation_count = ParticipationRecord.objects.filter(date=today).count()
    total_persons = Person.objects.filter(is_active=True).count()
    
    # Get recent attendance
    recent_attendance = AttendanceRecord.objects.filter(date=today).select_related('person')[:10]
    recent_participation = ParticipationRecord.objects.filter(date=today).select_related('person')[:10]
    
    # Get active session
    active_session = Session.objects.filter(is_active=True).first()
    
    context = {
        'attendance_count': attendance_count,
        'participation_count': participation_count,
        'total_persons': total_persons,
        'recent_attendance': recent_attendance,
        'recent_participation': recent_participation,
        'active_session': active_session,
        'today': today,
    }
    
    return render(request, 'attendance/home.html', context)


def camera_view(request):
    """Camera view for real-time detection"""
    return render(request, 'attendance/camera.html')


def camera_feed(request):
    """Video streaming route for camera feed"""
    def generate():
        global latest_frame
        while True:
            if latest_frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', latest_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


def verificar_deteccion_continua(person_id):
    """Verifica si una persona ha sido detectada continuamente"""
    ahora = time.time()

    if person_id not in detection_results['personas_detectadas']:
        detection_results['personas_detectadas'][person_id] = ahora
        return False

    tiempo_deteccion = ahora - detection_results['personas_detectadas'][person_id]
    return tiempo_deteccion >= MIN_CONFIDENCE_TIME


def registrar_mano_levantada(person_id, person_name):
    """Registra que una persona levantó la mano"""
    ahora = time.time()
    detection_results['mano_levantada'][person_id] = ahora

    # Solo registrar participación si la persona está confirmada
    if verificar_deteccion_continua(person_id):
        return registrar_participacion_mejorada(person_id, person_name)
    return False


def registrar_participacion_mejorada(person_id, person_name):
    """Registra la participación de una persona con cooldown mejorado"""
    try:
        ahora = time.time()
        
        # Verificar cooldown
        if person_id in detection_results['ultima_participacion']:
            tiempo_transcurrido = ahora - detection_results['ultima_participacion'][person_id]
            if tiempo_transcurrido < PARTICIPATION_COOLDOWN:
                logger.debug(f"Participación de {person_name} en cooldown ({tiempo_transcurrido:.1f}s)")
                return False

        # Crear registro de participación
        person = Person.objects.get(id=person_id)
        ParticipationRecord.objects.create(
            person=person,
            confidence=0.95,  # Alta confianza para detección manual
            participation_type='hand_raised'
        )
        
        # Actualizar estado en memoria
        detection_results['participation_today'].add(person_name)
        detection_results['ultima_participacion'][person_id] = ahora

        logger.info(f"✅ PARTICIPACIÓN: {person_name} - mano_levantada a las {datetime.now().strftime('%H:%M:%S')}")
        return True
        
    except Exception as e:
        logger.error(f"Error registrando participación para {person_name}: {e}")
        return False


def limpiar_detecciones():
    """Limpia detecciones antiguas para liberar memoria"""
    ahora = time.time()
    
    # Limpiar detecciones de personas
    detection_results['personas_detectadas'] = {
        k: v for k, v in detection_results['personas_detectadas'].items()
        if ahora - v < MIN_CONFIDENCE_TIME * 2
    }
    
    # Limpiar detecciones de manos
    detection_results['mano_levantada'] = {
        k: v for k, v in detection_results['mano_levantada'].items()
        if ahora - v < HAND_DETECTION_THRESHOLD * 2
    }


def verificar_mano_levantada(person_id):
    """Verifica si una persona tiene la mano levantada recientemente"""
    ahora = time.time()
    if person_id in detection_results['mano_levantada']:
        return ahora - detection_results['mano_levantada'][person_id] < HAND_DETECTION_THRESHOLD
    return False


def start_camera():
    """Start camera detection in background thread - improved version"""
    global camera, face_service, hand_service, is_camera_running, latest_frame, detection_results
    
    if is_camera_running:
        return
    
    try:
        camera = cv2.VideoCapture(0)
        # Configuración optimizada para mejor FPS
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)  # Aumentar FPS objetivo
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer para menos latencia
        
        face_service = FaceRecognitionService()
        hand_service = HandGestureService()
        
        is_camera_running = True
        
        logger.info("Camera started successfully")
        
        # Main detection loop
        frame_count = 0
        
        while is_camera_running:
            ret, frame = camera.read()
            if not ret:
                logger.warning("No se pudo leer frame de la cámara")
                break
            
            frame_count += 1
            current_time = time.time()
            
            # Variables para procesamiento balanceado
            process_recognition = (frame_count % FRAME_SKIP == 0)
            draw_visuals = (frame_count % DRAWING_SKIP == 0)
            
            # Inicializar con valores vacíos si es primera ejecución
            recognized_faces = detection_results.get('faces', [])
            hands = detection_results.get('hands', [])
            face_locations = detection_results.get('face_locations', [])
            hand_associations = detection_results.get('hand_associations', [])
            
            # Procesar reconocimiento cada FRAME_SKIP frames
            if process_recognition:
                try:
                    # Face recognition
                    recognized_faces, face_locations = face_service.recognize_face(frame)
                    
                    # Hand detection (procesar siempre, no solo si hay rostros)
                    hands, hand_results = hand_service.detect_hand_raised(frame)
                    hand_associations = hand_service.associate_hand_with_face(hands, face_locations, recognized_faces)
                    
                    # Update detection results
                    detection_results.update({
                        'faces': recognized_faces,
                        'hands': hands,
                        'face_locations': face_locations,
                        'hand_associations': hand_associations
                    })
                    
                    # Log para debug
                    if len(recognized_faces) > 0:
                        logger.info(f"Detectados {len(recognized_faces)} rostros en frame {frame_count}")
                        
                except Exception as e:
                    logger.error(f"Error en procesamiento: {e}")
                    # En caso de error, limpiar detecciones previas
                    recognized_faces = []
                    hands = []
                    face_locations = []
                    hand_associations = []
                
                # Process attendance registration - MEJORADO
                for i, face in enumerate(recognized_faces):
                    if face['person_id'] and face['confidence'] > 0.4:  # Minimum confidence
                        person_id = face['person_id']
                        
                        # Verificar detección continua ANTES de registrar asistencia
                        if verificar_deteccion_continua(person_id):
                            try:
                                person = Person.objects.get(id=person_id)
                                attendance, created = AttendanceRecord.objects.get_or_create(
                                    person=person,
                                    date=date.today(),
                                    defaults={'confidence': face['confidence']}
                                )
                                if created:
                                    detection_results['attendance_today'].add(person.name)
                                    logger.info(f"✅ ASISTENCIA: {person.name} - {datetime.now().strftime('%H:%M:%S')}")
                            except Person.DoesNotExist:
                                pass
                
                # Process participation registration - SOLO cuando se procesa reconocimiento
                for association in hand_associations:
                    person_id = association['person_id']
                    person_name = association['person_name']
                    
                    # Usar la nueva función mejorada
                    if registrar_mano_levantada(person_id, person_name):
                        logger.info(f"Participación registrada para {person_name}")
                
                # Limpiar detecciones antiguas (SOLO cada ciertos frames)
                if frame_count % 30 == 0:  # Solo cada 30 frames (1 segundo aprox)
                    limpiar_detecciones()
            
            # Siempre dibujar visualizaciones para mejor feedback
            frame = draw_detections(frame, recognized_faces, face_locations, hands, hand_associations)
            
            latest_frame = frame
            
            # Delay balanceado para buen FPS
            time.sleep(0.02)
    
    except Exception as e:
        logger.error(f"Camera error: {e}")
    finally:
        if camera:
            camera.release()
        is_camera_running = False


def draw_detections(frame, faces, face_locations, hands, hand_associations):
    """Draw detection results on frame - improved version"""
    # Asegurar que frame sea válido
    if frame is None:
        logger.error("Frame is None in draw_detections")
        return frame
    
    # Asegurar que las listas tengan valores por defecto
    if faces is None:
        faces = []
    if face_locations is None:
        face_locations = []
    if hands is None:
        hands = []
    if hand_associations is None:
        hand_associations = []
    
    # Optimización: evitar evaluaciones innecesarias
    attendance_today = detection_results['attendance_today']
    
    # Draw face rectangles and labels (optimizado)
    for i, ((top, right, bottom, left), face) in enumerate(zip(face_locations, faces)):
        try:
            person_id = face.get('person_id')
            name = face.get('name', 'Unknown')
            confidence = face.get('confidence', 0.0)
            
            # Determinar color y estado (optimizado)
            if not person_id:
                color = (0, 0, 255)  # Rojo
                label = "Unknown"
            elif name in attendance_today:
                color = (0, 255, 0)  # Verde
                label = f"{name}"
            elif verificar_deteccion_continua(person_id):
                color = (255, 255, 0)  # Amarillo
                label = f"{name}"
            else:
                color = (0, 128, 255)  # Naranja
                label = f"{name}"

            # Dibujar solo rectángulo y nombre (simplificado para rendimiento)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, label, (left + 4, bottom - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        
        except Exception as e:
            logger.error(f"Error dibujando rostro {i}: {e}")
            continue
    
    # Draw hand indicators (simplificado)
    for hand in hands:
        if hand.get('raised', False):
            center = hand.get('center')
            if center:
                cv2.circle(frame, center, 15, (0, 255, 255), 2)
    
    # Draw participation associations (solo información esencial)
    if len(hand_associations) > 0:
        cv2.putText(frame, f"Participaciones: {len(hand_associations)}", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    
    # Draw statistics (siempre visible para debug)
    today_attendance = len(detection_results['attendance_today'])
    info_text = f"Asistencias: {today_attendance} | Rostros: {len(faces)}"
    cv2.putText(frame, info_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Mostrar estado del sistema
    status_text = f"Estado: {'ACTIVO' if len(faces) > 0 else 'BUSCANDO'}"
    cv2.putText(frame, status_text, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if len(faces) > 0 else (255, 255, 0), 1)
    
    # Mostrar timestamp para debug
    import time
    timestamp = time.strftime("%H:%M:%S")
    cv2.putText(frame, timestamp, (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
    
    return frame


@csrf_exempt
@require_http_methods(["POST"])
def start_detection(request):
    """Start camera detection"""
    global camera_thread, is_camera_running
    
    if not is_camera_running:
        camera_thread = threading.Thread(target=start_camera)
        camera_thread.daemon = True
        camera_thread.start()
        return JsonResponse({'status': 'started'})
    
    return JsonResponse({'status': 'already_running'})


@csrf_exempt
@require_http_methods(["POST"])
def stop_detection(request):
    """Stop camera detection"""
    global is_camera_running
    
    is_camera_running = False
    return JsonResponse({'status': 'stopped'})


@csrf_exempt
def detection_status(request):
    """Get current detection status and results"""
    return JsonResponse({
        'is_running': is_camera_running,
        'attendance_today': list(detection_results['attendance_today']),
        'participation_today': list(detection_results['participation_today']),
        'faces_detected': len(detection_results['faces']),
        'hands_detected': len([h for h in detection_results['hands'] if h['raised']])
    })


def person_list(request):
    """Redirect to new student list (legacy compatibility)"""
    return redirect('attendance:student_list')


def person_detail(request, person_id):
    """Redirect to student edit (legacy compatibility)"""
    return redirect('attendance:student_edit', pk=person_id)


def attendance_report(request):
    """Attendance report view"""
    today = date.today()
    date_filter = request.GET.get('date', today.strftime('%Y-%m-%d'))
    
    try:
        selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except:
        selected_date = today
    
    attendance_records = AttendanceRecord.objects.filter(
        date=selected_date
    ).select_related('person').order_by('-timestamp')
    
    context = {
        'attendance_records': attendance_records,
        'selected_date': selected_date,
        'total_attendance': attendance_records.count(),
    }
    
    return render(request, 'attendance/attendance_report.html', context)


def participation_report(request):
    """Participation report view"""
    today = date.today()
    date_filter = request.GET.get('date', today.strftime('%Y-%m-%d'))
    
    try:
        selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except:
        selected_date = today
    
    participation_records = ParticipationRecord.objects.filter(
        date=selected_date
    ).select_related('person').order_by('-timestamp')
    
    context = {
        'participation_records': participation_records,
        'selected_date': selected_date,
        'total_participation': participation_records.count(),
    }
    
    return render(request, 'attendance/participation_report.html', context)


# ======================== SISTEMA DE MATRÍCULA ========================

def student_register(request):
    """Vista para registrar nuevos estudiantes"""
    if request.method == 'POST':
        form = EstudianteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar estudiante
                    student = form.save()
                    
                    # Procesar foto si se subió
                    foto = form.cleaned_data.get('foto')
                    if foto:
                        # Crear PersonImage
                        person_image = PersonImage.objects.create(
                            person=student,
                            image=foto,
                            is_primary=True
                        )
                        
                        # Generar encoding facial
                        try:
                            global face_service
                            if not face_service:
                                face_service = FaceRecognitionService()
                            
                            encoding = face_service.generate_face_encoding(person_image.image.path)
                            if encoding is not None:
                                person_image.encoding = json.dumps(encoding.tolist())
                                person_image.save()
                                
                                # Recargar el servicio para incluir el nuevo encoding
                                face_service.load_encodings()
                                
                                messages.success(request, 
                                    f'¡Estudiante {student.nombre_completo} matriculado exitosamente! '
                                    f'Reconocimiento facial configurado.')
                            else:
                                messages.warning(request, 
                                    f'Estudiante {student.nombre_completo} matriculado, pero no se pudo '
                                    f'procesar el reconocimiento facial. Revise la foto.')
                        except Exception as e:
                            logger.error(f"Error generando encoding: {e}")
                            messages.warning(request, 
                                f'Estudiante {student.nombre_completo} matriculado, pero hubo un error '
                                f'procesando el reconocimiento facial.')
                    else:
                        messages.success(request, 
                            f'¡Estudiante {student.nombre_completo} matriculado exitosamente!')
                    
                    return redirect('attendance:student_list')
                    
            except Exception as e:
                logger.error(f"Error en matrícula: {e}")
                messages.error(request, 'Error al matricular estudiante. Intente nuevamente.')
                
    else:
        form = EstudianteForm()
    
    return render(request, 'attendance/matricula.html', {'form': form})


def student_list(request):
    """Vista para listar estudiantes con filtros y paginación"""
    students = Person.objects.prefetch_related('images').order_by('apellidos', 'nombres')
    
    # Filtros
    search = request.GET.get('search', '').strip()
    curso_filter = request.GET.get('curso', '').strip()
    aula_filter = request.GET.get('aula', '').strip()
    
    if search:
        students = students.filter(
            Q(nombres__icontains=search) |
            Q(apellidos__icontains=search) |
            Q(email__icontains=search) |
            Q(cedula__icontains=search)
        )
    
    if curso_filter:
        students = students.filter(curso=curso_filter)
    
    if aula_filter:
        students = students.filter(aula=aula_filter)
    
    # Paginación
    paginator = Paginator(students, 12)  # 12 estudiantes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_students = Person.objects.count()
    active_students = Person.objects.filter(is_active=True).count()
    total_courses = Person.objects.values('curso').distinct().count()
    with_photos = Person.objects.filter(images__isnull=False).distinct().count()
    
    # Listas para filtros
    cursos = Person.objects.values_list('curso', flat=True).distinct().order_by('curso')
    aulas = Person.objects.values_list('aula', flat=True).distinct().order_by('aula')
    
    context = {
        'students': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_students': total_students,
        'active_students': active_students,
        'total_courses': total_courses,
        'with_photos': with_photos,
        'cursos': cursos,
        'aulas': aulas,
    }
    
    return render(request, 'attendance/student_list.html', context)


def student_edit(request, pk):
    """Vista para editar estudiantes existentes"""
    student = get_object_or_404(Person, pk=pk)
    
    if request.method == 'POST':
        form = EstudianteForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar cambios del estudiante
                    updated_student = form.save()
                    
                    # Procesar nueva foto si se subió
                    foto = form.cleaned_data.get('foto')
                    if foto:
                        # Crear nueva PersonImage
                        person_image = PersonImage.objects.create(
                            person=updated_student,
                            image=foto,
                            is_primary=True
                        )
                        
                        # Desmarcar otras fotos como primarias
                        PersonImage.objects.filter(
                            person=updated_student
                        ).exclude(pk=person_image.pk).update(is_primary=False)
                        
                        # Generar nuevo encoding facial
                        try:
                            global face_service
                            if not face_service:
                                face_service = FaceRecognitionService()
                            
                            encoding = face_service.generate_face_encoding(person_image.image.path)
                            if encoding is not None:
                                person_image.encoding = json.dumps(encoding.tolist())
                                person_image.save()
                                
                                # Recargar encodings
                                face_service.load_encodings()
                                
                                messages.success(request, 
                                    f'¡Estudiante {updated_student.nombre_completo} actualizado exitosamente! '
                                    f'Nueva foto procesada para reconocimiento facial.')
                            else:
                                messages.warning(request, 
                                    f'Estudiante actualizado, pero no se pudo procesar la nueva foto.')
                        except Exception as e:
                            logger.error(f"Error generando encoding: {e}")
                            messages.warning(request, 
                                f'Estudiante actualizado, pero hubo un error procesando la nueva foto.')
                    else:
                        messages.success(request, 
                            f'¡Estudiante {updated_student.nombre_completo} actualizado exitosamente!')
                    
                    return redirect('attendance:student_list')
                    
            except Exception as e:
                logger.error(f"Error actualizando estudiante: {e}")
                messages.error(request, 'Error al actualizar estudiante. Intente nuevamente.')
                
    else:
        form = EstudianteForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
        'is_edit': True,
    }
    
    return render(request, 'attendance/matricula.html', context)


def student_delete(request, pk):
    """Vista para eliminar estudiantes"""
    student = get_object_or_404(Person, pk=pk)
    
    if request.method == 'POST':
        try:
            student_name = student.nombre_completo
            student.delete()
            
            # Recargar encodings después de eliminar
            global face_service
            if face_service:
                face_service.load_encodings()
            
            messages.success(request, f'Estudiante {student_name} eliminado exitosamente.')
        except Exception as e:
            logger.error(f"Error eliminando estudiante: {e}")
            messages.error(request, 'Error al eliminar estudiante.')
    
    return redirect('attendance:student_list')


# ======================== MÓDULO DE REPORTES AVANZADOS ========================

def reports_dashboard(request):
    """Vista unificada de reportes con tablas detalladas"""
    from django.db.models import Count, Q, Avg
    from datetime import timedelta
    
    # Parámetros de filtro
    today = date.today()
    date_from = request.GET.get('date_from', today.strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', today.strftime('%Y-%m-%d'))
    curso_filter = request.GET.get('curso', '')
    
    try:
        start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        start_date = end_date = today
    
    # Obtener estudiantes activos con estadísticas
    students_query = Person.objects.filter(is_active=True)
    if curso_filter:
        students_query = students_query.filter(curso=curso_filter)
    
    # Construir datos de la tabla principal
    students_data = []
    for student in students_query:
        # Contar asistencias en el período
        asistencias = AttendanceRecord.objects.filter(
            person=student,
            date__range=[start_date, end_date]
        ).count()
        
        # Contar participaciones en el período  
        participaciones = ParticipationRecord.objects.filter(
            person=student,
            date__range=[start_date, end_date]
        ).count()
        
        # Calcular días totales en el período
        total_days = (end_date - start_date).days + 1
        
        # Calcular porcentaje de asistencia
        asistencia_pct = round((asistencias / total_days * 100), 1) if total_days > 0 else 0
        
        # Determinar estado de asistencia
        if asistencias > 0:
            asistencia_status = "✅" 
            asistencia_class = "text-success"
        else:
            asistencia_status = "❌"
            asistencia_class = "text-danger"
        
        students_data.append({
            'id': student.id,
            'nombres': student.nombres,
            'apellidos': student.apellidos,
            'curso': student.curso,
            'aula': student.get_course_aula(),
            'email': student.email,
            'asistencias': asistencias,
            'participaciones': participaciones,
            'asistencia_pct': asistencia_pct,
            'asistencia_status': asistencia_status,
            'asistencia_class': asistencia_class,
            'foto': student.images.first()
        })
    
    # Ordenar por asistencia (mayor a menor)
    students_data.sort(key=lambda x: x['asistencia_pct'], reverse=True)
    
    # Estadísticas generales
    total_students = len(students_data)
    total_asistencias = sum(s['asistencias'] for s in students_data)
    total_participaciones = sum(s['participaciones'] for s in students_data)
    
    promedio_asistencia = round(sum(s['asistencia_pct'] for s in students_data) / total_students, 1) if total_students > 0 else 0
    
    # Registros recientes de asistencia (últimos 10)
    recent_attendance = AttendanceRecord.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('person').order_by('-timestamp')[:10]
    
    # Registros recientes de participación (últimos 10)
    recent_participation = ParticipationRecord.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('person').order_by('-timestamp')[:10]
    
    # Lista de cursos para filtro
    cursos = Person.objects.values_list('curso', flat=True).distinct().order_by('curso')
    
    context = {
        'students_data': students_data,
        'start_date': start_date,
        'end_date': end_date,
        'curso_filter': curso_filter,
        'cursos': cursos,
        'total_students': total_students,
        'total_asistencias': total_asistencias,
        'total_participaciones': total_participaciones,
        'promedio_asistencia': promedio_asistencia,
        'recent_attendance': recent_attendance,
        'recent_participation': recent_participation,
    }
    
    return render(request, 'attendance/reports_dashboard.html', context)


# ========================
# VISTAS DE CURSOS
# ========================

def course_list(request):
    """Lista de cursos con filtros y estadísticas"""
    # Filtros
    search = request.GET.get('search', '')
    
    # Obtener cursos
    courses_query = Course.objects.filter(is_active=True)
    
    if search:
        courses_query = courses_query.filter(
            Q(nombre__icontains=search) |
            Q(codigo__icontains=search) |
            Q(profesor__icontains=search)
        )
    
    courses = courses_query.order_by('nombre')
    
    # Agregar estadísticas de estudiantes a cada curso
    for course in courses:
        course.student_count = Person.objects.filter(
            curso=course.nombre, 
            is_active=True
        ).count()
    
    # Estadísticas generales
    total_courses = courses.count()
    active_courses = courses.filter(is_active=True).count()
    total_students = Person.objects.filter(is_active=True).count()
    
    # Paginación
    paginator = Paginator(courses, 12)  # 12 cursos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': page_obj,
        'search': search,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'total_students': total_students,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'attendance/course_list.html', context)


def course_create(request):
    """Crear nuevo curso"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            try:
                course = form.save()
                messages.success(
                    request, 
                    f'✅ Curso "{course.nombre}" creado exitosamente.'
                )
                return redirect('attendance:course_list')
            except Exception as e:
                messages.error(
                    request, 
                    f'❌ Error al crear el curso: {str(e)}'
                )
        else:
            messages.error(
                request, 
                '❌ Por favor corrige los errores en el formulario.'
            )
    else:
        form = CourseForm()
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Curso',
        'submit_text': 'Guardar Curso'
    }
    
    return render(request, 'attendance/course_form.html', context)


def course_edit(request, pk):
    """Editar curso existente"""
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            try:
                course = form.save()
                messages.success(
                    request, 
                    f'✅ Curso "{course.nombre}" actualizado exitosamente.'
                )
                return redirect('attendance:course_list')
            except Exception as e:
                messages.error(
                    request, 
                    f'❌ Error al actualizar el curso: {str(e)}'
                )
        else:
            messages.error(
                request, 
                '❌ Por favor corrige los errores en el formulario.'
            )
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'course': course,
        'title': f'Editar Curso: {course.nombre}',
        'submit_text': 'Guardar Cambios'
    }
    
    return render(request, 'attendance/course_form.html', context)


def course_delete(request, pk):
    """Eliminar curso (marcar como inactivo)"""
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si tiene estudiantes asociados
            student_count = Person.objects.filter(curso=course.nombre, is_active=True).count()
            
            if student_count > 0:
                messages.warning(
                    request,
                    f'⚠️ No se puede eliminar el curso "{course.nombre}" porque tiene {student_count} estudiantes asociados.'
                )
            else:
                course.is_active = False
                course.save()
                messages.success(
                    request,
                    f'✅ Curso "{course.nombre}" eliminado exitosamente.'
                )
        except Exception as e:
            messages.error(
                request,
                f'❌ Error al eliminar el curso: {str(e)}'
            )
    
    return redirect('attendance:course_list')


def management_dashboard(request):
    """Dashboard de gestión general"""
    from django.db import models
    
    # Estadísticas generales
    total_students = Person.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    students_with_photos = Person.objects.filter(
        is_active=True,
        images__isnull=False
    ).distinct().count()
    students_without_photos = total_students - students_with_photos
    
    # Cursos más populares (simulado por ahora)
    popular_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:5]
    for course in popular_courses:
        course.student_count = Person.objects.filter(
            curso=course.nombre, 
            is_active=True
        ).count()
    
    # Registros recientes
    recent_students = Person.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'students_with_photos': students_with_photos,
        'students_without_photos': students_without_photos,
        'popular_courses': popular_courses,
        'recent_students': recent_students,
        'recent_courses': recent_courses,
    }
    
    return render(request, 'attendance/management_dashboard.html', context)


def login_view(request):
    """Vista de login personalizada"""
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('attendance:home')
        else:
            return render(request, 'attendance/login.html', {
                'error_message': 'Usuario o contraseña incorrectos'
            })
    
    return render(request, 'attendance/login.html')


def logout_view(request):
    """Vista de logout"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('attendance:login')


def index_view(request):
    """Vista de índice que redirige según el estado de autenticación"""
    if request.user.is_authenticated:
        return redirect('attendance:home')
    else:
        return redirect('attendance:login')
