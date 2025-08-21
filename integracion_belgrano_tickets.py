#!/usr/bin/env python3
"""
Script de integración entre Belgrano Ahorro y Belgrano Tickets
Permite enviar tickets de pedidos completados a la plataforma de gestión
"""

import requests
import json
import os
from datetime import datetime

class BelgranoTicketsAPI:
    def __init__(self, base_url="http://localhost:5001"):
        """
        Inicializar conexión con Belgrano Tickets
        
        Args:
            base_url (str): URL base de la API de Belgrano Tickets
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/tickets"
        
    def enviar_ticket(self, pedido_data):
        """
        Enviar un ticket de pedido a Belgrano Tickets
        
        Args:
            pedido_data (dict): Datos del pedido completado
            
        Returns:
            dict: Respuesta de la API
        """
        try:
            # Preparar datos del ticket
            ticket_data = {
                'numero': f"PED-{pedido_data['numero']}",
                'cliente_nombre': pedido_data['cliente_nombre'],
                'cliente_direccion': pedido_data['direccion'],
                'cliente_telefono': pedido_data.get('telefono', ''),
                'cliente_email': pedido_data.get('email', ''),
                'productos': pedido_data.get('productos', []),
                'prioridad': 'alta' if pedido_data.get('tipo_cliente') == 'comerciante' else 'normal',
                'indicaciones': pedido_data.get('indicaciones', ''),
                'total': pedido_data.get('total', 0),
                'metodo_pago': pedido_data.get('metodo_pago', ''),
                'fecha_pedido': pedido_data.get('fecha', ''),
                'tipo_cliente': pedido_data.get('tipo_cliente', 'cliente')
            }
            
            # Enviar POST a la API
            response = requests.post(
                self.api_endpoint,
                json=ticket_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                tipo_cliente = ticket_data.get('tipo_cliente', 'cliente').title()
                print(f"✅ Ticket enviado exitosamente: {ticket_data['numero']} ({tipo_cliente})")
                return response.json()
            else:
                print(f"❌ Error al enviar ticket: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión con Belgrano Tickets: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def verificar_conexion(self):
        """
        Verificar si Belgrano Tickets está disponible
        
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False

# Función para integrar con la aplicación principal
def integrar_con_belgrano_ahorro():
    """
    Función para ser llamada desde la aplicación principal
    cuando se complete un pedido
    """
    api = BelgranoTicketsAPI()
    
    if not api.verificar_conexion():
        print("⚠️ Belgrano Tickets no está disponible")
        return False
    
    return api

# Ejemplo de uso
if __name__ == "__main__":
    # Probar conexión
    api = BelgranoTicketsAPI()
    
    if api.verificar_conexion():
        print("✅ Conexión exitosa con Belgrano Tickets")
        
        # Ejemplo de envío de ticket
        pedido_ejemplo = {
            'numero': '001',
            'cliente_nombre': 'Juan Pérez',
            'direccion': 'Av. Belgrano 123, CABA',
            'telefono': '11-1234-5678',
            'email': 'juan@ejemplo.com',
            'productos': [
                {'nombre': 'Arroz', 'cantidad': 2, 'precio': 500},
                {'nombre': 'Aceite', 'cantidad': 1, 'precio': 800}
            ],
            'total': 1800,
            'metodo_pago': 'Efectivo',
            'fecha': datetime.now().isoformat(),
            'indicaciones': 'Entregar antes de las 18:00'
        }
        
        resultado = api.enviar_ticket(pedido_ejemplo)
        if resultado:
            print(f"Ticket creado con ID: {resultado.get('ticket_id')}")
    else:
        print("❌ No se pudo conectar con Belgrano Tickets")
        print("Asegúrate de que esté ejecutándose en http://localhost:5001")
