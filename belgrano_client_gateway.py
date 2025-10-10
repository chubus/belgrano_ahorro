#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente API mejorado para comunicación con Belgrano Ahorro a través del Gateway
Incluye retry logic, cache, y sincronización en tiempo real
"""

import os
import requests
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BelgranoAhorroClientGateway:
    """Cliente mejorado para comunicación con Belgrano Ahorro a través del Gateway"""
    
    def __init__(self, use_gateway=True):
        self.use_gateway = use_gateway
        
        if use_gateway:
            # Usar API Gateway unificado
            self.base_url = os.getenv('GATEWAY_URL', 'http://localhost:5003/gateway')
            self.api_key = os.getenv('GATEWAY_API_KEY', 'devops_api_key_2025')
        else:
            # Conexión directa
            self.base_url = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
            self.api_key = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        
        self.timeout = int(os.getenv('API_TIMEOUT', '30'))
        self.retry_attempts = int(os.getenv('API_RETRY_ATTEMPTS', '3'))
        self.retry_delay = int(os.getenv('API_RETRY_DELAY', '1'))
        
        # Cache para optimizar requests
        self.cache = {}
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))  # 5 minutos
        
        # Headers por defecto
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Source': 'devops'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None, use_cache: bool = True) -> Dict:
        """Realizar request a la API con retry logic y cache"""
        
        # Verificar cache para GET requests
        if method == 'GET' and use_cache and endpoint in self.cache:
            cached_data, timestamp = self.cache[endpoint]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.info(f"Cache hit for {endpoint}")
                return cached_data
        
        url = f"{self.base_url}/{endpoint}" if self.use_gateway else f"{self.base_url}/api/{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
                
                # Log de respuesta
                logger.info(f"Response: {response.status_code} - {response.reason}")
                
                if response.status_code == 200:
                    result = response.json() if response.content else {}
                    
                    # Guardar en cache para GET requests
                    if method == 'GET' and use_cache:
                        self.cache[endpoint] = (result, datetime.now())
                    
                    return {
                        'success': True,
                        'data': result,
                        'status_code': response.status_code
                    }
                elif response.status_code == 401:
                    logger.error("API Key inválida")
                    return {
                        'success': False,
                        'error': 'API Key inválida',
                        'status_code': 401
                    }
                elif response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    logger.error(f"API Error {response.status_code}: {error_data}")
                    return {
                        'success': False,
                        'error': error_data.get('error', f'HTTP {response.status_code}'),
                        'status_code': response.status_code
                    }
                else:
                    return {
                        'success': True,
                        'data': response.json() if response.content else {},
                        'status_code': response.status_code
                    }
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en intento {attempt + 1}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Request timeout',
                        'status_code': 408
                    }
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error en intento {attempt + 1}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Connection error',
                        'status_code': 503
                    }
                    
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'status_code': 500
                }
        
        return {
            'success': False,
            'error': 'Max retry attempts exceeded',
            'status_code': 500
        }
    
    def clear_cache(self):
        """Limpiar cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_sync_status(self) -> Dict:
        """Obtener estado de sincronización"""
        if self.use_gateway:
            return self._make_request('GET', 'sync/status')
        else:
            return self._make_request('GET', 'health')
    
    def force_sync(self) -> Dict:
        """Forzar sincronización completa"""
        if self.use_gateway:
            return self._make_request('POST', 'sync/force')
        else:
            return {'success': False, 'error': 'Sync not available without gateway'}
    
    # =============================
    # MÉTODOS CRUD PARA NEGOCIOS
    # =============================
    
    def get_negocios(self) -> Dict:
        """Obtener todos los negocios"""
        return self._make_request('GET', 'negocios')
    
    def get_negocio(self, negocio_id: int) -> Dict:
        """Obtener negocio específico"""
        return self._make_request('GET', f'negocios/{negocio_id}')
    
    def create_negocio(self, negocio_data: Dict) -> Dict:
        """Crear nuevo negocio"""
        self.clear_cache()  # Limpiar cache al crear
        return self._make_request('POST', 'negocios', negocio_data)
    
    def update_negocio(self, negocio_id: int, negocio_data: Dict) -> Dict:
        """Actualizar negocio"""
        self.clear_cache()  # Limpiar cache al actualizar
        return self._make_request('PUT', f'negocios/{negocio_id}', negocio_data)
    
    def delete_negocio(self, negocio_id: int) -> Dict:
        """Eliminar negocio"""
        self.clear_cache()  # Limpiar cache al eliminar
        return self._make_request('DELETE', f'negocios/{negocio_id}')
    
    # =============================
    # MÉTODOS CRUD PARA PRODUCTOS
    # =============================
    
    def get_productos(self) -> Dict:
        """Obtener todos los productos"""
        return self._make_request('GET', 'productos')
    
    def get_producto(self, producto_id: int) -> Dict:
        """Obtener producto específico"""
        return self._make_request('GET', f'productos/{producto_id}')
    
    def create_producto(self, producto_data: Dict) -> Dict:
        """Crear nuevo producto"""
        self.clear_cache()
        return self._make_request('POST', 'productos', producto_data)
    
    def update_producto(self, producto_id: int, producto_data: Dict) -> Dict:
        """Actualizar producto"""
        self.clear_cache()
        return self._make_request('PUT', f'productos/{producto_id}', producto_data)
    
    def delete_producto(self, producto_id: int) -> Dict:
        """Eliminar producto"""
        self.clear_cache()
        return self._make_request('DELETE', f'productos/{producto_id}')
    
    # =============================
    # MÉTODOS CRUD PARA OFERTAS
    # =============================
    
    def get_ofertas(self) -> Dict:
        """Obtener todas las ofertas"""
        return self._make_request('GET', 'ofertas')
    
    def get_oferta(self, oferta_id: int) -> Dict:
        """Obtener oferta específica"""
        return self._make_request('GET', f'ofertas/{oferta_id}')
    
    def create_oferta(self, oferta_data: Dict) -> Dict:
        """Crear nueva oferta"""
        self.clear_cache()
        return self._make_request('POST', 'ofertas', oferta_data)
    
    def update_oferta(self, oferta_id: int, oferta_data: Dict) -> Dict:
        """Actualizar oferta"""
        self.clear_cache()
        return self._make_request('PUT', f'ofertas/{oferta_id}', oferta_data)
    
    def delete_oferta(self, oferta_id: int) -> Dict:
        """Eliminar oferta"""
        self.clear_cache()
        return self._make_request('DELETE', f'ofertas/{oferta_id}')
    
    # =============================
    # MÉTODOS CRUD PARA SUCURSALES
    # =============================
    
    def get_sucursales(self) -> Dict:
        """Obtener todas las sucursales"""
        return self._make_request('GET', 'sucursales')
    
    def get_sucursal(self, sucursal_id: int) -> Dict:
        """Obtener sucursal específica"""
        return self._make_request('GET', f'sucursales/{sucursal_id}')
    
    def create_sucursal(self, sucursal_data: Dict) -> Dict:
        """Crear nueva sucursal"""
        self.clear_cache()
        return self._make_request('POST', 'sucursales', sucursal_data)
    
    def update_sucursal(self, sucursal_id: int, sucursal_data: Dict) -> Dict:
        """Actualizar sucursal"""
        self.clear_cache()
        return self._make_request('PUT', f'sucursales/{sucursal_id}', sucursal_data)
    
    def delete_sucursal(self, sucursal_id: int) -> Dict:
        """Eliminar sucursal"""
        self.clear_cache()
        return self._make_request('DELETE', f'sucursales/{sucursal_id}')
    
    # =============================
    # MÉTODOS PARA PRECIOS
    # =============================
    
    def get_precios(self, producto_id: int) -> Dict:
        """Obtener precios de un producto"""
        return self._make_request('GET', f'precios/{producto_id}')
    
    def update_precio(self, producto_id: int, precio_data: Dict) -> Dict:
        """Actualizar precio de un producto"""
        self.clear_cache()
        return self._make_request('PUT', f'precios/{producto_id}', precio_data)
    
    # =============================
    # MÉTODOS DE UTILIDAD
    # =============================
    
    def test_connection(self) -> Dict:
        """Probar conexión con la API"""
        return self.get_sync_status()
    
    def get_health(self) -> Dict:
        """Obtener estado de salud de la API"""
        if self.use_gateway:
            return self._make_request('GET', 'health')
        else:
            return self._make_request('GET', 'health')
    
    def get_cache_info(self) -> Dict:
        """Obtener información del cache"""
        return {
            'cache_size': len(self.cache),
            'cache_keys': list(self.cache.keys()),
            'cache_ttl': self.cache_ttl
        }

