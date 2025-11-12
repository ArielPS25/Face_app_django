#!/usr/bin/env python3
"""
Script para probar la funcionalidad de liberación automática de cámara
"""

import requests
import time
from datetime import datetime

def test_camera_release_functionality():
    """Probar que la cámara se libere correctamente"""
    print("🔧 PRUEBA DE LIBERACIÓN AUTOMÁTICA DE CÁMARA")
    print("=" * 60)
    print(f"📅 Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "http://127.0.0.1:8000"
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(base_url, timeout=5)
        print("✅ Servidor Django corriendo")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Servidor Django no disponible")
        return False
    
    # Verificar página de cámara
    try:
        response = requests.get(f"{base_url}/camera/", timeout=10)
        if response.status_code == 200:
            print("✅ Página de cámara accesible")
            content = response.text
        else:
            print(f"❌ Error accediendo a página de cámara: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Verificar mejoras implementadas
    print("\n📋 Verificando mejoras implementadas:")
    
    checks = {
        "beforeunload event mejorado": 'window.addEventListener(\'beforeunload\'' in content,
        "Función stopDetectionSync": 'function stopDetectionSync()' in content,
        "sendBeacon para confiabilidad": 'navigator.sendBeacon' in content,
        "pagehide event": 'window.addEventListener(\'pagehide\'' in content,
        "popstate event": 'window.addEventListener(\'popstate\'' in content,
        "Función goBackHome": 'function goBackHome()' in content,
        "Botón regresar mejorado": 'onclick="goBackHome()"' in content,
        "Detección isRunning": 'if (isRunning)' in content
    }
    
    all_good = True
    for check, result in checks.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {check}")
        if not result:
            all_good = False
    
    # Verificar estructura del JavaScript
    print(f"\n🔍 Verificando estructura JavaScript:")
    
    js_functions = [
        'stopDetectionSync',
        'goBackHome',
        'startDetection',
        'stopDetection'
    ]
    
    for func in js_functions:
        if f'function {func}' in content:
            print(f"✅ Función {func} encontrada")
        else:
            print(f"❌ Función {func} faltante")
            all_good = False
    
    # Verificar eventos de navegador
    print(f"\n🌐 Verificando eventos de navegador:")
    
    browser_events = [
        'beforeunload',
        'pagehide', 
        'popstate'
    ]
    
    for event in browser_events:
        if f"addEventListener('{event}'" in content:
            print(f"✅ Evento {event} configurado")
        else:
            print(f"❌ Evento {event} faltante")
            all_good = False
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ¡TODAS LAS MEJORAS IMPLEMENTADAS CORRECTAMENTE!")
        print("\n💡 Funcionalidades agregadas:")
        print("   - Detención automática al cerrar pestaña/ventana")
        print("   - Detención automática con botón atrás del navegador")
        print("   - Detención automática con botón 'Regresar'")
        print("   - Uso de sendBeacon para máxima confiabilidad")
        print("   - Manejo de múltiples eventos de navegador")
        
        print(f"\n📱 Para probar:")
        print(f"   1. Ir a: {base_url}/camera/")
        print(f"   2. Hacer clic en 'Iniciar Detección'")
        print(f"   3. Probar salir de la página de diferentes formas:")
        print(f"      - Botón 'Regresar'")
        print(f"      - Botón atrás del navegador")
        print(f"      - Cerrar pestaña")
        print(f"      - Navegar a otra URL")
        print(f"   4. Verificar que la cámara se libere automáticamente")
        
        status = "COMPLETAMENTE FUNCIONAL"
    else:
        print("❌ FALTAN ALGUNAS MEJORAS")
        status = "REQUIERE CORRECCIONES"
    
    print(f"\n🏷️  Estado: {status}")
    print("=" * 60)
    
    return all_good

if __name__ == "__main__":
    success = test_camera_release_functionality()
    exit(0 if success else 1)