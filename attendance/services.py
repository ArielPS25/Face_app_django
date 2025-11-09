import cv2
import face_recognition
import numpy as np
import json
import logging
from django.conf import settings
from .models import Person, PersonImage
import mediapipe as mp

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    """Service for handling face recognition operations"""
    
    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.known_person_ids = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all known face encodings from database"""
        self.known_encodings = []
        self.known_names = []
        self.known_person_ids = []
        
        try:
            person_images = PersonImage.objects.select_related('person').filter(
                person__is_active=True
            )
            
            for person_image in person_images:
                if person_image.encoding:
                    try:
                        encoding = np.array(json.loads(person_image.encoding))
                        self.known_encodings.append(encoding)
                        self.known_names.append(person_image.person.name)
                        self.known_person_ids.append(person_image.person.id)
                        logger.debug(f"Loaded encoding for {person_image.person.name}")
                    except Exception as e:
                        logger.error(f"Error loading encoding for {person_image.person.name}: {e}")
            
            logger.info(f"Loaded {len(self.known_encodings)} face encodings")
            
        except Exception as e:
            logger.error(f"Error loading known faces: {e}")
    
    def generate_encoding(self, image_path):
        """Generate face encoding from image file"""
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                return encodings[0].tolist()  # Convert to list for JSON serialization
            else:
                logger.warning(f"No face found in image: {image_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating encoding for {image_path}: {e}")
            return None
    
    def recognize_face(self, frame):
        """Recognize faces in a video frame - balanced performance"""
        # Configuración balanceada para rendimiento y precisión
        VIDEO_SCALE = 0.25  # Mantener resolución balanceada
        
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=VIDEO_SCALE, fy=VIDEO_SCALE)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find faces con configuración balanceada
        face_locations = face_recognition.face_locations(
            rgb_small_frame, 
            model='hog'  # Mantener modelo HOG pero sin restricciones excesivas
        )
        
        # Limitar a máximo 5 rostros por frame (más flexible)
        if len(face_locations) > 5:
            face_locations = face_locations[:5]
        
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_faces = []
        
        for face_encoding in face_encodings:
            # Compare with known faces con tolerancia optimizada
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            name = "Unknown"
            person_id = None
            confidence = 0.0
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_names[best_match_index]
                    person_id = self.known_person_ids[best_match_index]
                    confidence = 1.0 - face_distances[best_match_index]
            
            recognized_faces.append({
                'name': name,
                'person_id': person_id,
                'confidence': confidence
            })
        
        # Scale face locations back up (usar 1/VIDEO_SCALE)
        scaled_face_locations = []
        scale_factor = int(1 / VIDEO_SCALE)
        for (top, right, bottom, left) in face_locations:
            scaled_face_locations.append((
                top * scale_factor, 
                right * scale_factor, 
                bottom * scale_factor, 
                left * scale_factor
            ))
        
        return recognized_faces, scaled_face_locations


class HandGestureService:
    """Service for hand gesture detection using MediaPipe"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        # Configuración optimizada basada en el código funcional
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.3  # Reducido para mejor tracking
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_hand_raised(self, frame):
        """Detect if a hand is raised in the frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hands_detected = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Check if hand is raised
                if self._is_hand_raised(hand_landmarks):
                    # Get hand position
                    hand_center = self._get_hand_center(hand_landmarks, frame.shape)
                    hands_detected.append({
                        'landmarks': hand_landmarks,
                        'center': hand_center,
                        'raised': True
                    })
        
        return hands_detected, results
    
    def _is_hand_raised(self, hand_landmarks):
        """Check if the hand is in a raised position - improved algorithm"""
        if not hand_landmarks:
            return False

        landmarks = hand_landmarks.landmark
        
        # Key points: wrist and fingertips
        wrist = landmarks[0]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Usar margen más generoso para mejor detección (como en tu código)
        margen = 0.05  # 5% de margen adicional
        
        # Verificar si los dedos principales están arriba de la muñeca
        dedos_arriba = [
            index_tip.y < (wrist.y - margen),    # Índice
            middle_tip.y < (wrist.y - margen),   # Medio
            ring_tip.y < (wrist.y - margen),     # Anular
        ]
        
        # También verificar que la mano esté en posición vertical (no horizontal)
        altura_mano = abs(wrist.y - middle_tip.y)
        ancho_mano = abs(landmarks[5].x - landmarks[17].x)  # Base de índice a base de meñique
        
        es_vertical = altura_mano > ancho_mano * 0.7
        
        # Condiciones para mano levantada:
        # 1. Al menos 2 dedos principales arriba de la muñeca
        # 2. La mano está en posición más vertical que horizontal
        dedos_levantados = sum(dedos_arriba)
        
        resultado = dedos_levantados >= 2 and es_vertical
        
        # Debug: imprimir información cuando se detecta
        if resultado:
            logger.debug(f"Mano levantada detectada: {dedos_levantados}/3 dedos arriba, vertical: {es_vertical}")
        
        return resultado
    
    def _get_hand_center(self, hand_landmarks, frame_shape):
        """Get the center position of the hand"""
        x_coords = [lm.x for lm in hand_landmarks.landmark]
        y_coords = [lm.y for lm in hand_landmarks.landmark]
        
        center_x = int(np.mean(x_coords) * frame_shape[1])
        center_y = int(np.mean(y_coords) * frame_shape[0])
        
        return (center_x, center_y)
    
    def associate_hand_with_face(self, hands, face_locations, recognized_faces):
        """Associate detected hands with recognized faces"""
        associations = []
        
        for i, hand in enumerate(hands):
            if not hand['raised']:
                continue
                
            hand_center = hand['center']
            min_distance = float('inf')
            associated_face = None
            
            for j, (top, right, bottom, left) in enumerate(face_locations):
                if j < len(recognized_faces) and recognized_faces[j]['person_id'] is not None:
                    # Calculate face center
                    face_center_x = (left + right) // 2
                    face_center_y = (top + bottom) // 2
                    
                    # Calculate distance
                    distance = np.sqrt(
                        (hand_center[0] - face_center_x) ** 2 + 
                        (hand_center[1] - face_center_y) ** 2
                    )
                    
                    if distance < min_distance and distance < 300:  # Max 300 pixels
                        min_distance = distance
                        associated_face = recognized_faces[j]
            
            if associated_face:
                associations.append({
                    'person_id': associated_face['person_id'],
                    'person_name': associated_face['name'],
                    'hand_center': hand_center,
                    'confidence': 1.0 - (min_distance / 300)  # Normalize confidence
                })
        
        return associations
    
    def draw_hand_landmarks(self, frame, results):
        """Draw hand landmarks on frame"""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
        return frame