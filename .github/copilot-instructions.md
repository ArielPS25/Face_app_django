# Django Face Recognition Attendance System

This is a Django web application for managing attendance and participation using facial recognition and hand gesture detection.

## Project Structure
- Django web framework with attendance app
- Face recognition using OpenCV and face_recognition library  
- Hand gesture detection with MediaPipe
- Real-time camera feed processing with threading
- Attendance and participation tracking with database models
- CSV export functionality and comprehensive reporting

## Key Features
- Facial recognition for automatic attendance marking
- Hand gesture detection for participation tracking
- Real-time video processing with detection overlays
- Web-based interface with Bootstrap 5 styling
- Data export capabilities and filtering
- User management and detailed reporting
- Django admin panel for full data management

## Technology Stack
- Django 5.2+ (Python web framework)
- OpenCV (computer vision and video processing)
- face_recognition (facial recognition library)
- MediaPipe (hand gesture detection)
- pandas (data processing and CSV export)
- Bootstrap 5 (responsive frontend framework)
- jQuery (JavaScript interactions)
- SQLite database (configurable to other databases)

## Setup Requirements
- Python 3.11+
- Django 5.2+
- OpenCV, face_recognition, mediapipe, pandas, pillow
- Webcam access for real-time functionality
- Modern web browser with WebRTC support

## Usage
1. Run `python manage.py runserver` to start development server
2. Access admin panel at `/admin/` (admin:admin123)
3. Add persons and upload face images in admin
4. Use camera interface for live detection
5. View reports and export data as needed

## Development Notes
- Face encodings are generated automatically and stored as JSON
- Threading is used for real-time camera processing
- Detection cooldowns prevent duplicate registrations
- Responsive design works on desktop and mobile devices