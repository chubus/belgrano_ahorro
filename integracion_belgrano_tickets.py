#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de integración entre Belgrano Ahorro y Belgrano Tickets
Permite enviar tickets automáticamente cuando se procesa un pedido
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BelgranoTicketsAPI:
    """
    Cliente API para comunicarse con Belgrano Tickets
    """
    
    def __init__(self, base_url: str = "http://localhost:5001", timeout: int = 10):
        """
        Inicializar cliente API
        
        Args:
            base_url: URL base de Belgrano Tickets
            timeout: Timeout para requests en segundos
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Headers por defecto
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BelgranoAhorro-Integration/1.0'
        })
    
    def verificar_conexion(self) -> bool:
        """
        Verificar si Belgrano Tickets está disponible
        
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Belgrano Tickets disponible: {data.get('status', 'unknown')}")
                return True
            else:
                logger.warning(f"⚠️ Belgrano Tickets respondió con status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ No se puede conectar a Belgrano Tickets en {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout al conectar con Belgrano Tickets")
            return False
        except Exception as e:
            logger.error(f"❌ Error verificando conexión: {e}")
            return False
    
    def enviar_ticket(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Enviar ticket a Belgrano Tickets
        
        Args:
            ticket_data: Datos del ticket a enviar
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            # Preparar datos para la API
            api_data = {
                'numero': ticket_data.get('numero'),
                'cliente_nombre': ticket_data.get('cliente_nombre'),
                'cliente_direccion': ticket_data.get('direccion'),
                'cliente_telefono': ticket_data.get('telefono', ''),
                'cliente_email': ticket_data.get('email'),
                'productos': ticket_data.get('productos', []),
                'estado': 'pendiente',
                'prioridad': 'alta' if ticket_data.get('tipo_cliente') == 'comerciante' else 'normal',
                'indicaciones': ticket_data.get('indicaciones', ''),
                'tipo_cliente': ticket_data.get('tipo_cliente', 'cliente'),
                'metodo_pago': ticket_data.get('metodo_pago', ''),
                'total': ticket_data.get('total', 0),
                'fecha_pedido': ticket_data.get('fecha', datetime.now().isoformat())
            }
            
            # Validar datos requeridos
            if not all([api_data['numero'], api_data['cliente_nombre'], api_data['cliente_direccion']]):
                logger.error("❌ Datos incompletos para enviar ticket")
                return False
            
            # Enviar ticket
            response = self.session.post(
                f"{self.base_url}/api/tickets/recibir",
                json=api_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('exito'):
                    logger.info(f"✅ Ticket enviado exitosamente: {api_data['numero']}")
                    logger.info(f"   Repartidor asignado: {result.get('repartidor_asignado', 'Automático')}")
                    return True
                else:
                    logger.error(f"❌ Error en respuesta de Belgrano Tickets: {result.get('error')}")
                    return False
            else:
                logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ No se puede conectar a Belgrano Tickets")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout al enviar ticket")
            return False
        except Exception as e:
            logger.error(f"❌ Error enviando ticket: {e}")
            return False
    
    def obtener_estado_ticket(self, numero_ticket: str) -> Optional[Dict[str, Any]]:
        """
        Obtener estado de un ticket específico
        
        Args:
            numero_ticket: Número del ticket a consultar
            
        Returns:
            Dict con información del ticket o None si no se encuentra
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/tickets/{numero_ticket}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ No se pudo obtener estado del ticket {numero_ticket}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del ticket: {e}")
            return None
    
    def obtener_estadisticas(self) -> Optional[Dict[str, Any]]:
        """
        Obtener estadísticas generales de Belgrano Tickets
        
        Returns:
            Dict con estadísticas o None si no se puede obtener
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/estadisticas",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("⚠️ No se pudieron obtener estadísticas")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return None

def test_integracion():
    """
    Función de prueba para verificar la integración
    """
    print("🧪 PRUEBA DE INTEGRACIÓN - BELGRANO TICKETS")
    print("=" * 50)
    
    # Crear instancia de la API
    api = BelgranoTicketsAPI()
    
    # Verificar conexión
    print("\n1️⃣ Verificando conexión...")
    if api.verificar_conexion():
        print("✅ Conexión exitosa")
    else:
        print("❌ No se pudo conectar")
        return False
    
    # Enviar ticket de prueba
    print("\n2️⃣ Enviando ticket de prueba...")
    ticket_prueba = {
        'numero': 'TEST-001',
        'cliente_nombre': 'Cliente de Prueba',
        'direccion': 'Av. Test 123, CABA',
        'telefono': '11-1234-5678',
        'email': 'test@ejemplo.com',
        'productos': [
            {
                'nombre': 'Producto de Prueba',
                'cantidad': 2,
                'precio': 100,
                'subtotal': 200
            }
        ],
        'total': 200,
        'metodo_pago': 'Efectivo',
        'fecha': datetime.now().isoformat(),
        'indicaciones': 'Ticket de prueba para verificar integración',
        'tipo_cliente': 'cliente'
    }
    
    if api.enviar_ticket(ticket_prueba):
        print("✅ Ticket de prueba enviado exitosamente")
    else:
        print("❌ Error enviando ticket de prueba")
        return False
    
    # Obtener estadísticas
    print("\n3️⃣ Obteniendo estadísticas...")
    stats = api.obtener_estadisticas()
    if stats:
        print(f"✅ Estadísticas obtenidas: {stats.get('total_tickets', 0)} tickets")
    else:
        print("⚠️ No se pudieron obtener estadísticas")
    
    print("\n🎉 Prueba de integración completada")
    return True

if __name__ == "__main__":
    test_integracion()
