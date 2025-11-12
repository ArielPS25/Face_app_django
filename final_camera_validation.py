#!/usr/bin/env python3
"""
Prueba final completa de funcionalidad de cámara
"""

import os
import sys
import time
from datetime import datetime

def print_header(title):
    """Imprimir header decorativo"""
    border = "=" * 70
    print(f"\n{border}")
    print(f"  {title}")
    print(f"{border}")

def print_status(component, status, details=""):
    """Imprimir estado con iconos"""
    icon = "✅" if status else "❌"
    print(f"{icon} {component}")
    if details:
        print(f"   📝 {details}")

def check_file_structure():
    """Verificar estructura de archivos"""
    print_header("📁 VERIFICANDO ESTRUCTURA DE ARCHIVOS")
    
    required_files = {
        "Template matrícula": "attendance/templates/attendance/matricula.html",
        "Views backend": "attendance/views.py", 
        "Models": "attendance/models.py",
        "Forms": "attendance/forms.py",
        "Services": "attendance/services.py",
        "Static CSS": "static/css/style.css",
        "Static JS": "static/js/app.js"
    }
    
    all_good = True
    for name, path in required_files.items():
        exists = os.path.exists(path)
        if not exists:
            all_good = False
        print_status(name, exists, f"Path: {path}")
    
    return all_good

def verify_template_content():
    """Verificar contenido del template"""
    print_header("📄 VERIFICANDO CONTENIDO DEL TEMPLATE")
    
    template_path = "attendance/templates/attendance/matricula.html"
    if not os.path.exists(template_path):
        print_status("Template no encontrado", False)
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "Botón usar cámara": 'onclick="toggleCamera()"' in content,
        "Función toggleCamera": 'async function toggleCamera()' in content,
        "Función startCamera": 'async function startCamera()' in content,
        "Función capturePhoto": 'async function capturePhoto()' in content,
        "Variables de cámara": 'let stream = null;' in content,
        "Contenedor de cámara": 'id="camera-container"' in content,
        "Elemento video": 'id="camera-video"' in content,
        "Canvas de captura": 'id="capture-canvas"' in content,
        "Input de archivo": 'id="id_foto"' in content,
        "Preview de foto": 'id="foto-preview"' in content,
        "Estilos CSS": '#camera-container' in content,
        "Gestión de MediaDevices": 'getUserMedia' in content,
        "Base64 processing": 'readAsDataURL' in content,
        "Form submission": 'captured_photo' in content
    }
    
    all_good = True
    for check, result in checks.items():
        if not result:
            all_good = False
        print_status(check, result)
    
    # Verificar unicidad de funciones (no duplicadas)
    toggle_count = content.count('function toggleCamera')
    start_count = content.count('function startCamera')
    capture_count = content.count('function capturePhoto')
    
    print(f"\n📊 Conteo de funciones:")
    print_status(f"toggleCamera (debe ser 1)", toggle_count == 1, f"Encontradas: {toggle_count}")
    print_status(f"startCamera (debe ser 1)", start_count == 1, f"Encontradas: {start_count}")
    print_status(f"capturePhoto (debe ser 1)", capture_count == 1, f"Encontradas: {capture_count}")
    
    if toggle_count != 1 or start_count != 1 or capture_count != 1:
        all_good = False
    
    return all_good

def check_backend_support():
    """Verificar soporte backend"""
    print_header("⚙️ VERIFICANDO SOPORTE BACKEND")
    
    views_path = "attendance/views.py"
    if not os.path.exists(views_path):
        print_status("Views no encontrado", False)
        return False
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    backend_checks = {
        "Función student_register": 'def student_register(' in content,
        "Manejo captured_photo": 'captured_photo' in content,
        "Procesamiento base64": 'base64.b64decode' in content,
        "ContentFile import": 'ContentFile' in content,
        "PersonImage model": 'PersonImage' in content,
        "Face encoding": 'generate_face_encoding' in content,
        "Error handling": 'try:' in content and 'except' in content
    }
    
    all_good = True
    for check, result in backend_checks.items():
        if not result:
            all_good = False
        print_status(check, result)
    
    return all_good

