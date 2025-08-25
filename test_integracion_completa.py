#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la integración completa entre Belgrano Ahorro y Belgrano Tickets
"""

import requests
import json
import time
from datetime import datetime

def test_belgrano_ahorro():
    """Probar que Belgrano Ahorro esté funcionando"""
    print("🔍 Verificando Belgrano Ahorro...")
    
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro está funcionando")
            return True
        else:
            print(f"❌ Belgrano Ahorro respondió con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar a Belgrano Ahorro: {e}")
        return False

def test_belgrano_tickets():
    """Probar que Belgrano Tickets esté funcionando"""
    print("🔍 Verificando Belgrano Tickets...")
    
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Belgrano Tickets está funcionando")
            print(f"   Status: {data.get('status')}")
            print(f"   Tickets: {data.get('total_tickets', 0)}")
            return True
        else:
            print(f"❌ Belgrano Tickets respondió con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar a Belgrano Tickets: {e}")
        return False

def test_integracion_api():
    """Probar la integración via API"""
    print("🔍 Probando integración via API...")
    
    ticket_prueba = {
        'numero': f'TEST-{int(time.time())}',
        'cliente_nombre': 'Cliente de Prueba',
        'cliente_direccion': 'Av. Test 123, CABA',
        'cliente_telefono': '11-1234-5678',
        'cliente_email': 'test@ejemplo.com',
        'productos': [
            {
                'nombre': 'Arroz',
                'cantidad': 2,
                'precio': 500,
                'subtotal': 1000
            }
        ],
        'estado': 'pendiente',
        'prioridad': 'normal',
        'indicaciones': 'Ticket de prueba',
        'tipo_cliente': 'cliente',
        'metodo_pago': 'Efectivo',
        'total': 1000,
        'fecha_pedido': datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            "http://localhost:5001/api/tickets/recibir",
            json=ticket_prueba,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('exito'):
                print("✅ Ticket enviado exitosamente via API")
                return True
            else:
                print(f"❌ Error en respuesta: {result.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando ticket: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DE INTEGRACIÓN COMPLETA")
    print("=" * 50)
    
    belgrano_ahorro_ok = test_belgrano_ahorro()
    print()
    
    belgrano_tickets_ok = test_belgrano_tickets()
    print()
    
    if not belgrano_ahorro_ok or not belgrano_tickets_ok:
        print("❌ No se pueden probar los servicios")
        return False
    
    api_ok = test_integracion_api()
    print()
    
    print("📊 RESUMEN:")
    print(f"   Belgrano Ahorro: {'✅' if belgrano_ahorro_ok else '❌'}")
    print(f"   Belgrano Tickets: {'✅' if belgrano_tickets_ok else '❌'}")
    print(f"   API Integration: {'✅' if api_ok else '❌'}")
    
    if all([belgrano_ahorro_ok, belgrano_tickets_ok, api_ok]):
        print("🎉 ¡INTEGRACIÓN FUNCIONANDO!")
        return True
    else:
        print("❌ Hay problemas en la integración")
        return False

if __name__ == "__main__":
    main()
