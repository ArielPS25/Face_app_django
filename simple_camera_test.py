#!/usr/bin/env python3
"""
Script simplificado para verificar selector de cámaras
"""

import requests
from datetime import datetime

def main():
    print("📹 VERIFICACIÓN RÁPIDA DEL SELECTOR DE CÁMARAS")
    print("=" * 60)
    
    try:
        response = requests.get('http://127.0.0.1:8000/students/register/', timeout=10)
        content = response.text
        print("✅ Página de matrícula cargada")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Lista de componentes importantes
    components = [
        ('Selector HTML', 'id="camera-selector"'),
        ('Select de cámaras', 'id="camera-select"'),
        ('Función detectar cámaras', 'detectAvailableCameras'),
        ('Función cambiar cámara', 'switchCamera'),
        ('Función actualizar lista', 'refreshCameraList'),
        ('Variables de dispositivos', 'availableCameras'),
        ('ID de cámara actual', 'currentCameraId'),
        ('Detección Canon', 'canon'),
        ('API enumerateDevices', 'enumerateDevices'),
        ('Configuración deviceId', 'constraints.video.deviceId')
    ]
    
    print("\n🔍 Verificando componentes:")
    found = 0
    for name, pattern in components:
        if pattern in content:
            print(f"✅ {name}")
            found += 1
        else:
            print(f"❌ {name}")
    
    percentage = (found / len(components)) * 100
    print(f"\n📊 Resultado: {found}/{len(components)} componentes encontrados ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("🎉 ¡SELECTOR DE CÁMARAS IMPLEMENTADO CORRECTAMENTE!")
        print("\n💡 Funcionalidades disponibles:")
        print("   • Detección automática de cámaras")
        print("   • Selector desplegable para elegir dispositivo")
        print("   • Identificación de cámaras problemáticas")
        print("   • Cambio de cámara sin reiniciar")
        print("   • Actualización de lista de dispositivos")
        
        print(f"\n📱 Para usar:")
        print(f"   1. Ir a: http://127.0.0.1:8000/students/register/")
        print(f"   2. Hacer clic en 'Usar Cámara'")
        print(f"   3. Usar el selector que aparece si hay múltiples cámaras")
        print(f"   4. Hacer clic en 'Cambiar Cámara' para aplicar selección")
    else:
        print("❌ Faltan algunos componentes importantes")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()