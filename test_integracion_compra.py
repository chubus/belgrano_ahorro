#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la integración entre Belgrano Ahorro y la Ticketera
"""

import requests
import json
import time
from datetime import datetime

def test_integracion_compra():
    """Probar la integración completa de compra"""
    
    print("🧪 TESTEANDO INTEGRACIÓN DE COMPRA")
    print("=" * 50)
    
    # URLs de los servicios
    belgrano_url = "http://localhost:5000"
    ticketera_url = "http://localhost:5001"
    
    # Verificar que ambos servicios estén corriendo
    print("🔍 Verificando servicios...")
    
    try:
        # Verificar Belgrano Ahorro
        response = requests.get(f"{belgrano_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro está corriendo")
        else:
            print("❌ Belgrano Ahorro no responde correctamente")
            return False
    except:
        print("❌ Belgrano Ahorro no está disponible")
        return False
    
    try:
        # Verificar Ticketera
        response = requests.get(f"{ticketera_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Ticketera está corriendo")
        else:
            print("❌ Ticketera no responde correctamente")
            return False
    except:
        print("❌ Ticketera no está disponible")
        return False
    
    # Simular datos de compra
    print("\n📦 Simulando compra...")
    
    # Datos de usuario
    usuario = {
        'id': 1,
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'email': 'juan.perez@test.com',
        'telefono': '11-1234-5678'
    }
    
    # Datos de carrito
    carrito_items = [
        {
            'producto': {
                'id': 1,
                'nombre': 'Leche',
                'precio': 150.0
            },
            'cantidad': 2,
            'subtotal': 300.0
        },
        {
            'producto': {
                'id': 2,
                'nombre': 'Pan',
                'precio': 80.0
            },
            'cantidad': 1,
            'subtotal': 80.0
        }
    ]
    
    # Datos de la compra
    numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total = 380.0
    metodo_pago = "efectivo"
    direccion = "Av. Belgrano 123, CABA"
    notas = "Entregar en horario de tarde"
    
    # Simular envío directo a la API de la ticketera
    print(f"📤 Enviando pedido {numero_pedido} a la Ticketera...")
    
    ticket_data = {
        "numero": numero_pedido,
        "cliente_nombre": f"{usuario['nombre']} {usuario['apellido']}",
        "cliente_direccion": direccion,
        "cliente_telefono": usuario['telefono'],
        "cliente_email": usuario['email'],
        "productos": [f"{item['producto']['nombre']} x{item['cantidad']}" for item in carrito_items],
        "total": total,
        "metodo_pago": metodo_pago,
        "indicaciones": notas,
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente"
    }
    
    try:
        # Enviar a la API de la ticketera
        response = requests.post(
            f"{ticketera_url}/api/tickets/recibir",
            json=ticket_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Respuesta de la Ticketera: {response.status_code}")
        print(f"📄 Contenido: {response.text}")
        
        if response.status_code == 201:
            print("✅ Pedido enviado exitosamente a la Ticketera")
            
            # Verificar que el ticket aparezca en el panel
            print("\n🔍 Verificando que el ticket aparezca en el panel...")
            time.sleep(2)  # Esperar un poco para que se procese
            
            try:
                # Intentar obtener tickets (esto requeriría autenticación en producción)
                response = requests.get(f"{ticketera_url}/api/tickets", timeout=5)
                if response.status_code == 200:
                    tickets = response.json()
                    print(f"✅ Se encontraron {tickets.get('total_tickets', 0)} tickets en el sistema")
                else:
                    print("⚠️ No se pudo verificar tickets (posiblemente requiere autenticación)")
            except Exception as e:
                print(f"⚠️ Error verificando tickets: {e}")
            
            return True
        else:
            print(f"❌ Error enviando pedido: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la Ticketera")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout al conectar con la Ticketera")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_endpoint_directo():
    """Probar el endpoint directamente"""
    
    print("\n🔧 TESTEANDO ENDPOINT DIRECTO")
    print("=" * 40)
    
    ticketera_url = "http://localhost:5001"
    
    # Datos de prueba simplificados
    test_data = {
        "numero": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "cliente_nombre": "Cliente de Prueba",
        "cliente_direccion": "Dirección de Prueba 123",
        "cliente_telefono": "11-9999-8888",
        "cliente_email": "test@test.com",
        "productos": ["Producto 1 x1", "Producto 2 x2"],
        "total": 250.0,
        "metodo_pago": "efectivo",
        "indicaciones": "Notas de prueba",
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente"
    }
    
    try:
        print(f"📤 Enviando datos de prueba...")
        print(f"   Datos: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            f"{ticketera_url}/api/tickets/recibir",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📥 Respuesta: {response.status_code}")
        print(f"📄 Contenido: {response.text}")
        
        if response.status_code == 201:
            print("✅ Test exitoso")
            return True
        else:
            print("❌ Test falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN")
    print("=" * 60)
    
    # Test 1: Integración completa
    success1 = test_integracion_compra()
    
    # Test 2: Endpoint directo
    success2 = test_endpoint_directo()
    
    print("\n📊 RESULTADOS DE LAS PRUEBAS")
    print("=" * 40)
    print(f"✅ Integración completa: {'EXITOSO' if success1 else 'FALLÓ'}")
    print(f"✅ Endpoint directo: {'EXITOSO' if success2 else 'FALLÓ'}")
    
    if success1 and success2:
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        print("💡 La integración entre Belgrano Ahorro y la Ticketera está funcionando correctamente.")
    else:
        print("\n⚠️ Algunas pruebas fallaron.")
        print("🔧 Revisa los logs para identificar el problema.")
    
    return success1 and success2

if __name__ == "__main__":
    main()
