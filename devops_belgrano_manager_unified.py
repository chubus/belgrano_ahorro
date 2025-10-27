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
        self.fallback_mode = False  # FORZAR SOLO DATOS REALES
        
        # Cache de autenticación
        self._auth_token = None
        self._token_expiry = None
        
        # if self.fallback_mode: # ELIMINADO - SOLO DATOS REALES
        logger.info("✅ Cliente API configurado para SOLO datos reales")
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
            'Authorization': f'Bearer {self.belgrano_api_key}'  # Usar API key directamente como Bearer token
        }
        
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """Construir URL completa para endpoint"""
        if not self.belgrano_url:
            raise ValueError("BELGRANO_AHORRO_URL no configurada")
        
        # Mapear endpoints a las rutas correctas de Belgrano Ahorro
        endpoint_mapping = {
            'productos': '/api/v1/productos',
            'sucursales': '/api/v1/sucursales', 
            'negocios': '/api/v1/negocios',
            'ofertas': '/api/v1/ofertas',
            'precios': '/api/v1/precios',
            'tickets': '/api/tickets',
            'health': '/api/health'
        }
        
        # Normalizar endpoint (remover / inicial si existe)
        clean_endpoint = endpoint.lstrip('/')
        mapped_endpoint = endpoint_mapping.get(clean_endpoint, endpoint)
        return urljoin(self.belgrano_url, mapped_endpoint)
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[bool, Any]:
        """Realizar request a la API con manejo de errores unificado"""
        if self.fallback_mode:
            return False, "API no disponible - Configurar variables de entorno"
        
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
            ('/api/health', 'Health Check'),
            ('/api/v1/negocios', 'Negocios'),
            ('/api/v1/productos', 'Productos'),
            ('/api/v1/sucursales', 'Sucursales'),
            ('/api/v1/ofertas', 'Ofertas'),
            ('/api/tickets', 'Tickets')
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
        """Obtener items por tipo desde API real de Belgrano Ahorro."""
        try:
            if self.fallback_mode:
                logger.error(f"❌ API no configurada para {kind} - Configurar BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY")
                # return [] # ELIMINADO - SOLO DATOS REALES
            
            success, data = self._make_request('GET', kind)
            if success and isinstance(data, list):
                logger.info(f"✅ {kind} obtenidos desde API real: {len(data)} items")
                return data
            elif success and isinstance(data, dict) and 'data' in data:
                # Manejar respuesta con estructura {data: [...]}
                items = data.get('data', [])
                logger.info(f"✅ {kind} obtenidos desde API real: {len(items)} items")
                return items
            else:
                logger.warning(f"⚠️ No se pudo obtener {kind} desde API: {data}")
                # return [] # ELIMINADO - SOLO DATOS REALES
        except Exception as e:
            logger.error(f"❌ Error obteniendo {kind}: {e}")
            # return [] # ELIMINADO - SOLO DATOS REALES
    
    def create_item(self, kind: str, data: Dict) -> Tuple[bool, str]:
        """Crear item en API real de Belgrano Ahorro."""
        try:
            if self.fallback_mode:
                logger.error(f"❌ API no configurada para {kind} - Configurar BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY")
                return False, "API no disponible - Configurar variables de entorno"
            
            success, response = self._make_request('POST', kind, data)
            if success:
                item_name = data.get('nombre', data.get('titulo', 'Sin nombre'))
                logger.info(f"✅ {kind} creado en API real: {item_name}")
                return True, f"{kind.title()} creado exitosamente en Belgrano Ahorro"
            logger.warning(f"⚠️ No se pudo crear {kind} en API: {response}")
            return False, f"Error al crear {kind} en API: {response}"
        except Exception as e:
            logger.error(f"❌ Error creando {kind}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def update_item(self, kind: str, item_id: Any, data: Dict) -> Tuple[bool, str]:
        """Actualizar item en API real de Belgrano Ahorro."""
        try:
            if self.fallback_mode:
                logger.error(f"❌ API no configurada para {kind} - Configurar BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY")
                return False, "API no disponible - Configurar variables de entorno"
            
            success, response = self._make_request('PUT', f'{kind}/{item_id}', data)
            if success:
                logger.info(f"✅ {kind} actualizado en API real: ID {item_id}")
                return True, f"{kind.title()} actualizado exitosamente en Belgrano Ahorro"
            logger.warning(f"⚠️ No se pudo actualizar {kind} en API: {response}")
            return False, f"Error al actualizar {kind} en API: {response}"
        except Exception as e:
            logger.error(f"❌ Error actualizando {kind}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def delete_item(self, kind: str, item_id: Any) -> Tuple[bool, str]:
        """Eliminar item en API real de Belgrano Ahorro."""
        try:
            if self.fallback_mode:
                logger.warning("⚠️ Modo fallback activado - API no configurada")
                return False, "API no disponible - Configurar variables de entorno"
            success, response = self._make_request('DELETE', f'{kind}/{item_id}')
            if success:
                logger.info(f"✅ {kind} eliminado en API real: ID {item_id}")
                return True, f"{kind.title()} eliminado exitosamente en Belgrano Ahorro"
            logger.warning(f"⚠️ No se pudo eliminar {kind} en API: {response}")
            return False, f"Error al eliminar {kind} en API: {response}"
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
    # DATOS DE FALLBACK ELIMINADOS - SOLO DATOS REALES
    # =================================================================
    # Función _get_local_data eliminada - Solo datos reales desde API

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
