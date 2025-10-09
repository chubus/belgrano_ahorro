#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente API completo para comunicación con Belgrano Ahorro
Métodos CRUD para todos los recursos
"""

import os
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BelgranoAhorroClient:
    """Cliente completo para comunicación con la API de Belgrano Ahorro"""
    
    def __init__(self):
        self.base_url = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
        self.api_key = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        self.timeout = 30
        
        # Headers por defecto
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Realizar request a la API con manejo de errores"""
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            logger.info(f"Making {method} request to {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Log de respuesta
            logger.info(f"Response status: {response.status_code}")
            
            # Manejar errores HTTP
            if response.status_code == 401:
                logger.error("Unauthorized: Invalid API key")
                return {'error': 'Invalid API key', 'status_code': 401}
            
            if response.status_code == 404:
                logger.error("Not found")
                return {'error': 'Resource not found', 'status_code': 404}
            
            if response.status_code >= 500:
                logger.error(f"Server error: {response.status_code}")
                return {'error': 'Server error', 'status_code': response.status_code}
            
            # Intentar parsear JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error("Invalid JSON response")
                return {'error': 'Invalid JSON response', 'status_code': response.status_code}
        
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return {'error': 'Request timeout', 'status_code': 408}
        
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            return {'error': 'Connection error', 'status_code': 503}
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {'error': str(e), 'status_code': 500}
    
    # =============================
    # MÉTODOS PARA NEGOCIOS
    # =============================
    
    def get_negocios(self) -> Dict:
        """Obtener todos los negocios"""
        return self._make_request('GET', 'negocios')
    
    def get_negocio(self, negocio_id: int) -> Dict:
        """Obtener negocio específico"""
        return self._make_request('GET', f'negocios/{negocio_id}')
    
    def create_negocio(self, negocio_data: Dict) -> Dict:
        """Crear nuevo negocio"""
        return self._make_request('POST', 'negocios', data=negocio_data)
    
    def update_negocio(self, negocio_id: int, negocio_data: Dict) -> Dict:
        """Actualizar negocio"""
        return self._make_request('PUT', f'negocios/{negocio_id}', data=negocio_data)
    
    def delete_negocio(self, negocio_id: int) -> Dict:
        """Eliminar negocio"""
        return self._make_request('DELETE', f'negocios/{negocio_id}')
    
    # =============================
    # MÉTODOS PARA SUCURSALES
    # =============================
    
    def get_sucursales(self) -> Dict:
        """Obtener todas las sucursales"""
        return self._make_request('GET', 'sucursales')
    
    def get_sucursal(self, sucursal_id: int) -> Dict:
        """Obtener sucursal específica"""
        return self._make_request('GET', f'sucursales/{sucursal_id}')
    
    def create_sucursal(self, sucursal_data: Dict) -> Dict:
        """Crear nueva sucursal"""
        return self._make_request('POST', 'sucursales', data=sucursal_data)
    
    def update_sucursal(self, sucursal_id: int, sucursal_data: Dict) -> Dict:
        """Actualizar sucursal"""
        return self._make_request('PUT', f'sucursales/{sucursal_id}', data=sucursal_data)
    
    def delete_sucursal(self, sucursal_id: int) -> Dict:
        """Eliminar sucursal"""
        return self._make_request('DELETE', f'sucursales/{sucursal_id}')
    
    # =============================
    # MÉTODOS PARA PRODUCTOS
    # =============================
    
    def get_productos(self) -> Dict:
        """Obtener todos los productos"""
        return self._make_request('GET', 'productos')
    
    def get_producto(self, producto_id: int) -> Dict:
        """Obtener producto específico"""
        return self._make_request('GET', f'productos/{producto_id}')
    
    def create_producto(self, producto_data: Dict) -> Dict:
        """Crear nuevo producto"""
        return self._make_request('POST', 'productos', data=producto_data)
    
    def update_producto(self, producto_id: int, producto_data: Dict) -> Dict:
        """Actualizar producto"""
        return self._make_request('PUT', f'productos/{producto_id}', data=producto_data)
    
    def delete_producto(self, producto_id: int) -> Dict:
        """Eliminar producto"""
        return self._make_request('DELETE', f'productos/{producto_id}')
    
    # =============================
    # MÉTODOS PARA OFERTAS
    # =============================
    
    def get_ofertas(self) -> Dict:
        """Obtener todas las ofertas"""
        return self._make_request('GET', 'ofertas')
    
    def get_oferta(self, oferta_id: int) -> Dict:
        """Obtener oferta específica"""
        return self._make_request('GET', f'ofertas/{oferta_id}')
    
    def create_oferta(self, oferta_data: Dict) -> Dict:
        """Crear nueva oferta"""
        return self._make_request('POST', 'ofertas', data=oferta_data)
    
    def update_oferta(self, oferta_id: int, oferta_data: Dict) -> Dict:
        """Actualizar oferta"""
        return self._make_request('PUT', f'ofertas/{oferta_id}', data=oferta_data)
    
    def delete_oferta(self, oferta_id: int) -> Dict:
        """Eliminar oferta"""
        return self._make_request('DELETE', f'ofertas/{oferta_id}')
    
    # =============================
    # MÉTODOS PARA PRECIOS
    # =============================
    
    def get_precios(self) -> Dict:
        """Obtener historial de precios"""
        return self._make_request('GET', 'precios')
    
    def update_precio(self, producto_id: int, precio_data: Dict) -> Dict:
        """Actualizar precio de producto"""
        return self._make_request('PUT', f'precios/{producto_id}', data=precio_data)
    
    # =============================
    # MÉTODOS DE UTILIDAD
    # =============================
    
    def health_check(self) -> Dict:
        """Verificar estado de la API"""
        return self._make_request('GET', 'health')
    
    def get_status(self) -> Dict:
        """Obtener estado detallado de la API"""
        return self._make_request('GET', 'status')
    
    def ping(self) -> Dict:
        """Ping simple"""
        return self._make_request('GET', 'ping')
    
    # =============================
    # MÉTODOS DE SINCRONIZACIÓN
    # =============================
    
    def sync_data(self, tipo_cambio: str, datos: Dict) -> bool:
        """Sincronizar datos con la API"""
        try:
            if tipo_cambio == 'negocio':
                if 'id' in datos:
                    return 'error' not in self.update_negocio(datos['id'], datos)
                else:
                    return 'error' not in self.create_negocio(datos)
            
            elif tipo_cambio == 'sucursal':
                if 'id' in datos:
                    return 'error' not in self.update_sucursal(datos['id'], datos)
                else:
                    return 'error' not in self.create_sucursal(datos)
            
            elif tipo_cambio == 'producto':
                if 'id' in datos:
                    return 'error' not in self.update_producto(datos['id'], datos)
                else:
                    return 'error' not in self.create_producto(datos)
            
            elif tipo_cambio == 'oferta':
                if 'id' in datos:
                    return 'error' not in self.update_oferta(datos['id'], datos)
                else:
                    return 'error' not in self.create_oferta(datos)
            
            elif tipo_cambio == 'precio':
                return 'error' not in self.update_precio(datos['producto_id'], datos)
            
            return False
            
        except Exception as e:
            logger.error(f"Error en sincronización: {e}")
            return False
    
    # =============================
    # MÉTODOS DE CONSULTA AVANZADA
    # =============================
    
    def get_negocios_activos(self) -> Dict:
        """Obtener solo negocios activos"""
        result = self.get_negocios()
        if 'error' in result:
            return result
        
        negocios_activos = [n for n in result.get('data', []) if n.get('activo', False)]
        return {
            'status': 'success',
            'data': negocios_activos,
            'total': len(negocios_activos)
        }
    
    def get_productos_por_negocio(self, negocio_id: int) -> Dict:
        """Obtener productos de un negocio específico"""
        result = self.get_productos()
        if 'error' in result:
            return result
        
        productos_negocio = [p for p in result.get('data', []) if p.get('negocio_id') == negocio_id]
        return {
            'status': 'success',
            'data': productos_negocio,
            'total': len(productos_negocio)
        }
    
    def get_sucursales_por_negocio(self, negocio_id: int) -> Dict:
        """Obtener sucursales de un negocio específico"""
        result = self.get_sucursales()
        if 'error' in result:
            return result
        
        sucursales_negocio = [s for s in result.get('data', []) if s.get('negocio_id') == negocio_id]
        return {
            'status': 'success',
            'data': sucursales_negocio,
            'total': len(sucursales_negocio)
        }
    
    def get_ofertas_activas(self) -> Dict:
        """Obtener solo ofertas activas"""
        result = self.get_ofertas()
        if 'error' in result:
            return result
        
        ofertas_activas = [o for o in result.get('data', []) if o.get('activa', False)]
        return {
            'status': 'success',
            'data': ofertas_activas,
            'total': len(ofertas_activas)
        }

# Instancia global del cliente
belgrano_client = BelgranoAhorroClient()

def test_connection():
    """Probar conexión con Belgrano Ahorro"""
    try:
        logger.info("Testing connection to Belgrano Ahorro API...")
        
        # Health check
        health = belgrano_client.health_check()
        if 'error' in health:
            logger.error(f"Health check failed: {health['error']}")
            return False
        
        logger.info("✅ Connection successful")
        return True
    
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False

def get_client():
    """Obtener instancia del cliente"""
    return belgrano_client

if __name__ == "__main__":
    # Probar conexión
    if test_connection():
        print("✅ Belgrano Ahorro API connection successful")
        
        # Probar algunos métodos
        print("\n📊 Probando métodos básicos...")
        
        # Health check
        health = belgrano_client.health_check()
        print(f"Health: {health}")
        
        # Status
        status = belgrano_client.get_status()
        print(f"Status: {status}")
        
        # Listar negocios
        negocios = belgrano_client.get_negocios()
        print(f"Negocios: {len(negocios.get('data', []))} encontrados")
        
    else:
        print("❌ Belgrano Ahorro API connection failed")