#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente API central para Belgrano Ahorro
Proporciona funciones reutilizables para todas las operaciones CRUD
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configuración de logging
logger = logging.getLogger(__name__)

class BelgranoAhorroAPIClient:
    """Cliente API para Belgrano Ahorro con funciones reutilizables"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Inicializar cliente API
        
        Args:
            base_url: URL base de la API (por defecto desde variables de entorno)
            api_key: Clave API (por defecto desde variables de entorno)
        """
        self.base_url = base_url or os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
        self.api_key = api_key or os.environ.get('BELGRANO_AHORRO_API_KEY')
        self.timeout = 30
        
        # Headers por defecto
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key
        
        logger.info(f"Cliente API inicializado para: {self.base_url}")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """
        Realizar petición HTTP a la API
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint de la API (ej: '/api/negocios')
            data: Datos para enviar en el body
            params: Parámetros de query string
            
        Returns:
            Dict con la respuesta o None si hay error
        """
        url = f"{self.base_url}{endpoint}"
        
        # Reintentos con backoff exponencial para tolerar 5xx/cold-starts y errores transitorios
        max_attempts = 4
        backoff_base_seconds = 1.5
        last_error: Optional[Dict] = None
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Realizando {method} a {url} (intento {attempt}/{max_attempts})")
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
                logger.info(f"Respuesta {response.status_code} de {url}")

                if response.status_code in (200, 201, 204):
                    try:
                        return response.json()
                    except ValueError:
                        return {'status': 'success', 'message': 'Operación exitosa'}

                # Reintentar ante 502/503/504
                if response.status_code in (502, 503, 504):
                    last_error = {
                        'error': True,
                        'status_code': response.status_code,
                        'message': response.text
                    }
                    if attempt < max_attempts:
                        import time
                        sleep_s = backoff_base_seconds ** attempt
                        logger.warning(f"Respuesta {response.status_code} en {url}. Reintentando en {sleep_s:.1f}s...")
                        time.sleep(sleep_s)
                        continue
                    return last_error

                # Otros errores no reintentables
                logger.error(f"Error {response.status_code}: {response.text}")
                return {
                    'error': True,
                    'status_code': response.status_code,
                    'message': response.text
                }

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_error = {'error': True, 'message': str(e)}
                if attempt < max_attempts:
                    import time
                    sleep_s = backoff_base_seconds ** attempt
                    logger.warning(f"{type(e).__name__} en {url}. Reintento en {sleep_s:.1f}s...")
                    time.sleep(sleep_s)
                    continue
                logger.error(f"Error persistente accediendo a {url}: {e}")
                return last_error
            except Exception as e:
                logger.error(f"Error inesperado en {url}: {e}")
                return {'error': True, 'message': str(e)}

        # Fallback si nunca retornó (no debería alcanzarse)
        return last_error or {'error': True, 'message': 'Error desconocido'}
    
    # =================================================================
    # NEGOCIOS
    # =================================================================
    
    def get_negocios(self) -> List[Dict]:
        """Obtener lista de negocios"""
        response = self._make_request('GET', '/api/v1/negocios')
        if response and not response.get('error'):
            return response.get('data', []) if isinstance(response, dict) else response
        return []
    
    def get_negocio(self, negocio_id: int) -> Optional[Dict]:
        """Obtener un negocio específico"""
        response = self._make_request('GET', f'/api/v1/negocios/{negocio_id}')
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def create_negocio(self, data: Dict) -> Optional[Dict]:
        """Crear nuevo negocio"""
        response = self._make_request('POST', '/api/v1/negocios', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def update_negocio(self, negocio_id: int, data: Dict) -> Optional[Dict]:
        """Actualizar negocio existente"""
        response = self._make_request('PUT', f'/api/v1/negocios/{negocio_id}', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def delete_negocio(self, negocio_id: int) -> bool:
        """Eliminar negocio"""
        response = self._make_request('DELETE', f'/api/v1/negocios/{negocio_id}')
        return response and not response.get('error')
    
    # =================================================================
    # PRODUCTOS
    # =================================================================
    
    def get_productos(self) -> List[Dict]:
        """Obtener lista de productos"""
        response = self._make_request('GET', '/api/v1/productos')
        if response and not response.get('error'):
            return response.get('data', []) if isinstance(response, dict) else response
        return []
    
    def get_producto(self, producto_id: int) -> Optional[Dict]:
        """Obtener un producto específico"""
        response = self._make_request('GET', f'/api/v1/productos/{producto_id}')
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def create_producto(self, data: Dict) -> Optional[Dict]:
        """Crear nuevo producto"""
        response = self._make_request('POST', '/api/v1/productos', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def update_producto(self, producto_id: int, data: Dict) -> Optional[Dict]:
        """Actualizar producto existente"""
        response = self._make_request('PUT', f'/api/v1/productos/{producto_id}', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def delete_producto(self, producto_id: int) -> bool:
        """Eliminar producto"""
        response = self._make_request('DELETE', f'/api/v1/productos/{producto_id}')
        return response and not response.get('error')
    
    # =================================================================
    # OFERTAS
    # =================================================================
    
    def get_ofertas(self) -> List[Dict]:
        """Obtener lista de ofertas"""
        response = self._make_request('GET', '/api/v1/ofertas')
        if response and not response.get('error'):
            return response.get('data', []) if isinstance(response, dict) else response
        return []
    
    def get_oferta(self, oferta_id: int) -> Optional[Dict]:
        """Obtener una oferta específica"""
        response = self._make_request('GET', f'/api/v1/ofertas/{oferta_id}')
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def create_oferta(self, data: Dict) -> Optional[Dict]:
        """Crear nueva oferta"""
        response = self._make_request('POST', '/api/v1/ofertas', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def update_oferta(self, oferta_id: int, data: Dict) -> Optional[Dict]:
        """Actualizar oferta existente"""
        response = self._make_request('PUT', f'/api/v1/ofertas/{oferta_id}', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def delete_oferta(self, oferta_id: int) -> bool:
        """Eliminar oferta"""
        response = self._make_request('DELETE', f'/api/v1/ofertas/{oferta_id}')
        return response and not response.get('error')
    
    # =================================================================
    # PRECIOS
    # =================================================================
    
    def get_precios(self) -> List[Dict]:
        """Obtener lista de precios"""
        response = self._make_request('GET', '/api/v1/precios')
        if response and not response.get('error'):
            return response.get('data', []) if isinstance(response, dict) else response
        return []
    
    def get_precio(self, precio_id: int) -> Optional[Dict]:
        """Obtener un precio específico"""
        response = self._make_request('GET', f'/api/v1/precios/{precio_id}')
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def create_precio(self, data: Dict) -> Optional[Dict]:
        """Crear nuevo precio"""
        response = self._make_request('POST', '/api/v1/precios', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def update_precio(self, precio_id: int, data: Dict) -> Optional[Dict]:
        """Actualizar precio existente"""
        response = self._make_request('PUT', f'/api/v1/precios/{precio_id}', data)
        if response and not response.get('error'):
            return response.get('data') if isinstance(response, dict) else response
        return None
    
    def delete_precio(self, precio_id: int) -> bool:
        """Eliminar precio"""
        response = self._make_request('DELETE', f'/api/v1/precios/{precio_id}')
        return response and not response.get('error')
    
    # =================================================================
    # UTILIDADES
    # =================================================================
    
    def health_check(self) -> bool:
        """Verificar salud de la API"""
        response = self._make_request('GET', '/api/health')
        return response and not response.get('error')
    
    def test_connection(self) -> Dict:
        """Probar conexión y devolver estado detallado"""
        try:
            response = self._make_request('GET', '/api/health')
            if response and not response.get('error'):
                return {
                    'status': 'success',
                    'message': 'Conexión exitosa',
                    'api_url': self.base_url,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': response.get('message', 'Error desconocido') if response else 'Sin respuesta',
                    'api_url': self.base_url,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'api_url': self.base_url,
                'timestamp': datetime.now().isoformat()
            }

# Instancia global del cliente (lazy loading)
_api_client = None

def get_api_client() -> Optional[BelgranoAhorroAPIClient]:
    """
    Obtener instancia del cliente API (lazy loading)
    
    Returns:
        BelgranoAhorroAPIClient o None si hay error
    """
    global _api_client
    
    if _api_client is not None:
        return _api_client
    
    try:
        # Leer variables de entorno en tiempo de ejecución
        base_url = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
        api_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
        
        if not base_url:
            logger.warning("BELGRANO_AHORRO_URL no configurada")
            return None
        
        _api_client = BelgranoAhorroAPIClient(base_url, api_key)
        logger.info("Cliente API inicializado correctamente")
        return _api_client
        
    except Exception as e:
        logger.error(f"Error inicializando cliente API: {e}")
        return None

def reset_api_client():
    """Resetear cliente API para forzar reinicialización"""
    global _api_client
    _api_client = None
    logger.info("Cliente API reseteado")

if __name__ == "__main__":
    # Test del cliente API
    print("=== Test Cliente API Belgrano Ahorro ===")
    
    client = get_api_client()
    if client:
        print("✅ Cliente inicializado correctamente")
        
        # Test de conexión
        test_result = client.test_connection()
        print(f"🔗 Test de conexión: {test_result['status']}")
        print(f"📡 URL: {test_result['api_url']}")
        
        # Test de negocios
        negocios = client.get_negocios()
        print(f"🏢 Negocios encontrados: {len(negocios)}")
        
        # Test de productos
        productos = client.get_productos()
        print(f"📦 Productos encontrados: {len(productos)}")
        
        # Test de ofertas
        ofertas = client.get_ofertas()
        print(f"🎯 Ofertas encontradas: {len(ofertas)}")
        
    else:
        print("❌ Error inicializando cliente API")