# Instancia global del cliente
client = BelgranoAhorroClientGateway(use_gateway=True)

# Funciones de conveniencia para uso directo
def get_negocios():
    """Obtener todos los negocios"""
    return client.get_negocios()

def create_negocio(data):
    """Crear negocio"""
    return client.create_negocio(data)

def update_negocio(negocio_id, data):
    """Actualizar negocio"""
    return client.update_negocio(negocio_id, data)

def delete_negocio(negocio_id):
    """Eliminar negocio"""
    return client.delete_negocio(negocio_id)

def get_productos():
    """Obtener todos los productos"""
    return client.get_productos()

def create_producto(data):
    """Crear producto"""
    return client.create_producto(data)

def update_producto(producto_id, data):
    """Actualizar producto"""
    return client.update_producto(producto_id, data)

def delete_producto(producto_id):
    """Eliminar producto"""
    return client.delete_producto(producto_id)

def get_ofertas():
    """Obtener todas las ofertas"""
    return client.get_ofertas()

def create_oferta(data):
    """Crear oferta"""
    return client.create_oferta(data)

def update_oferta(oferta_id, data):
    """Actualizar oferta"""
    return client.update_oferta(oferta_id, data)

def delete_oferta(oferta_id):
    """Eliminar oferta"""
    return client.delete_oferta(oferta_id)

def get_sucursales():
    """Obtener todas las sucursales"""
    return client.get_sucursales()

def create_sucursal(data):
    """Crear sucursal"""
    return client.create_sucursal(data)

def update_sucursal(sucursal_id, data):
    """Actualizar sucursal"""
    return client.update_sucursal(sucursal_id, data)

def delete_sucursal(sucursal_id):
    """Eliminar sucursal"""
    return client.delete_sucursal(sucursal_id)

def force_sync():
    """Forzar sincronización"""
    return client.force_sync()

def get_sync_status():
    """Obtener estado de sincronización"""
    return client.get_sync_status()

# Crear aplicación Flask para ejecución directa
if __name__ == "__main__":
    print("🔧 Cliente API Gateway para Belgrano Ahorro")
    print("=" * 50)
    
    # Probar conexión
    print("1. Probando conexión...")
    status = client.test_connection()
    print(f"   Status: {status}")
    
    # Probar obtención de datos
    print("\n2. Probando obtención de negocios...")
    negocios = client.get_negocios()
    print(f"   Negocios: {negocios}")
    
    # Probar cache
    print("\n3. Información del cache...")
    cache_info = client.get_cache_info()
    print(f"   Cache: {cache_info}")
    
    print("\n✅ Cliente API Gateway funcionando correctamente")
