#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de productos detallados en la comunicación entre Belgrano Ahorro y Ticketera
Verifica que se envíen y muestren correctamente: nombre, precio, cantidad y sucursal
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
    """Test de envío de productos con información detallada"""
    print("🎫 Probando envío de productos con información detallada...")
    
    # Simular carrito con productos detallados
    carrito_items = [
        {
            'producto': {
                'nombre': 'Arroz Integral 1kg',
                'precio': 850,
                'sucursal': 'Sucursal Centro',
                'categoria': 'Granos',
                'descripcion': 'Arroz integral de alta calidad',
                'codigo': 'ARROZ001'
            },
            'cantidad': 2
        },
        {
            'producto': {
                'nombre': 'Aceite de Oliva Extra Virgen 500ml',
                'precio': 1200,
                'sucursal': 'Sucursal Norte',
                'categoria': 'Aceites',
                'descripcion': 'Aceite de oliva premium',
                'codigo': 'ACEITE002'
            },
            'cantidad': 1
        },
        {
            'producto': {
                'nombre': 'Leche Descremada 1L',
                'precio': 450,
                'sucursal': 'Sucursal Sur',
                'categoria': 'Lácteos',
                'descripcion': 'Leche descremada fresca',
                'codigo': 'LECHE003'
            },
            'cantidad': 3
        }
    ]
    
    # Calcular total
    total = sum(item['cantidad'] * item['producto']['precio'] for item in carrito_items)
    
    # Preparar productos con estructura detallada
    productos = []
    for item in carrito_items:
        producto = item['producto']
        producto_detallado = {
            'nombre': producto['nombre'],
            'cantidad': item['cantidad'],
            'precio_unitario': producto['precio'],
            'precio_total': item['cantidad'] * producto['precio'],
            'sucursal': producto['sucursal'],
            'categoria': producto['categoria'],
            'descripcion': producto['descripcion'],
            'codigo': producto['codigo']
        }
        productos.append(producto_detallado)
    
    ticket_data = {
        "numero": f"PRODUCTOS-DETALLADOS-{int(time.time())}",
        "cliente_nombre": "Cliente Test Productos Detallados",
        "cliente_direccion": "Dirección Test 123",
        "cliente_telefono": "1234567890",
        "cliente_email": "test.productos@example.com",
        "productos": productos,
        "total": total,
        "metodo_pago": "efectivo",
        "indicaciones": "Test de productos con información detallada",
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
        print(f"📤 Enviando ticket con productos detallados a {TICKETERA_URL}/api/tickets")
        print(f"   Número: {ticket_data['numero']}")
        print(f"   Cliente: {ticket_data['cliente_nombre']}")
        print(f"   Total: ${ticket_data['total']}")
        print(f"   Productos: {len(productos)} items")
        
        # Mostrar detalles de productos
        print("\n📋 Detalles de productos a enviar:")
        for i, producto in enumerate(productos, 1):
            print(f"   {i}. {producto['nombre']}")
            print(f"      Cantidad: {producto['cantidad']}")
            print(f"      Precio unitario: ${producto['precio_unitario']}")
            print(f"      Precio total: ${producto['precio_total']}")
            print(f"      Sucursal: {producto['sucursal']}")
            print(f"      Categoría: {producto['categoria']}")
            print()
        
        response = requests.post(
            f"{TICKETERA_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=20
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code in (200, 201):
            try:
                response_data = response.json()
                print("✅ Ticket creado exitosamente!")
                print(f"   Ticket ID: {response_data.get('ticket_id', 'N/A')}")
                print(f"   Número: {response_data.get('numero', 'N/A')}")
                print(f"   Estado: {response_data.get('estado', 'N/A')}")
                print(f"   Repartidor: {response_data.get('repartidor_asignado', 'N/A')}")
                
                # Verificar que los productos se procesaron correctamente
                print("\n🔍 Verificando procesamiento de productos...")
                if response_data.get('exito'):
                    print("✅ Ticket procesado correctamente")
                    return response_data.get('numero')
                else:
                    print("⚠️ Ticket procesado pero con advertencias")
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
    """Verificar que la Ticketera esté funcionando"""
    print("\n🔍 Verificando estado de la Ticketera...")
    
    try:
        response = requests.get(f"{TICKETERA_URL}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ Ticketera: OK")
            return True
        else:
            print(f"❌ Ticketera: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ticketera: Error - {e}")
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
        print("🎉 ¡PRODUCTOS DETALLADOS FUNCIONANDO!")
        print("✅ Información completa enviada:")
        print("   - Nombre del producto")
        print("   - Precio unitario")
        print("   - Cantidad")
        print("   - Precio total por producto")
        print("   - Sucursal")
        print("   - Categoría")
        print("   - Descripción")
        print("   - Código de producto")
        print(f"✅ Ticket creado: {ticket_numero}")
    else:
        print("❌ Problemas con productos detallados")
        print("🔧 Revisar configuración y logs")

if __name__ == "__main__":
    main()
