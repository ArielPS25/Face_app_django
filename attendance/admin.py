from django.contrib import admin
from django.utils.html import format_html
from .models import Person, PersonImage, AttendanceRecord, ParticipationRecord, Session, Course


class PersonImageInline(admin.TabularInline):
    model = PersonImage
    extra = 1
    readonly_fields = ('uploaded_at', 'encoding')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'created_at', 'image_count', 'attendance_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at',)
    inlines = [PersonImageInline]
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'
    
    def attendance_count(self, obj):
        return obj.attendance_records.count()
    attendance_count.short_description = 'Attendance Records'


@admin.register(PersonImage)
class PersonImageAdmin(admin.ModelAdmin):
    list_display = ('person', 'is_primary', 'uploaded_at', 'has_encoding', 'image_preview')
    list_filter = ('is_primary', 'uploaded_at', 'person')
    search_fields = ('person__name',)
    readonly_fields = ('uploaded_at', 'encoding', 'image_preview')
    
    def has_encoding(self, obj):
        return bool(obj.encoding)
    has_encoding.boolean = True
    has_encoding.short_description = 'Has Encoding'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Preview'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('person', 'date', 'timestamp', 'confidence', 'notes')
    list_filter = ('date', 'timestamp')
    search_fields = ('person__name',)
    readonly_fields = ('timestamp', 'date')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('person')


@admin.register(ParticipationRecord)
class ParticipationRecordAdmin(admin.ModelAdmin):
    list_display = ('person', 'participation_type', 'date', 'timestamp', 'confidence')
    list_filter = ('participation_type', 'date', 'timestamp')
    search_fields = ('person__name',)
    readonly_fields = ('timestamp', 'date')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('person')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'start_time', 'end_time', 'is_active', 'created_by', 'attendance_count', 'participation_count')
    list_filter = ('is_active', 'date', 'created_by')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'attendance_count', 'participation_count')
    
    def attendance_count(self, obj):
        return obj.get_attendance_count()
    attendance_count.short_description = 'Attendees'
    
    def participation_count(self, obj):
        return obj.get_participation_count()
    participation_count.short_description = 'Participations'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'profesor', 'aula', 'horario', 'is_active', 'student_count', 'created_at')
    list_filter = ('is_active', 'aula', 'sesion', 'created_at')
    search_fields = ('nombre', 'codigo', 'profesor', 'aula')
    readonly_fields = ('created_at', 'updated_at', 'student_count')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'descripcion')
        }),
        ('Detalles Académicos', {
            'fields': ('profesor', 'aula', 'sesion', 'horario')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Información del Sistema', {
            'fields': ('student_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def student_count(self, obj):
        count = obj.get_student_count()
        if count > 0:
            return format_html(
                '<strong style="color: green;">{} estudiantes</strong>',
                count
            )
        return format_html('<span style="color: gray;">Sin estudiantes</span>')
    student_count.short_description = 'Estudiantes Matriculados'
