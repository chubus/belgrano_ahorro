#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente API para comunicación con Belgrano Ahorro
Usado por DevOps para gestionar datos
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
    """Cliente para comunicación con la API de Belgrano Ahorro"""
    
    def __init__(self):
        self.base_url = os.getenv('BELGRANO_AHORRO_URL', 'http://localhost:5000')
        self.api_key = os.getenv('BELGRANO_AHORRO_API_KEY', 'dev_api_key_123')
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
    
    # === PRODUCTOS ===
    def get_products(self) -> Dict:
        """Obtener todos los productos"""
        return self._make_request('GET', 'products')
    
    def get_product(self, product_id: int) -> Dict:
        """Obtener producto específico"""
        return self._make_request('GET', f'products/{product_id}')
    
    def create_product(self, product_data: Dict) -> Dict:
        """Crear nuevo producto"""
        return self._make_request('POST', 'products', data=product_data)
    
    def update_product(self, product_id: int, product_data: Dict) -> Dict:
        """Actualizar producto"""
        return self._make_request('PUT', f'products/{product_id}', data=product_data)
    
    def delete_product(self, product_id: int) -> Dict:
        """Eliminar producto"""
        return self._make_request('DELETE', f'products/{product_id}')
    
    # === NEGOCIOS ===
    def get_businesses(self) -> Dict:
        """Obtener todos los negocios"""
        return self._make_request('GET', 'businesses')
    
    def create_business(self, business_data: Dict) -> Dict:
        """Crear nuevo negocio"""
        return self._make_request('POST', 'businesses', data=business_data)
    
    def update_business(self, business_id: int, business_data: Dict) -> Dict:
        """Actualizar negocio"""
        return self._make_request('PUT', f'businesses/{business_id}', data=business_data)
    
    def delete_business(self, business_id: int) -> Dict:
        """Eliminar negocio"""
        return self._make_request('DELETE', f'businesses/{business_id}')
    
    # === SUCURSALES ===
    def get_branches(self) -> Dict:
        """Obtener todas las sucursales"""
        return self._make_request('GET', 'branches')
    
    def create_branch(self, branch_data: Dict) -> Dict:
        """Crear nueva sucursal"""
        return self._make_request('POST', 'branches', data=branch_data)
    
    def update_branch(self, branch_id: int, branch_data: Dict) -> Dict:
        """Actualizar sucursal"""
        return self._make_request('PUT', f'branches/{branch_id}', data=branch_data)
    
    def delete_branch(self, branch_id: int) -> Dict:
        """Eliminar sucursal"""
        return self._make_request('DELETE', f'branches/{branch_id}')
    
    # === OFERTAS ===
    def get_offers(self) -> Dict:
        """Obtener todas las ofertas"""
        return self._make_request('GET', 'offers')
    
    def create_offer(self, offer_data: Dict) -> Dict:
        """Crear nueva oferta"""
        return self._make_request('POST', 'offers', data=offer_data)
    
    def update_offer(self, offer_id: int, offer_data: Dict) -> Dict:
        """Actualizar oferta"""
        return self._make_request('PUT', f'offers/{offer_id}', data=offer_data)
    
    def delete_offer(self, offer_id: int) -> Dict:
        """Eliminar oferta"""
        return self._make_request('DELETE', f'offers/{offer_id}')
    
    # === CARRITO ===
    def get_cart(self) -> Dict:
        """Obtener carrito"""
        return self._make_request('GET', 'cart')
    
    def confirm_cart(self, cart_data: Dict) -> Dict:
        """Confirmar carrito"""
        return self._make_request('POST', 'cart', data=cart_data)
    
    # === HEALTH CHECK ===
    def health_check(self) -> Dict:
        """Verificar estado de la API"""
        return self._make_request('GET', 'health')

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

if __name__ == "__main__":
    # Probar conexión
    if test_connection():
        print("✅ Belgrano Ahorro API connection successful")
    else:
        print("❌ Belgrano Ahorro API connection failed")
