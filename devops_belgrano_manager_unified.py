#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor DevOps Unificado para Belgrano Ahorro
Módulo de gestión segura con conectividad API, autenticación JWT y fallback local
"""

import os
import json
import requests
import logging
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsBelgranoManagerUnified:
    """Gestor DevOps unificado con conectividad API, autenticación JWT y fallback local"""
    
    def __init__(self):
        """Inicializar el gestor DevOps unificado"""
        self.belgrano_url = os.environ.get('BELGRANO_AHORRO_URL', 'http://localhost:5000')
        self.belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
        self.api_timeout = int(os.environ.get('API_TIMEOUT_SECS', '30'))
        self.jwt_secret = os.environ.get('JWT_SECRET', 'devops_jwt_secret_2025')
        self.fallback_mode = not (self.belgrano_url and self.belgrano_api_key)
        
        # Cache de autenticación
        self._auth_token = None
        self._token_expiry = None
        
        if self.fallback_mode:
            logger.warning("⚠️ Modo fallback activado - Variables de entorno no configuradas")
        else:
            logger.info("✅ Cliente API configurado correctamente")
            logger.info(f"   URL: {self.belgrano_url}")
            logger.info(f"   API Key: {'*' * len(self.belgrano_api_key)}")
    
    def _get_auth_token(self) -> Optional[str]:
        """Obtener token de autenticación simple"""
        if self._auth_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._auth_token
        
        try:
            # Generar token simple (sin JWT)
            timestamp = str(int(datetime.now().timestamp()))
            token_data = f"devops_{timestamp}_{self.belgrano_api_key}"
            token = base64.b64encode(token_data.encode()).decode()
            
            self._auth_token = token
            self._token_expiry = datetime.now() + timedelta(hours=1)
            
            logger.info("✅ Token de autenticación generado exitosamente")
            return token
            
        except Exception as e:
            logger.error(f"❌ Error generando token: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtener headers para requests API"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DevOps-Belgrano-Manager/3.0',
            'X-API-Key': self.belgrano_api_key
        }
        
        # Agregar token JWT si está disponible
        token = self._get_auth_token()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """Construir URL completa para endpoint"""
        if not self.belgrano_url:
            raise ValueError("BELGRANO_AHORRO_URL no configurada")
        
        # Normalizar endpoint
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'
        
        # Mapear endpoints a las rutas correctas
        endpoint_mapping = {
            '/v1/productos': '/api/v1/productos',
            '/v1/sucursales': '/api/v1/sucursales', 
            '/v1/negocios': '/api/v1/negocios',
            '/v1/ofertas': '/api/v1/ofertas',
            '/v1/precios': '/api/v1/precios',
            '/tickets': '/api/tickets',
            '/health': '/healthz'
        }
        
        mapped_endpoint = endpoint_mapping.get(endpoint, endpoint)
        return urljoin(self.belgrano_url, mapped_endpoint)
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[bool, Any]:
        """Realizar request a la API con manejo de errores unificado"""
        if self.fallback_mode:
            return False, "API no disponible (modo fallback)"
        
        try:
            url = self._build_url(endpoint)
            headers = self._get_headers()
            
            logger.info(f"🌐 {method} {url}")
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=self.api_timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=self.api_timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=self.api_timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.api_timeout)
            else:
                return False, f"Método HTTP no soportado: {method}"
            
            # Manejo unificado de respuestas
            if response.status_code == 200:
                return True, response.json()
            elif response.status_code == 201:
                return True, response.json()
            elif response.status_code == 302:
                return False, "Redirigido a login (302) - Revisar autenticación"
            elif response.status_code == 401:
                return False, "No autorizado (401) - Token inválido o expirado"
            elif response.status_code == 404:
                return False, f"Endpoint no encontrado (404): {endpoint}"
            elif response.status_code == 500:
                return False, f"Error interno del servidor (500): {response.text}"
            else:
                return False, f"Error HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout de conexión"
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión - Servicio no disponible"
        except requests.exceptions.RequestException as e:
            return False, f"Error de request: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def test_connectivity(self) -> Dict[str, Any]:
        """Probar conectividad con todos los endpoints"""
        logger.info("🔍 Probando conectividad con Belgrano Ahorro...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.belgrano_url,
            'overall_status': 'unknown',
            'endpoints': {},
            'errors': []
        }
        
        # Endpoints a probar
        endpoints_to_test = [
            ('/health', 'Health Check'),
            ('/v1/negocios', 'Negocios'),
            ('/v1/productos', 'Productos'),
            ('/v1/sucursales', 'Sucursales'),
            ('/v1/ofertas', 'Ofertas'),
            ('/tickets', 'Tickets')
        ]
        
        successful_endpoints = 0
        
        for endpoint, name in endpoints_to_test:
            try:
                success, response = self._make_request('GET', endpoint)
                
                if success:
                    results['endpoints'][endpoint] = {
                        'status': 'success',
                        'response': response,
                        'name': name
                    }
                    successful_endpoints += 1
                    logger.info(f"✅ {name}: OK")
                else:
                    results['endpoints'][endpoint] = {
                        'status': 'error',
                        'error': response,
                        'name': name
                    }
                    results['errors'].append(f"{name}: {response}")
                    logger.warning(f"❌ {name}: {response}")
                    
            except Exception as e:
                results['endpoints'][endpoint] = {
                    'status': 'error',
                    'error': str(e),
                    'name': name
                }
                results['errors'].append(f"{name}: {str(e)}")
                logger.error(f"❌ {name}: {str(e)}")
        
        # Determinar estado general
        total_endpoints = len(endpoints_to_test)
        if successful_endpoints == total_endpoints:
            results['overall_status'] = 'success'
        elif successful_endpoints > 0:
            results['overall_status'] = 'partial'
        else:
            results['overall_status'] = 'error'
        
        results['success_rate'] = f"{successful_endpoints}/{total_endpoints}"
        
        logger.info(f"📊 Conectividad: {results['overall_status']} ({results['success_rate']})")
        
        return results
    
    # =================================================================
    # OPERACIONES CRUD GENÉRICAS
    # =================================================================
    
    def get_items(self, kind: str) -> List[Dict]:
        """Obtener items por tipo exclusivamente desde API (sin datos simulados)."""
        try:
            success, data = self._make_request('GET', f'v1/{kind}')
            if success and isinstance(data, list):
                logger.info(f"✅ {kind} obtenidos desde API: {len(data)} items")
                return data
            logger.warning(f"⚠️ No se pudo obtener {kind} desde API: {data}")
            return []
        except Exception as e:
            logger.error(f"❌ Error obteniendo {kind}: {e}")
            return []
    
    def create_item(self, kind: str, data: Dict) -> Tuple[bool, str]:
        """Crear item exclusivamente en API (sin creación local)."""
        try:
            if self.fallback_mode:
                logger.warning("⚠️ Modo fallback activado - API no configurada")
                return False, "API no disponible (modo fallback)"
            success, response = self._make_request('POST', f'v1/{kind}', data)
            if success:
                logger.info(f"✅ {kind} creado en API: {data.get('nombre', 'Sin nombre')}")
                return True, "Item creado exitosamente en API"
            logger.warning(f"⚠️ No se pudo crear {kind} en API: {response}")
            return False, f"Error al crear item en API: {response}"
        except Exception as e:
            logger.error(f"❌ Error creando {kind}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def update_item(self, kind: str, item_id: Any, data: Dict) -> Tuple[bool, str]:
        """Actualizar item exclusivamente en API (sin actualización local)."""
        try:
            if self.fallback_mode:
                logger.warning("⚠️ Modo fallback activado - API no configurada")
                return False, "API no disponible (modo fallback)"
            success, response = self._make_request('PUT', f'v1/{kind}/{item_id}', data)
            if success:
                logger.info(f"✅ {kind} actualizado en API: ID {item_id}")
                return True, "Item actualizado exitosamente en API"
            logger.warning(f"⚠️ No se pudo actualizar {kind} en API: {response}")
            return False, f"Error al actualizar item en API: {response}"
        except Exception as e:
            logger.error(f"❌ Error actualizando {kind}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def delete_item(self, kind: str, item_id: Any) -> Tuple[bool, str]:
        """Eliminar item exclusivamente en API (sin eliminación local)."""
        try:
            if self.fallback_mode:
                logger.warning("⚠️ Modo fallback activado - API no configurada")
                return False, "API no disponible (modo fallback)"
            success, response = self._make_request('DELETE', f'v1/{kind}/{item_id}')
            if success:
                logger.info(f"✅ {kind} eliminado en API: ID {item_id}")
                return True, "Item eliminado exitosamente en API"
            logger.warning(f"⚠️ No se pudo eliminar {kind} en API: {response}")
            return False, f"Error al eliminar item en API: {response}"
        except Exception as e:
            logger.error(f"❌ Error eliminando {kind}: {e}")
            return False, f"Error interno: {str(e)}"
    
    # =================================================================
    # OPERACIONES ESPECÍFICAS
    # =================================================================
    
    def get_productos(self) -> List[Dict]:
        """Obtener productos"""
        return self.get_items('productos')
    
    def get_negocios(self) -> List[Dict]:
        """Obtener negocios"""
        return self.get_items('negocios')
    
    def get_ofertas(self) -> List[Dict]:
        """Obtener ofertas"""
        return self.get_items('ofertas')
    
    def get_sucursales(self) -> List[Dict]:
        """Obtener sucursales"""
        return self.get_items('sucursales')
    
    def get_precios(self) -> List[Dict]:
        """Obtener precios"""
        return self.get_items('precios')
    
    def create_producto(self, data: Dict) -> Tuple[bool, str]:
        """Crear producto"""
        return self.create_item('productos', data)
    
    def create_negocio(self, data: Dict) -> Tuple[bool, str]:
        """Crear negocio"""
        return self.create_item('negocios', data)
    
    def create_oferta(self, data: Dict) -> Tuple[bool, str]:
        """Crear oferta"""
        return self.create_item('ofertas', data)
    
    def create_sucursal(self, data: Dict) -> Tuple[bool, str]:
        """Crear sucursal"""
        return self.create_item('sucursales', data)
    
    def update_producto(self, producto_id: Any, data: Dict) -> Tuple[bool, str]:
        """Actualizar producto"""
        return self.update_item('productos', producto_id, data)
    
    def update_negocio(self, negocio_id: Any, data: Dict) -> Tuple[bool, str]:
        """Actualizar negocio"""
        return self.update_item('negocios', negocio_id, data)
    
    def update_oferta(self, oferta_id: Any, data: Dict) -> Tuple[bool, str]:
        """Actualizar oferta"""
        return self.update_item('ofertas', oferta_id, data)
    
    def update_sucursal(self, sucursal_id: Any, data: Dict) -> Tuple[bool, str]:
        """Actualizar sucursal"""
        return self.update_item('sucursales', sucursal_id, data)
    
    def delete_producto(self, producto_id: Any) -> Tuple[bool, str]:
        """Eliminar producto"""
        return self.delete_item('productos', producto_id)
    
    def delete_negocio(self, negocio_id: Any) -> Tuple[bool, str]:
        """Eliminar negocio"""
        return self.delete_item('negocios', negocio_id)
    
    def delete_oferta(self, oferta_id: Any) -> Tuple[bool, str]:
        """Eliminar oferta"""
        return self.delete_item('ofertas', oferta_id)
    
    def delete_sucursal(self, sucursal_id: Any) -> Tuple[bool, str]:
        """Eliminar sucursal"""
        return self.delete_item('sucursales', sucursal_id)
    
    # =================================================================
    # DATOS DE FALLBACK
    # =================================================================
    
    def _get_fallback_data(self, data_type: str) -> List[Dict]:
        """Obtener datos de fallback local"""
        fallback_data = {
            'productos': [
                {
                    'id': 1,
                    'nombre': 'Leche Entera 1L',
                    'descripcion': 'Leche fresca pasteurizada',
                    'precio': 850.00,
                    'categoria_id': 1,
                    'negocio_id': 1,
                    'activo': True
                },
                {
                    'id': 2,
                    'nombre': 'Pan Integral',
                    'descripcion': 'Pan de trigo integral fresco',
                    'precio': 450.00,
                    'categoria_id': 2,
                    'negocio_id': 1,
                    'activo': True
                }
            ],
            'negocios': [
                {
                    'id': 1,
                    'nombre': 'Supermercado Central',
                    'descripcion': 'Supermercado con productos frescos',
                    'direccion': 'Av. Belgrano 1234',
                    'telefono': '+54 11 1234-5678',
                    'email': 'info@supercentral.com',
                    'activo': True
                },
                {
                    'id': 2,
                    'nombre': 'Farmacia San Martín',
                    'descripcion': 'Farmacia con medicamentos',
                    'direccion': 'Calle San Martín 567',
                    'telefono': '+54 11 9876-5432',
                    'email': 'contacto@farmaciasanmartin.com',
                    'activo': True
                }
            ],
            'ofertas': [
                {
                    'id': 1,
                    'titulo': 'Oferta Especial 50%',
                    'descripcion': 'Descuento del 50% en productos seleccionados',
                    'descuento': 50,
                    'fecha_inicio': '2025-01-19',
                    'fecha_fin': '2025-01-31',
                    'activa': True,
                    'negocio_id': 1
                }
            ],
            'sucursales': [
                {
                    'id': 1,
                    'nombre': 'Sucursal Centro',
                    'direccion': 'Av. Corrientes 1234',
                    'telefono': '+54 11 1111-1111',
                    'negocio_id': 1,
                    'activo': True
                }
            ],
            'precios': [
                {
                    'id': 1,
                    'producto_id': 1,
                    'producto_nombre': 'Leche Entera 1L',
                    'precio_actual': 850.00,
                    'precio_anterior': 800.00,
                    'negocio_nombre': 'Supermercado Central',
                    'fecha_actualizacion': '2025-01-19T10:30:00',
                    'motivo': 'Ajuste de precios'
                }
            ]
        }
        
        return fallback_data.get(data_type, [])
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            'timestamp': datetime.now().isoformat(),
            'fallback_mode': self.fallback_mode,
            'api_url': self.belgrano_url,
            'api_configured': bool(self.belgrano_api_key),
            'connectivity': self.test_connectivity()
        }

# Instancia global del gestor unificado
devops_manager_unified = DevOpsBelgranoManagerUnified()
