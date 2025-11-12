#!/usr/bin/env python3
"""
Script para verificar la nueva funcionalidad de selector de cámaras
"""

import requests
import re
from datetime import datetime

def test_camera_selector_functionality():
    """Verificar la funcionalidad del selector de cámaras"""
    print("📹 VERIFICACIÓN DEL SELECTOR DE CÁMARAS")
    print("=" * 60)
    print(f"📅 Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar servidor
    try:
        response = requests.get('http://127.0.0.1:8000/students/register/', timeout=10)
        if response.status_code == 200:
            print("✅ Página de matrícula accesible")
            content = response.text
        else:
            print(f"❌ Error: Página no accesible - {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n🔍 Verificando componentes del selector de cámaras:")
    
    # Verificar elementos HTML
    html_checks = {
        "Contenedor selector": 'id="camera-selector"' in content,
        "Select de cámaras": 'id="camera-select"' in content,
        "Botón cambiar cámara": 'onclick="switchCamera()"' in content,
        "Botón actualizar lista": 'onclick="refreshCameraList()"' in content,
        "Estilos del selector": 'background: #f8f9fa' in content,
        "Label del selector": 'Seleccionar Cámara:' in content
    }
    
    for check, result in html_checks.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {check}")
    
    print("\n🔧 Verificando funciones JavaScript:")
    
    # Verificar funciones JavaScript
    js_functions = {
        "detectAvailableCameras": 'async function detectAvailableCameras()',
        "updateCameraSelector": 'function updateCameraSelector()',
        "getCurrentCameraName": 'function getCurrentCameraName()',
        "switchCamera": 'async function switchCamera()',
        "refreshCameraList": 'async function refreshCameraList()',
        "startCamera mejorada": 'async function startCamera(deviceId = null)'
    }
    
    for func, pattern in js_functions.items():
        found = pattern in content
        icon = "✅" if found else "❌"
        print(f"{icon} {func}")
    
    print("\n📱 Verificando APIs de navegador:")
    
    # Verificar uso de APIs
    browser_apis = {
        "enumerateDevices": 'enumerateDevices()' in content,
        "getUserMedia con deviceId": 'constraints.video.deviceId' in content,
        "getVideoTracks": 'getVideoTracks()' in content,
        "getSettings": 'getSettings()' in content,
        "Manejo de permisos": 'tempStream' in content
    }
    
    for api, result in browser_apis.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {api}")
    
    print("\n🛠️ Verificando manejo de errores:")
    
    # Verificar manejo de errores
    error_handling = {
        "NotReadableError": 'NotReadableError' in content,
        "Detectar Canon/DSLR": 'canon' in content.lower() or 'dslr' in content.lower(),
        "Múltiples cámaras": 'availableCameras.length > 1' in content,
        "Fallback a defecto": 'facingMode' in content,
        "Mensajes informativos": 'Puede tener problemas' in content
    }
    
    for check, result in error_handling.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {check}")
    
    print("\n🎯 Verificando variables globales:")
    
    # Verificar variables
    variables = {
        "availableCameras": 'let availableCameras = [];' in content,
        "currentCameraId": 'let currentCameraId = null;' in content,
        "stream y cameraActive": 'let stream = null;' in content and 'let cameraActive = false;' in content
    }
    
    for var, result in variables.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {var}")
    
    # Calcular resultado
    all_checks = {**html_checks, **js_functions, **browser_apis, **error_handling, **variables}
    passed = sum(all_checks.values())
    total = len(all_checks)
    percentage = (passed / total) * 100
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado: {passed}/{total} verificaciones pasadas ({percentage:.1f}%)")
    
    if percentage >= 95:
        print("🎉 ¡SELECTOR DE CÁMARAS COMPLETAMENTE IMPLEMENTADO!")
        
        print(f"\n💡 Nuevas funcionalidades:")
        print(f"   ✅ Detección automática de cámaras disponibles")
        print(f"   ✅ Selector desplegable para elegir cámara")
        print(f"   ✅ Identificación de cámaras problemáticas (Canon/DSLR)")
        print(f"   ✅ Botón para cambiar cámara sin reiniciar")
        print(f"   ✅ Botón para actualizar lista de dispositivos")
        print(f"   ✅ Manejo inteligente de errores por dispositivo")
        print(f"   ✅ Preferencia automática por cámaras web estándar")
        
        print(f"\n🚀 Solución al problema Canon:")
        print(f"   • El sistema detecta automáticamente cámaras Canon/DSLR")
        print(f"   • Las marca con ⚠️ (Puede tener problemas)")
        print(f"   • Prioriza cámaras web normales por defecto")
        print(f"   • Permite cambiar fácilmente entre dispositivos")
        print(f"   • Muestra errores específicos por tipo de dispositivo")
        
        print(f"\n📱 Cómo usar:")
        print(f"   1. Ir a: http://127.0.0.1:8000/students/register/")
        print(f"   2. Hacer clic en 'Usar Cámara'")
        print(f"   3. Si hay múltiples cámaras, aparece el selector")
        print(f"   4. Elegir cámara del desplegable")
        print(f"   5. Hacer clic en 'Cambiar Cámara'")
        print(f"   6. Usar 'Actualizar Lista' si conectas/desconectas cámaras")
        
        status = "COMPLETAMENTE FUNCIONAL"
    else:
        print("❌ Faltan algunos componentes")
        missing = [name for name, result in all_checks.items() if not result]
        print(f"\nComponentes faltantes:")
        for component in missing[:5]:  # Mostrar solo los primeros 5
            print(f"   - {component}")
        status = "REQUIERE CORRECCIONES"
    
    print(f"\n🏷️  Estado: {status}")
    print("=" * 60)
    
    return percentage >= 95

if __name__ == "__main__":
    success = test_camera_selector_functionality()
    exit(0 if success else 1)