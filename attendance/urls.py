from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Index and authentication
    path('', views.index_view, name='index'),
    
    # Home and dashboard  
    path('home/', views.home, name='home'),
    
    # Camera and detection
    path('camera/', views.camera_view, name='camera'),
    path('camera/feed/', views.camera_feed, name='camera_feed'),
    path('api/start-detection/', views.start_detection, name='start_detection'),
    path('api/stop-detection/', views.stop_detection, name='stop_detection'),
    path('api/detection-status/', views.detection_status, name='detection_status'),
    
    # Person management
    path('persons/', views.person_list, name='person_list'),
    path('persons/<int:person_id>/', views.person_detail, name='person_detail'),
    
    # Student management (Sistema de Matrícula)
    path('students/', views.student_list, name='student_list'),
    path('students/register/', views.student_register, name='student_register'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Management dashboard
    path('management/', views.management_dashboard, name='management_dashboard'),
    
    # Course management
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/participation/', views.participation_report, name='participation_report'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]