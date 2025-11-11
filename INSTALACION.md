# 🚀 GUÍA DE INSTALACIÓN - Django Face Recognition System

## 📋 Requisitos del Sistema

### ✅ **Software Necesario:**
- **Python 3.8 - 3.11** (Recomendado: 3.11)
- **Git** (para clonar el repositorio)
- **Visual Studio Build Tools** (Windows)
- **CMake** (para compilar dlib)

### 🖥️ **Sistemas Operativos Soportados:**
- Windows 10/11
- Ubuntu 18.04+
- macOS 10.14+

---

## ⚡ INSTALACIÓN RÁPIDA

### 🪟 **Windows (Automática):**
```cmd
git clone https://github.com/ArielPS25/Face_app_django.git
cd Face_app_django
install.bat
```

### 🐧 **Linux/macOS (Automática):**
```bash
git clone https://github.com/ArielPS25/Face_app_django.git
cd Face_app_django
chmod +x install.sh
./install.sh
```

---

## 🔧 INSTALACIÓN MANUAL

### 1️⃣ **Clonar Repositorio:**
```bash
git clone https://github.com/ArielPS25/Face_app_django.git
cd Face_app_django
```

### 2️⃣ **Crear Entorno Virtual:**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS  
source .venv/bin/activate
```

### 3️⃣ **Instalar Dependencias:**

#### **Opción A - Instalación Completa:**
```bash
pip install --upgrade pip
pip install cmake wheel setuptools
pip install -r requirements.txt
```

#### **Opción B - Si hay problemas con dlib:**
```bash
pip install -r requirements-minimal.txt
```

### 4️⃣ **Configurar Base de Datos:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5️⃣ **Ejecutar Servidor:**
```bash
python manage.py runserver
```

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### ❌ **Error: dlib no se puede instalar**

#### **Windows:**
```cmd
# Instalar Visual Studio Build Tools
# Descargar desde: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Instalar CMake
pip install cmake

# Instalar dlib específicamente
pip install dlib==19.24.0

# Si sigue fallando, usar wheel precompilado:
# Descargar desde https://pypi.org/project/dlib/#files
pip install dlib-19.24.0-cp311-cp311-win_amd64.whl
```

#### **Ubuntu/Debian:**
```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libpng-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libgtk2.0-dev libcanberra-gtk-module
sudo apt-get install python3-dev

# Instalar dlib
pip install dlib==19.24.0
```

#### **macOS:**
```bash
# Instalar Homebrew (si no está instalado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependencias
brew install cmake pkg-config

# Instalar dlib
pip install dlib==19.24.0
```

### ❌ **Error: mysqlclient no se puede instalar**

#### **Windows:**
```cmd
# Usar alternativo
pip uninstall mysqlclient
pip install mysql-connector-python==9.5.0
```

#### **Ubuntu/Debian:**
```bash
sudo apt-get install default-libmysqlclient-dev
pip install mysqlclient
```

#### **macOS:**
```bash
brew install mysql
pip install mysqlclient
```

### ❌ **Error: OpenCV no funciona**
```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python==4.10.0.84
```

---

## 🗄️ CONFIGURACIÓN DE BASE DE DATOS

### **SQLite (Por Defecto):**
```bash
# No requiere configuración adicional
python manage.py migrate
```

### **MySQL (Producción):**
```bash
# Activar MySQL
export USE_MYSQL=true  # Linux/macOS
set USE_MYSQL=true     # Windows

# Configurar variables (opcional)
export MYSQL_HOST=tu-host-rds.amazonaws.com
export MYSQL_DATABASE=tu_base_datos
export MYSQL_USER=tu_usuario
export MYSQL_PASSWORD=tu_password

python manage.py migrate
```

---

## 📦 VERSIONES DE DEPENDENCIAS

### **Principales:**
- Django: 5.2.8
- OpenCV: 4.12.0.88
- dlib: 19.24.0 ⚠️ (Versión problemática: 20.0.0)
- face-recognition: 1.3.0
- mediapipe: 0.10.21
- numpy: 1.26.4

### **Base de Datos:**
- mysqlclient: 2.2.7 (MySQL)
- mysql-connector-python: 9.5.0 (Alternativo)

---

## 🎯 VERIFICACIÓN DE INSTALACIÓN

```bash
# Verificar Python
python --version

# Verificar Django
python -c "import django; print(django.get_version())"

# Verificar OpenCV
python -c "import cv2; print(cv2.__version__)"

# Verificar dlib
python -c "import dlib; print('dlib OK')"

# Verificar face_recognition
python -c "import face_recognition; print('face_recognition OK')"

# Ejecutar diagnóstico completo
python config_dashboard.py
```

---

## 🔄 CAMBIO ENTRE BASES DE DATOS

### **Scripts Automáticos:**
```cmd
# Windows
use_mysql.bat    # Activa MySQL
use_sqlite.bat   # Activa SQLite

# Manual
set USE_MYSQL=true   # MySQL
set USE_MYSQL=false  # SQLite
```

---

## 🚀 PRIMEROS PASOS

1. **Acceder al sistema:** http://127.0.0.1:8000/
2. **Panel de administración:** http://127.0.0.1:8000/admin/
3. **Cargar imágenes:** Admin > Persons > Add Person > Upload Images
4. **Probar cámara:** http://127.0.0.1:8000/camera/

---

## 📞 SOPORTE

### **Problemas Comunes:**
- **dlib no compila:** Usar `requirements-minimal.txt`
- **MySQL no conecta:** Verificar credenciales en `settings.py`
- **Cámara no funciona:** Verificar permisos del navegador

### **Recursos:**
- **Repositorio:** https://github.com/ArielPS25/Face_app_django
- **Issues:** Reportar problemas en GitHub
- **Documentación:** Ver archivos `.md` en el proyecto

---

**🎉 ¡Tu sistema Django Face Recognition está listo para usar!**