def test_javascript_syntax():
    """Verificar sintaxis JavaScript básica"""
    print_header("🔧 VERIFICANDO SINTAXIS JAVASCRIPT")
    
    template_path = "attendance/templates/attendance/matricula.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar scripts
    script_start = content.find('<script>')
    script_end = content.rfind('</script>')
    
    if script_start == -1 or script_end == -1:
        print_status("Scripts no encontrados", False)
        return False
    
    js_content = content[script_start:script_end]
    
    syntax_checks = {
        "Paréntesis balanceados": js_content.count('(') == js_content.count(')'),
        "Llaves balanceadas": js_content.count('{') == js_content.count('}'),
        "Corchetes balanceados": js_content.count('[') == js_content.count(']'),
        "Comillas balanceadas": js_content.count('"') % 2 == 0,
        "Punto y comas": ';' in js_content,
        "Async/await": 'async' in js_content and 'await' in js_content,
        "Event listeners": 'addEventListener' in js_content,
        "Console logs": 'console.log' in js_content
    }
    
    all_good = True
    for check, result in syntax_checks.items():
        if not result:
            all_good = False
        print_status(check, result)
    
    return all_good

def check_dependencies():
    """Verificar dependencias requeridas"""
    print_header("📦 VERIFICANDO DEPENDENCIAS")
    
    # Verificar que Django esté disponible
    try:
        import django
        django_version = django.get_version()
        print_status("Django", True, f"Versión {django_version}")
    except ImportError:
        print_status("Django", False, "No instalado")
        return False
    
    # Verificar otras dependencias críticas
    dependencies = ['cv2', 'face_recognition', 'mediapipe', 'pandas', 'PIL']
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print_status(f"{dep}", True, "Disponible")
        except ImportError:
            print_status(f"{dep}", False, "No disponible")
            all_good = False
    
    return all_good

def run_final_validation():
    """Ejecutar validación final completa"""
    print_header("🚀 VALIDACIÓN FINAL COMPLETA DE FUNCIONALIDAD DE CÁMARA")
    print(f"📅 Ejecutado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Ejecutar todas las pruebas
    test_results['Estructura de archivos'] = check_file_structure()
    test_results['Contenido del template'] = verify_template_content()
    test_results['Soporte backend'] = check_backend_support()
    test_results['Sintaxis JavaScript'] = test_javascript_syntax()
    test_results['Dependencias'] = check_dependencies()
    
    # Calcular resultados
    passed = sum(test_results.values())
    total = len(test_results)
    percentage = (passed / total) * 100
    
    # Generar reporte final
    print_header("📋 REPORTE FINAL")
    
    print(f"📊 Pruebas pasadas: {passed}/{total} ({percentage:.1f}%)")
    
    for test_name, result in test_results.items():
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {test_name}")
    
    # Determinar estado general
    if percentage == 100:
        status = "🎉 COMPLETAMENTE FUNCIONAL"
        color = "verde"
    elif percentage >= 80:
        status = "✅ FUNCIONAL CON ISSUES MENORES"  
        color = "amarillo"
    elif percentage >= 60:
        status = "⚠️  PARCIALMENTE FUNCIONAL"
        color = "naranja"
    else:
        status = "❌ NO FUNCIONAL"
        color = "rojo"
    
    print(f"\n🏷️  Estado general: {status}")
    
    # Instrucciones finales
    print_header("💡 INSTRUCCIONES PARA PRUEBA MANUAL")
    
    if percentage >= 80:
        print("✅ Sistema listo para pruebas:")
        print("   1. Ejecutar: python manage.py runserver")
        print("   2. Ir a: http://127.0.0.1:8000/students/register/")
        print("   3. Hacer clic en 'Usar Cámara'")
        print("   4. Permitir acceso a la cámara cuando se solicite")
        print("   5. Hacer clic en 'Capturar Foto'")
        print("   6. Completar el formulario y enviar")
    else:
        print("❌ Se requieren correcciones antes de probar:")
        failed_tests = [name for name, result in test_results.items() if not result]
        for test in failed_tests:
            print(f"   - Corregir: {test}")
    
    print(f"\n📞 Si necesitas ayuda, revisa la documentación o contacta al desarrollador.")
    
    return percentage >= 80

if __name__ == "__main__":
    # Cambiar al directorio del proyecto
    if os.path.basename(os.getcwd()) != "django_face_app":
        print("⚠️  Ejecutar desde el directorio del proyecto django_face_app")
        sys.exit(1)
    
    # Ejecutar validación
    success = run_final_validation()
    
    # Exit code
    sys.exit(0 if success else 1)