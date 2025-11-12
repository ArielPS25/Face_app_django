# CONFIGURACIÓN EXACTA DEL ENTORNO DE DESARROLLO

## ⚠️ REQUISITOS CRÍTICOS

### Versión de Python
- **USAR OBLIGATORIAMENTE: Python 3.11.9**
- **NO USAR: Python 3.13.x** (causa conflictos con face_recognition y dlib)

### Sistema Operativo
- Windows 10/11
- Visual Studio Build Tools instalado (para compilar dlib)

## 🚀 INSTALACIÓN PASO A PASO

### Opción 1: Script Automático
```bash
# Ejecutar el script de instalación
setup-exact-environment.bat
```

### Opción 2: Manual
```bash
# 1. Crear entorno virtual con Python 3.11
python -m venv .venv

# 2. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 3. Actualizar pip
python -m pip install --upgrade pip

# 4. Instalar dependencias exactas
pip install -r requirements-working.txt

# 5. Si hay problemas con dlib, usar el wheel local
pip install dlib-20.0.0-cp311-cp311-win_amd64.whl
```

## 📦 DEPENDENCIAS PRINCIPALES

### Core Framework
- Django==5.2.8
- django-widget-tweaks==1.5.0

### Computer Vision
- opencv-python==4.12.0.88
- opencv-contrib-python==4.11.0.86
- face-recognition==1.3.0
- dlib==20.0.0
- mediapipe==0.10.21

### Data Processing
- numpy==1.26.4
- pandas==2.3.3
- pillow==12.0.0

### Database
- mysql-connector-python==9.5.0
- mysqlclient==2.2.7

## 🔧 SOLUCIÓN DE PROBLEMAS COMUNES

### Error con dlib
Si falla la instalación de dlib:
```bash
pip install dlib-20.0.0-cp311-cp311-win_amd64.whl
```

### Error con face_recognition
Asegúrate de tener Python 3.11.x:
```bash
python --version  # Debe mostrar 3.11.x
```

### Error con OpenCV
Si hay conflictos de versiones:
```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python==4.12.0.88
pip install opencv-contrib-python==4.11.0.86
```

## 🏃‍♂️ EJECUCIÓN

```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Ejecutar servidor de desarrollo
python manage.py runserver

# O usar la tarea configurada
# Ctrl+Shift+P -> "Tasks: Run Task" -> "Django Development Server"
```

## 📋 VERIFICACIÓN DE INSTALACIÓN

```bash
# Verificar Python
python --version  # Debe ser 3.11.9

# Verificar Django
python -c "import django; print(django.__version__)"  # 5.2.8

# Verificar OpenCV
python -c "import cv2; print(cv2.__version__)"  # 4.12.0

# Verificar face_recognition
python -c "import face_recognition; print('face_recognition OK')"

# Verificar mediapipe
python -c "import mediapipe; print('mediapipe OK')"
```

## 🎯 PARA OTRAS PC

1. **Instalar Python 3.11.9** desde https://www.python.org/downloads/release/python-3119/
2. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/ArielPS25/Face_app_django.git
   cd Face_app_django
   ```
3. **Ejecutar setup**:
   ```bash
   setup-exact-environment.bat
   ```
4. **Verificar instalación**:
   ```bash
   verify_installation.py
   ```

## 📝 NOTAS IMPORTANTES

- Este entorno ha sido probado y funciona correctamente en la laptop de desarrollo
- Las versiones están fijadas para evitar conflictos de compatibilidad  
- NO actualizar dependencias sin probar exhaustivamente
- Mantener Python 3.11.x hasta que todas las librerías soporten 3.13