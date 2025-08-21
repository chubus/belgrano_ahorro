#!/usr/bin/env python3
"""
Script de prueba para verificar la integración de tickets entre Belgrano Ahorro y Belgrano Tickets
"""

import requests
import json
from datetime import datetime

def test_integracion_tickets():
    """Probar la integración de tickets"""
    
    # URL de Belgrano Tickets
    base_url = "http://localhost:5001"
    api_endpoint = f"{base_url}/api/tickets/recibir"
    
    print("🧪 Probando integración de tickets...")
    
    # Test 1: Ticket de cliente normal
    print("\n📋 Test 1: Ticket de cliente normal")
    ticket_cliente = {
        'numero': 'TEST-001',
        'cliente_nombre': 'Juan Pérez',
        'cliente_direccion': 'Av. Belgrano 123, CABA',
        'cliente_telefono': '11-1234-5678',
        'cliente_email': 'juan@ejemplo.com',
        'productos': [
            {'nombre': 'Arroz', 'cantidad': 2, 'precio': 500, 'subtotal': 1000},
            {'nombre': 'Aceite', 'cantidad': 1, 'precio': 800, 'subtotal': 800}
        ],
        'total': 1800,
        'metodo_pago': 'Efectivo',
        'fecha': datetime.now().isoformat(),
        'indicaciones': 'Entregar antes de las 18:00',
        'tipo_cliente': 'cliente',
        'prioridad': 'normal'
    }
    
    try:
        response = requests.post(
            api_endpoint,
            json=ticket_cliente,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Ticket de cliente enviado exitosamente")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Error al enviar ticket de cliente: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 2: Ticket de comerciante
    print("\n🏪 Test 2: Ticket de comerciante")
    ticket_comerciante = {
        'numero': 'TEST-002',
        'cliente_nombre': 'Supermercado ABC - María González',
        'cliente_direccion': 'Av. Corrientes 456, CABA',
        'cliente_telefono': '11-9876-5432',
        'cliente_email': 'maria@supermercadoabc.com',
        'productos': [
            {'nombre': 'Harina', 'cantidad': 10, 'precio': 300, 'subtotal': 3000},
            {'nombre': 'Azúcar', 'cantidad': 8, 'precio': 250, 'subtotal': 2000},
            {'nombre': 'Leche', 'cantidad': 15, 'precio': 400, 'subtotal': 6000}
        ],
        'total': 11000,
        'metodo_pago': 'Transferencia',
        'fecha': datetime.now().isoformat(),
        'indicaciones': 'COMERCIANTE - Negocio: Supermercado ABC, Tipo: Supermercado, CUIT: 20-12345678-9. Entregar en horario comercial',
        'tipo_cliente': 'comerciante',
        'prioridad': 'alta'
    }
    
    try:
        response = requests.post(
            api_endpoint,
            json=ticket_comerciante,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Ticket de comerciante enviado exitosamente")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Error al enviar ticket de comerciante: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 3: Verificar conexión
    print("\n🔗 Test 3: Verificar conexión con Belgrano Tickets")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Tickets está funcionando")
        else:
            print(f"⚠️ Belgrano Tickets responde con código: {response.status_code}")
    except Exception as e:
        print(f"❌ No se puede conectar con Belgrano Tickets: {e}")
        print("   Asegúrate de que esté ejecutándose en http://localhost:5001")

if __name__ == "__main__":
    test_integracion_tickets()
    print("\n🎯 Pruebas completadas")
