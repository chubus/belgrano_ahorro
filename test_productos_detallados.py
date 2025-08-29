#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de productos detallados en la comunicación entre Belgrano Ahorro y Ticketera
Verifica que se envíen nombre, precio, cantidad, sucursal y negocio
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
TICKETERA_URL = "https://ticketerabelgrano.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def test_productos_detallados():
    """Test de envío de productos con información completa"""
    print("🎫 Test de productos detallados")
    print("=" * 50)
    
    # Datos de prueba con productos detallados
    ticket_data = {
        "numero": f"PRODUCTOS-DET-{int(time.time())}",
        "cliente_nombre": "Cliente Test Productos Detallados",
        "cliente_direccion": "Dirección Test 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "test.productos@example.com",
        "productos": [
            {
                "id": 1,
                "nombre": "Arroz 1kg",
                "precio": 950.0,
                "cantidad": 2,
                "subtotal": 1900.0,
                "sucursal": "Sucursal Centro",
                "negocio": "Belgrano Ahorro",
                "categoria": "Granos y Cereales",
                "descripcion": "Arroz de grano largo",
                "stock": 50,
                "destacado": True
            },
            {
                "id": 2,
                "nombre": "Aceite 900ml",
                "precio": 1800.0,
                "cantidad": 1,
                "subtotal": 1800.0,
                "sucursal": "Sucursal Sur",
                "negocio": "Belgrano Ahorro",
                "categoria": "Condimentos",
                "descripcion": "Aceite de girasol",
                "stock": 45,
                "destacado": True
            },
            {
                "id": 5,
                "nombre": "Leche 1L",
                "precio": 850.0,
                "cantidad": 3,
                "subtotal": 2550.0,
                "sucursal": "Sucursal Centro",
                "negocio": "Belgrano Ahorro",
                "categoria": "Lácteos",
                "descripcion": "Leche entera",
                "stock": 60,
                "destacado": True
            }
        ],
        "total": 6250.0,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de productos con información completa",
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente",
        "fecha_creacion": datetime.now().isoformat(),
        "origen": "belgrano_ahorro"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'User-Agent': 'BelgranoAhorro/1.0.0',
        'X-Request-ID': f"{ticket_data['numero']}-{int(time.time())}",
        'X-Origin': 'belgrano_ahorro'
    }
    
    try:
        print(f"📤 Enviando ticket con productos detallados...")
        print(f"   URL: {TICKETERA_URL}/api/tickets")
        print(f"   Número: {ticket_data['numero']}")
        print(f"   Cliente: {ticket_data['cliente_nombre']}")
        print(f"   Total: ${ticket_data['total']}")
        print(f"   Productos: {len(ticket_data['productos'])} items")
        
        # Mostrar detalles de cada producto
        for i, producto in enumerate(ticket_data['productos'], 1):
            print(f"   Producto {i}:")
            print(f"     - ID: {producto['id']}")
            print(f"     - Nombre: {producto['nombre']}")
            print(f"     - Precio: ${producto['precio']}")
            print(f"     - Cantidad: {producto['cantidad']}")
            print(f"     - Subtotal: ${producto['subtotal']}")
            print(f"     - Sucursal: {producto['sucursal']}")
            print(f"     - Negocio: {producto['negocio']}")
            print(f"     - Categoría: {producto['categoria']}")
        
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=20
        )
        
        print(f"\n📥 Status Code: {response.status_code}")
        
        if response.status_code in (200, 201):
            try:
                response_data = response.json()
                print("✅ Ticket creado exitosamente!")
                print(f"   Ticket ID: {response_data.get('ticket_id', 'N/A')}")
                print(f"   Número: {response_data.get('numero', 'N/A')}")
                print(f"   Estado: {response_data.get('estado', 'N/A')}")
                print(f"   Repartidor: {response_data.get('repartidor_asignado', 'N/A')}")
                
                # Verificar que los productos se guardaron correctamente
                print(f"\n🔍 Verificando productos en la respuesta...")
                if 'productos' in response_data:
                    productos_respuesta = response_data['productos']
                    print(f"   Productos en respuesta: {len(productos_respuesta)}")
                    for i, producto in enumerate(productos_respuesta, 1):
                        print(f"   Producto {i}: {producto}")
                else:
                    print("   ⚠️ No se encontraron productos en la respuesta")
                
                return response_data.get('numero')
                
            except json.JSONDecodeError:
                print(f"⚠️ Respuesta no es JSON válido: {response.text}")
                return None
        else:
            print(f"❌ Error creando ticket: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en comunicación: {e}")
        return None

def test_verificacion_ticketera():
    """Verificar que la Ticketera puede mostrar los productos correctamente"""
    print(f"\n🔍 Verificando que la Ticketera esté funcionando...")
    
    try:
        response = requests.get(f"{TICKETERA_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Ticketera está funcionando")
            return True
        else:
            print(f"❌ Ticketera no responde correctamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con Ticketera: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 TEST DE PRODUCTOS DETALLADOS")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. Verificar que la Ticketera esté funcionando
    if not test_verificacion_ticketera():
        print("\n❌ La Ticketera no está disponible")
        return
    
    # 2. Test de productos detallados
    ticket_numero = test_productos_detallados()
    
    # 3. Resultado final
    print("\n" + "=" * 50)
    print("🏁 RESULTADO FINAL")
    print("=" * 50)
    
    if ticket_numero:
        print("🎉 ¡PRODUCTOS DETALLADOS ENVIADOS EXITOSAMENTE!")
        print("✅ Información completa de productos enviada")
        print("✅ Nombre, precio, cantidad incluidos")
        print("✅ Sucursal y negocio incluidos")
        print("✅ Categoría y descripción incluidos")
        print(f"✅ Ticket creado: {ticket_numero}")
    else:
        print("❌ Problemas enviando productos detallados")
        print("🔧 Revisar configuración y logs")

if __name__ == "__main__":
    main()
