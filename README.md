# Django Face Recognition Attendance System

A comprehensive web-based attendance and participation tracking system using facial recognition and hand gesture detection.

## Features

- **Facial Recognition**: Automatic attendance marking using OpenCV and face_recognition
- **Hand Gesture Detection**: Real-time participation tracking with MediaPipe
- **Web Interface**: Modern, responsive Django web application
- **Real-time Camera Feed**: Live video processing with detection overlays
- **Data Management**: Complete CRUD operations for persons, attendance, and participation
- **Reporting**: Detailed attendance and participation reports with filtering
- **Admin Panel**: Full Django admin interface for data management
- **CSV Export**: Export attendance and participation data

## Technology Stack

- **Backend**: Django 5.2+, Python 3.11+
- **Computer Vision**: OpenCV, face_recognition, MediaPipe
- **Frontend**: Bootstrap 5, jQuery, HTML5/CSS3
- **Database**: SQLite (default, configurable)
- **Additional**: Pandas for data processing, Pillow for image handling

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Webcam for real-time detection
- Git (for cloning the repository)

### Step 1: Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd django_face_app

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install django opencv-python face_recognition mediapipe pandas pillow
```

### Step 3: Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 4: Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

## Usage Guide

### Initial Setup

1. **Access Admin Panel**: Go to `http://127.0.0.1:8000/admin/` and log in with your superuser credentials
2. **Add Persons**: Create person records in the admin panel
3. **Upload Photos**: Add multiple photos for each person to improve recognition accuracy
4. **Start Detection**: Go to the Camera page and click "Start Detection"

### Main Features

#### Dashboard
- View real-time statistics
- Quick access to all features
- Recent attendance and participation

#### Camera Detection
- Real-time face recognition
- Hand gesture detection for participation
- Live statistics and recent activity
- Start/stop detection controls

#### Person Management
- Add/edit person information
- Upload multiple face images
- View attendance history

#### Reports
- Attendance reports with date filtering
- Participation reports with type filtering
- Export functionality (CSV)

### Face Recognition Setup

1. **Add Person Images**:
   - Upload 2-3 clear photos per person
   - Ensure good lighting and face visibility
   - Mark one image as primary

2. **Detection Process**:
   - Face encodings are automatically generated
   - Recognition requires 1 second of continuous detection
   - Attendance is marked once per day per person

### Hand Gesture Detection

- **Raise Hand**: Open palm facing camera in vertical position
- **Participation Types**: Hand raised, question, answer, comment
- **Cooldown**: 30-second interval between participations

## API Endpoints

- `GET /` - Dashboard
- `GET /camera/` - Camera interface
- `GET /camera/feed/` - Video stream
- `POST /api/start-detection/` - Start camera detection
- `POST /api/stop-detection/` - Stop camera detection
- `GET /api/detection-status/` - Get detection status
- `GET /persons/` - Person list
- `GET /reports/attendance/` - Attendance reports
- `GET /reports/participation/` - Participation reports

## Configuration

### Settings (face_attendance_system/settings.py)

- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: Configure for deployment
- `DATABASES`: Configure database settings
- `STATIC_ROOT`: Set for production static files

### Detection Parameters

Adjust detection parameters in the service files:

- `MIN_CONFIDENCE_TIME`: Face detection confirmation time (default: 1s)
- `PARTICIPATION_COOLDOWN`: Time between participations (default: 30s)
- `VIDEO_SCALE`: Frame scaling for performance (default: 0.25)

## Troubleshooting

### Common Issues

1. **Camera Access**: Ensure webcam permissions are granted
2. **Face Recognition**: Add more photos if recognition is poor
3. **Hand Detection**: Ensure good lighting and clear hand visibility
4. **Performance**: Adjust video scaling if detection is slow

### Error Handling

- Check console logs for detailed error messages
- Verify all dependencies are installed correctly
- Ensure camera is not being used by another application

## Development

### Project Structure

```
django_face_app/
├── face_attendance_system/     # Django project settings
├── attendance/                 # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View logic
│   ├── services.py            # Face/hand detection services
│   ├── forms.py               # Django forms
│   ├── admin.py               # Admin configuration
│   └── templates/             # HTML templates
├── static/                    # Static files (CSS, JS)
├── media/                     # User uploaded files
└── manage.py                  # Django management script
```

### Adding New Features

1. **Models**: Add new models in `attendance/models.py`
2. **Views**: Create views in `attendance/views.py`
3. **Templates**: Add HTML templates in `attendance/templates/`
4. **URLs**: Configure URLs in `attendance/urls.py`
5. **Services**: Extend detection services in `attendance/services.py`

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up proper database (PostgreSQL/MySQL)
- [ ] Configure static files serving
- [ ] Set up media files serving
- [ ] Configure logging
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall and security

### Environment Variables

```bash
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
1. Check the troubleshooting section
2. Review the Django documentation
3. Check OpenCV and MediaPipe documentation
4. Create an issue in the project repository

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Note**: This system is designed for educational and small-scale use. For production environments, consider additional security measures, performance optimizations, and scalability requirements.