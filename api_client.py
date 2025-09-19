#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente API para DevOps - Re-exporta desde belgrano_tickets
"""

import sys
import os

# Agregar el directorio belgrano_tickets al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'belgrano_tickets'))

try:
    from belgrano_tickets.api_client import BelgranoAhorroAPIClient, create_api_client
    from belgrano_tickets.api_client import api_client as global_api_client
except ImportError:
    # Si no se puede importar, crear una implementación básica
    import requests
    import logging
    
    logger = logging.getLogger(__name__)
    
    class BelgranoAhorroAPIClient:
        """Cliente API básico para DevOps"""
        
        def __init__(self, base_url, api_key):
            self.base_url = base_url.rstrip('/')
            self.api_key = api_key
            self.session = requests.Session()
            self.session.headers.update({
                'Content-Type': 'application/json',
                'X-API-Key': api_key
            })
        
        def get(self, endpoint, **kwargs):
            """GET request"""
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.get(url, timeout=10, **kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error en GET {url}: {e}")
                return None
        
        def post(self, endpoint, data=None, **kwargs):
            """POST request"""
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.post(url, json=data, timeout=10, **kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error en POST {url}: {e}")
                return None
        
        def put(self, endpoint, data=None, **kwargs):
            """PUT request"""
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.put(url, json=data, timeout=10, **kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error en PUT {url}: {e}")
                return None
        
        def delete(self, endpoint, **kwargs):
            """DELETE request"""
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.delete(url, timeout=10, **kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error en DELETE {url}: {e}")
                return None
    
    def create_api_client(base_url, api_key):
        """Crear cliente API"""
        return BelgranoAhorroAPIClient(base_url, api_key)
    
    def test_api_connection(base_url, api_key):
        """
        Probar conexión con la API
        
        Args:
            base_url (str): URL base de la API
            api_key (str): Clave de API
            
        Returns:
            bool: True si la conexión es exitosa
        """
        client = BelgranoAhorroAPIClient(base_url, api_key)
        if client:
            try:
                response = client.get('/health')
                return response is not None
            except:
                return False
        return False
    
    # Cliente global por defecto
    global_api_client = None

# Exportar las funciones y clases
__all__ = ['BelgranoAhorroAPIClient', 'create_api_client', 'test_api_connection', 'global_api_client']
