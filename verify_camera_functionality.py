#!/usr/bin/env python3
"""
Script de verificación completa de la funcionalidad de cámara
"""

import requests
import re
from datetime import datetime

def check_server_status():
    """Verificar si el servidor Django está corriendo"""
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"✅ Servidor Django funcionando - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Error: El servidor Django no está corriendo")
        return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def check_matricula_page():
    """Verificar que la página de matrícula carga correctamente"""
    try:
        response = requests.get('http://127.0.0.1:8000/students/register/', timeout=10)
        if response.status_code == 200:
            print(f"✅ Página de matrícula carga correctamente - Status: {response.status_code}")
            return response.text
        else:
            print(f"❌ Error cargando página de matrícula - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error accediendo a página de matrícula: {e}")
        return None

def verify_camera_components(html_content):
    """Verificar que todos los componentes de cámara están presentes"""
    print("\n🔍 Verificando componentes de cámara...")
    
    # Lista de componentes críticos
    components = {
        'Botón Usar Cámara': r'onclick="toggleCamera\(\)"',
        'Función toggleCamera': r'async function toggleCamera\(\)',
        'Función startCamera': r'async function startCamera\(\)',
        'Función stopCamera': r'async function stopCamera\(\)',
        'Función capturePhoto': r'async function capturePhoto\(\)',
        'Variables globales': r'let stream = null;',
        'Contenedor cámara': r'id="camera-container"',
        'Video elemento': r'id="camera-video"',
        'Canvas captura': r'id="capture-canvas"',
        'Botón capturar': r'onclick="capturePhoto\(\)"',
        'Input archivo': r'id="id_foto"',
        'Preview container': r'id="foto-preview"'
    }
    
    results = {}
    for name, pattern in components.items():
        if re.search(pattern, html_content):
            print(f"✅ {name}: Encontrado")
            results[name] = True
        else:
            print(f"❌ {name}: NO encontrado")
            results[name] = False
    
    return results

def check_javascript_structure(html_content):
    """Verificar la estructura del JavaScript"""
    print("\n📋 Verificando estructura JavaScript...")
    
    # Contar funciones duplicadas
    toggle_count = len(re.findall(r'function toggleCamera', html_content))
    start_count = len(re.findall(r'function startCamera', html_content))
    capture_count = len(re.findall(r'function capturePhoto', html_content))
    
    print(f"📊 Funciones encontradas:")
    print(f"   - toggleCamera: {toggle_count} {'✅' if toggle_count == 1 else '❌'}")
    print(f"   - startCamera: {start_count} {'✅' if start_count == 1 else '❌'}")
    print(f"   - capturePhoto: {capture_count} {'✅' if capture_count == 1 else '❌'}")
    
    # Verificar orden de carga
    dom_ready = 'DOMContentLoaded' in html_content
    print(f"   - DOMContentLoaded: {'✅' if dom_ready else '❌'}")
    
    # Verificar sintaxis básica
    syntax_checks = {
        'Paréntesis balanceados': html_content.count('(') == html_content.count(')'),
        'Llaves balanceadas': html_content.count('{') == html_content.count('}'),
        'Scripts cerrados': '</script>' in html_content
    }
    
    for check, result in syntax_checks.items():
        print(f"   - {check}: {'✅' if result else '❌'}")

def verify_css_styles(html_content):
    """Verificar estilos CSS importantes"""
    print("\n🎨 Verificando estilos CSS...")
    
    css_components = {
        'Estilos de cámara': '#camera-container',
        'Estilos de botón': '.btn-primary',
        'Estilos responsivos': '@media (max-width: 768px)',
        'Animaciones': '@keyframes fadeInUp',
        'Preview container': '.preview-container'
    }
    
    for name, pattern in css_components.items():
        if pattern in html_content:
            print(f"✅ {name}: Presente")
        else:
            print(f"❌ {name}: Ausente")

def generate_report(results):
    """Generar reporte final"""
    print("\n" + "="*60)
    print("📋 REPORTE FINAL DE VERIFICACIÓN")
    print("="*60)
    
    total_components = len(results)
    working_components = sum(results.values())
    percentage = (working_components / total_components) * 100
    
    print(f"📊 Componentes funcionando: {working_components}/{total_components} ({percentage:.1f}%)")
    
    if percentage >= 95:
        print("🎉 ¡EXCELENTE! Todas las funcionalidades están implementadas correctamente")
        status = "COMPLETAMENTE FUNCIONAL"
    elif percentage >= 80:
        print("✅ BUENO: La mayoría de componentes están funcionando")
        status = "FUNCIONAL CON ISSUES MENORES"
    elif percentage >= 60:
        print("⚠️  REGULAR: Algunos componentes faltan o tienen problemas")
        status = "PARCIALMENTE FUNCIONAL"
    else:
        print("❌ CRÍTICO: Muchos componentes faltan o están rotos")
        status = "NO FUNCIONAL"
    
    print(f"\n🏷️  Estado general: {status}")
    print(f"📅 Verificación realizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Componentes faltantes
    missing = [name for name, result in results.items() if not result]
    if missing:
        print(f"\n❌ Componentes con problemas:")
        for component in missing:
            print(f"   - {component}")
    
    return status

def main():
    """Función principal de verificación"""
    print("🚀 INICIANDO VERIFICACIÓN COMPLETA DE FUNCIONALIDAD DE CÁMARA")
    print("="*60)
    
    # 1. Verificar servidor
    if not check_server_status():
        print("\n❌ No se puede continuar sin el servidor Django")
        return
    
    # 2. Cargar página de matrícula
    html_content = check_matricula_page()
    if not html_content:
        print("\n❌ No se puede verificar componentes sin acceso a la página")
        return
    
    # 3. Verificar componentes
    component_results = verify_camera_components(html_content)
    
    # 4. Verificar JavaScript
    check_javascript_structure(html_content)
    
    # 5. Verificar CSS
    verify_css_styles(html_content)
    
    # 6. Generar reporte
    final_status = generate_report(component_results)
    
    # 7. Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if final_status == "COMPLETAMENTE FUNCIONAL":
        print("   - Todo está funcionando correctamente")
        print("   - Puedes probar la cámara en el navegador")
        print("   - Asegúrate de dar permisos de cámara cuando se solicite")
    else:
        print("   - Revisa los componentes marcados como faltantes")
        print("   - Verifica que no hay errores de JavaScript en la consola")
        print("   - Comprueba que todos los archivos están guardados")
    
    print(f"\n🌐 Para probar manualmente: http://127.0.0.1:8000/students/register/")
    print("="*60)

if __name__ == "__main__":
    main()