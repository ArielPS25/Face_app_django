from django import forms
from django.core.exceptions import ValidationError
from .models import Person, PersonImage, Session, AttendanceRecord, ParticipationRecord, Course


class CourseForm(forms.ModelForm):
    """Formulario para crear y editar cursos"""
    
    class Meta:
        model = Course
        fields = ['nombre', 'descripcion', 'aula', 'sesion', 'profesor', 'horario']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Matemáticas Avanzadas',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del curso...'
            }),
            'aula': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'sesion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'min': '1',
                'max': '10',
                'step': '1'
            }),
            'profesor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del profesor',
                'required': True
            }),
            'horario': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            })
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            nombre = nombre.strip()
            # Verificar si ya existe (excluyendo la instancia actual si es edición)
            existing = Course.objects.filter(nombre=nombre)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Ya existe un curso con este nombre.")
        return nombre
    



class EstudianteForm(forms.ModelForm):
    """Formulario para matriculación de estudiantes"""
    
    foto = forms.ImageField(
        required=False,
        help_text="Subir foto del estudiante para reconocimiento facial",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'foto-input'
        })
    )
    
    curso = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        empty_label="-- Seleccione un curso --",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        help_text="Seleccione el curso al que pertenece el estudiante"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un estudiante existente, seleccionar el curso correcto
        if self.instance.pk and self.instance.curso:
            try:
                course = Course.objects.get(nombre=self.instance.curso)
                self.fields['curso'].initial = course
            except Course.DoesNotExist:
                pass
    
    class Meta:
        model = Person
        fields = ['nombres', 'apellidos', 'cedula', 'curso', 'email']
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Juan Carlos',
                'required': True
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: García López',
                'required': True
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1234567890',
                'maxlength': '20'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'estudiante@colegio.edu.ec',
                'required': True
            }),

        }
    
    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if nombres:
            nombres = nombres.strip().title()
            if len(nombres) < 2:
                raise ValidationError("Los nombres deben tener al menos 2 caracteres.")
        return nombres
    
    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if apellidos:
            apellidos = apellidos.strip().title()
            if len(apellidos) < 2:
                raise ValidationError("Los apellidos deben tener al menos 2 caracteres.")
        return apellidos
    
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula:
            cedula = cedula.strip()
            # Verificar si ya existe (excluyendo la instancia actual si es edición)
            existing = Person.objects.filter(cedula=cedula)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Ya existe un estudiante con esta cédula.")
        return cedula
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Verificar si ya existe (excluyendo la instancia actual si es edición)
            existing = Person.objects.filter(email=email)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Ya existe un estudiante con este email.")
        return email
    
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto:
            # Validar tamaño (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError("La imagen es muy grande. Máximo 5MB.")
            
            # Validar tipo de archivo
            if not foto.content_type.startswith('image/'):
                raise ValidationError("El archivo debe ser una imagen.")
                
        return foto
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convertir el Course seleccionado a string para guardarlo en el campo curso
        curso_obj = self.cleaned_data.get('curso')
        if curso_obj:
            instance.curso = curso_obj.nombre
        
        if commit:
            instance.save()
        return instance


class PersonForm(forms.ModelForm):
    """Form for adding/editing persons (legacy compatibility)"""
    
    class Meta:
        model = Person
        fields = ['nombres', 'apellidos', 'email', 'is_active']
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
        }


class PersonImageForm(forms.ModelForm):
    """Form for uploading person images"""
    
    class Meta:
        model = PersonImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 5MB.")
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
        
        return image


class SessionForm(forms.ModelForm):
    """Form for creating/editing sessions"""
    
    class Meta:
        model = Session
        fields = ['name', 'date', 'start_time', 'end_time']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter session name'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")
        
        return cleaned_data


class AttendanceReportForm(forms.Form):
    """Form for filtering attendance reports"""
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    person = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError("End date must be after start date.")
        
        return cleaned_data


class ParticipationReportForm(forms.Form):
    """Form for filtering participation reports"""
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    person = forms.ModelChoiceField(
        queryset=Person.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    participation_type = forms.ChoiceField(
        choices=[('', 'All Types')] + ParticipationRecord.PARTICIPATION_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )