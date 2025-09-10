#!/usr/bin/env python3
"""
Script de prueba para verificar la sincronización entre DevOps y Belgrano Ahorro
"""

import os
import sys
import requests
import json
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = 'https://belgranoahorro-hp30.onrender.com'
BELGRANO_AHORRO_API_KEY = 'belgrano_ahorro_api_key_2025'

def test_belgrano_ahorro_connection():
    """Probar conexión con Belgrano Ahorro"""
    print("🔍 Probando conexión con Belgrano Ahorro...")
    
    try:
        # Probar endpoint de negocios
        url = f"{BELGRANO_AHORRO_URL}/api/v1/negocios"
        headers = {
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'X-Origin': 'devops_test'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa - Negocios encontrados: {len(data) if isinstance(data, list) else 'N/A'}")
            return True, data
        else:
            print(f"❌ Error en conexión: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False, str(e)

def test_add_negocio():
    """Probar agregar un negocio de prueba"""
    print("\n🔍 Probando agregar negocio...")
    
    try:
        # Datos de prueba
        test_negocio = {
            'nombre': f'Negocio Test DevOps {datetime.now().strftime("%H%M%S")}',
            'descripcion': 'Negocio de prueba desde DevOps',
            'categoria': 'Test',
            'creado_desde': 'devops_test',
            'fecha_creacion': datetime.now().isoformat(),
            'activo': True
        }
        
        url = f"{BELGRANO_AHORRO_URL}/api/v1/negocios"
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': BELGRANO_AHORRO_API_KEY,
            'X-Origin': 'devops_test',
            'X-Timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(url, json=test_negocio, headers=headers, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Negocio agregado exitosamente: {data}")
            return True, data
        else:
            print(f"❌ Error agregando negocio: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Error agregando negocio: {e}")
        return False, str(e)

def test_devops_routes():
    """Probar las rutas de DevOps localmente"""
    print("\n🔍 Probando rutas de DevOps...")
    
    try:
        # Importar el blueprint
        from devops_routes import devops_bp
        print("✅ Blueprint de DevOps importado correctamente")
        
        # Verificar que las rutas estén registradas
        print(f"📋 Rutas registradas: {len(devops_bp.deferred_functions)}")
        
        return True, "Blueprint funcionando"
        
    except Exception as e:
        print(f"❌ Error importando DevOps: {e}")
        return False, str(e)

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de sincronización DevOps...")
    print("=" * 50)
    
    # Probar importación de DevOps
    devops_ok, devops_msg = test_devops_routes()
    
    # Probar conexión con Belgrano Ahorro
    connection_ok, connection_data = test_belgrano_ahorro_connection()
    
    # Probar agregar negocio
    if connection_ok:
        add_ok, add_data = test_add_negocio()
    else:
        add_ok, add_data = False, "No se pudo probar - sin conexión"
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"DevOps Routes: {'✅ OK' if devops_ok else '❌ ERROR'}")
    print(f"Conexión Belgrano: {'✅ OK' if connection_ok else '❌ ERROR'}")
    print(f"Agregar Negocio: {'✅ OK' if add_ok else '❌ ERROR'}")
    
    if devops_ok and connection_ok and add_ok:
        print("\n🎉 ¡Todas las pruebas pasaron! La sincronización está funcionando.")
    else:
        print("\n⚠️  Hay problemas que necesitan ser resueltos.")
        
        if not devops_ok:
            print("   - Revisar importación de devops_routes.py")
        if not connection_ok:
            print("   - Revisar URL y API key de Belgrano Ahorro")
        if not add_ok:
            print("   - Revisar endpoints de la API")

if __name__ == "__main__":
    main()