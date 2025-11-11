#!/bin/bash
# ===============================================
# INSTALADOR DJANGO FACE RECOGNITION SYSTEM
# Para Linux/macOS
# ===============================================

echo "==============================================="
echo "🚀 INSTALADOR DJANGO FACE RECOGNITION SYSTEM"
echo "==============================================="

# Verificar Python
echo "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    python3 --version
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    python --version
    PYTHON_CMD="python"
else
    echo "❌ Error: Python no está instalado"
    echo "📝 Instala Python 3.8-3.11"
    exit 1
fi

# Crear entorno virtual
echo ""
echo "📁 Creando entorno virtual..."
if [ -d ".venv" ]; then
    echo "⚠️  El entorno virtual ya existe"
else
    $PYTHON_CMD -m venv .venv
    echo "✅ Entorno virtual creado"
fi

# Activar entorno virtual
echo ""
echo "🔌 Activando entorno virtual..."
source .venv/bin/activate

# Actualizar pip
echo ""
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias básicas
echo ""
echo "📋 Instalando dependencias básicas..."

# Para Linux, instalar dependencias del sistema si es necesario
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detectado Linux - verificando dependencias del sistema..."
    
    # Verificar si apt está disponible (Ubuntu/Debian)
    if command -v apt-get &> /dev/null; then
        echo "📦 Para instalar dependencias del sistema, ejecuta:"
        echo "   sudo apt-get update"
        echo "   sudo apt-get install build-essential cmake pkg-config"
        echo "   sudo apt-get install libjpeg-dev libtiff5-dev libpng-dev"
        echo "   sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev"
        echo "   sudo apt-get install libgtk2.0-dev libcanberra-gtk-module"
        echo "   sudo apt-get install libxvidcore-dev libx264-dev"
        echo "   sudo apt-get install python3-dev python3-pip python3-venv"
        echo "   sudo apt-get install default-libmysqlclient-dev"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detectado macOS"
    if command -v brew &> /dev/null; then
        echo "🍺 Homebrew detectado - instalando dependencias..."
        brew install cmake pkg-config mysql
    else
        echo "📦 Instala Homebrew y luego ejecuta:"
        echo "   brew install cmake pkg-config mysql"
    fi
fi

pip install cmake wheel setuptools

# Instalar requirements
echo ""
echo "🎯 Instalando requirements..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Hubo errores en la instalación"
    echo "🔧 Intentando instalación alternativa para dlib..."
    
    pip install dlib==19.24.0
    pip install -r requirements.txt
fi

# Configurar base de datos
echo ""
echo "🗄️  Configurando base de datos..."
python manage.py migrate

# Crear superusuario
echo ""
echo "👤 ¿Quieres crear un superusuario? (s/n)"
read -r create_user
if [[ $create_user == "s" || $create_user == "S" ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "==============================================="
echo "✅ INSTALACIÓN COMPLETADA"
echo "==============================================="
echo ""
echo "📝 Comandos útiles:"
echo "   Activar entorno: source .venv/bin/activate"
echo "   Ejecutar servidor: python manage.py runserver"
echo "   Panel admin: http://127.0.0.1:8000/admin/"
echo ""
echo "🎉 ¡Tu sistema está listo!"