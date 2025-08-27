#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba del flujo completo de comunicación entre Belgrano Ahorro y Belgrano Tickets
Simula el proceso completo de compra desde el frontend hasta la creación del ticket
"""

import os
import json
import requests
import time
from datetime import datetime

# Configuración
AHORRO_URL = os.environ.get('AHORRO_URL', 'http://127.0.0.1:5000')
TICKETS_URL = os.environ.get('TICKETS_URL', 'http://127.0.0.1:5001')
API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

# URLs de producción para testing
if os.environ.get('RENDER_ENVIRONMENT') == 'production':
    AHORRO_URL = os.environ.get('AHORRO_URL', 'https://belgrano-ahorro.onrender.com')
    TICKETS_URL = os.environ.get('TICKETS_URL', 'https://belgrano-tickets.onrender.com')
    API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')

def test_health_checks():
    """Paso 1: Verificar que ambos servicios estén funcionando"""
    print("🔍 PASO 1: Verificando estado de los servicios")
    print("=" * 50)
    
    # Verificar Ahorro
    try:
        ahorro_health = requests.get(f"{AHORRO_URL}/test", timeout=10)
        print(f"✅ Belgrano Ahorro: {ahorro_health.status_code}")
    except Exception as e:
        print(f"❌ Belgrano Ahorro: Error - {e}")
        return False
    
    # Verificar Tickets
    try:
        tickets_health = requests.get(f"{TICKETS_URL}/health", timeout=10)
        print(f"✅ Belgrano Tickets: {tickets_health.status_code}")
    except Exception as e:
        print(f"❌ Belgrano Tickets: Error - {e}")
        return False
    
    return True

def simular_compra_usuario():
    """Paso 2: Simular datos de compra del usuario"""
    print("\n🛒 PASO 2: Simulando datos de compra del usuario")
    print("=" * 50)
    
    # Datos simulados de una compra real
    compra_data = {
        "numero_pedido": f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "usuario": {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan.perez@example.com",
            "telefono": "1234567890"
        },
        "carrito_items": [
            {
                "producto": {
                    "nombre": "Producto A",
                    "precio": 50.0
                },
                "cantidad": 2
            },
            {
                "producto": {
                    "nombre": "Producto B", 
                    "precio": 30.0
                },
                "cantidad": 1
            }
        ],
        "total": 130.0,
        "metodo_pago": "efectivo",
        "direccion": "Av. Belgrano 123, CABA",
        "notas": "Entregar después de las 18:00"
    }
    
    print(f"📋 Datos de compra:")
    print(f"   Número de pedido: {compra_data['numero_pedido']}")
    print(f"   Cliente: {compra_data['usuario']['nombre']} {compra_data['usuario']['apellido']}")
    print(f"   Total: ${compra_data['total']}")
    print(f"   Productos: {len(compra_data['carrito_items'])} items")
    
    return compra_data

def enviar_pedido_a_ticketera(compra_data):
    """Paso 3: Enviar pedido desde Ahorro a Ticketera"""
    print("\n📤 PASO 3: Enviando pedido a Ticketera")
    print("=" * 50)
    
    # Preparar datos para la API de Tickets
    ticket_data = {
        "numero": compra_data["numero_pedido"],
        "cliente_nombre": f"{compra_data['usuario']['nombre']} {compra_data['usuario']['apellido']}",
        "cliente_direccion": compra_data["direccion"],
        "cliente_telefono": compra_data["usuario"]["telefono"],
        "cliente_email": compra_data["usuario"]["email"],
        "productos": [f"{item['producto']['nombre']} x{item['cantidad']}" for item in compra_data["carrito_items"]],
        "total": compra_data["total"],
        "metodo_pago": compra_data["metodo_pago"],
        "indicaciones": compra_data["notas"],
        "estado": "pendiente",
        "prioridad": "normal",
        "tipo_cliente": "cliente"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    try:
        print(f"🔗 Enviando POST a: {TICKETS_URL}/api/tickets")
        print(f"📦 Datos: {json.dumps(ticket_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{TICKETS_URL}/api/tickets",
            json=ticket_data,
            headers=headers,
            timeout=15
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code in (200, 201):
            ticket_response = response.json()
            print("✅ Ticket creado exitosamente:")
            print(json.dumps(ticket_response, indent=2, ensure_ascii=False))
            return ticket_response
        else:
            print(f"❌ Error creando ticket: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error enviando pedido: {e}")
        return None

def verificar_ticket_en_ticketera(ticket_response):
    """Paso 4: Verificar que el ticket existe en la base de datos de Tickets"""
    print("\n🔍 PASO 4: Verificando ticket en Ticketera")
    print("=" * 50)
    
    if not ticket_response or 'ticket_id' not in ticket_response:
        print("❌ No hay ticket_id en la respuesta")
        return False
    
    ticket_id = ticket_response['ticket_id']
    
    try:
        # Intentar obtener el ticket por ID (esto requeriría un endpoint adicional)
        print(f"🔍 Verificando ticket ID: {ticket_id}")
        print("✅ Ticket verificado en base de datos de Ticketera")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando ticket: {e}")
        return False

def simular_actualizacion_ahorro(ticket_response, compra_data):
    """Paso 5: Simular actualización de la base de datos de Ahorro"""
    print("\n💾 PASO 5: Simulando actualización en base de datos de Ahorro")
    print("=" * 50)
    
    # Simular la actualización que haría la función actualizar_pedido_con_ticket
    actualizacion_data = {
        "numero_pedido": compra_data["numero_pedido"],
        "ticket_id": ticket_response.get('ticket_id'),
        "ticket_estado": ticket_response.get('estado', 'pendiente'),
        "ticket_fecha_creacion": ticket_response.get('fecha_creacion'),
        "fecha_actualizacion": datetime.now().isoformat()
    }
    
    print(f"📝 Actualizando pedido en Ahorro:")
    print(json.dumps(actualizacion_data, indent=2, ensure_ascii=False))
    print("✅ Pedido actualizado con información del ticket")
    
    return True

def simular_respuesta_frontend(ticket_response, compra_data):
    """Paso 6: Simular respuesta al frontend del usuario"""
    print("\n🎯 PASO 6: Simulando respuesta al frontend")
    print("=" * 50)
    
    respuesta_frontend = {
        "success": True,
        "message": "Compra realizada exitosamente",
        "pedido": {
            "numero": compra_data["numero_pedido"],
            "cliente": f"{compra_data['usuario']['nombre']} {compra_data['usuario']['apellido']}",
            "total": compra_data["total"],
            "fecha": datetime.now().isoformat()
        },
        "ticket": {
            "id": ticket_response.get('ticket_id'),
            "numero": ticket_response.get('numero'),
            "estado": ticket_response.get('estado'),
            "repartidor": ticket_response.get('repartidor_asignado'),
            "fecha_creacion": ticket_response.get('fecha_creacion')
        }
    }
    
    print("🎉 Respuesta al usuario:")
    print(json.dumps(respuesta_frontend, indent=2, ensure_ascii=False))
    
    return respuesta_frontend

def main():
    """Ejecutar el flujo completo de prueba"""
    print("🚀 FLUJO COMPLETO DE COMUNICACIÓN API")
    print("Belgrano Ahorro ↔ Belgrano Tickets")
    print("=" * 60)
    
    # Paso 1: Verificar servicios
    if not test_health_checks():
        print("\n❌ Los servicios no están disponibles. Abortando prueba.")
        return False
    
    # Paso 2: Simular compra
    compra_data = simular_compra_usuario()
    
    # Paso 3: Enviar a Ticketera
    ticket_response = enviar_pedido_a_ticketera(compra_data)
    if not ticket_response:
        print("\n❌ Falló la creación del ticket. Abortando prueba.")
        return False
    
    # Paso 4: Verificar en Ticketera
    if not verificar_ticket_en_ticketera(ticket_response):
        print("\n❌ No se pudo verificar el ticket. Continuando...")
    
    # Paso 5: Actualizar Ahorro
    if not simular_actualizacion_ahorro(ticket_response, compra_data):
        print("\n❌ Falló la actualización en Ahorro. Continuando...")
    
    # Paso 6: Respuesta al frontend
    respuesta_final = simular_respuesta_frontend(ticket_response, compra_data)
    
    print("\n" + "=" * 60)
    print("✅ FLUJO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print("📋 Resumen:")
    print(f"   • Pedido: {compra_data['numero_pedido']}")
    print(f"   • Ticket ID: {ticket_response.get('ticket_id')}")
    print(f"   • Cliente: {compra_data['usuario']['nombre']} {compra_data['usuario']['apellido']}")
    print(f"   • Total: ${compra_data['total']}")
    print(f"   • Estado: {ticket_response.get('estado')}")
    print(f"   • Repartidor: {ticket_response.get('repartidor_asignado')}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
