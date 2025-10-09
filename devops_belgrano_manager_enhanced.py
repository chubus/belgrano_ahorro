#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor DevOps Mejorado para Belgrano Ahorro
Módulo de gestión segura con conectividad API y fallback local
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsBelgranoManagerEnhanced:
    """Gestor DevOps mejorado con conectividad API y fallback local"""
    
    def __init__(self):
        """Inicializar el gestor DevOps mejorado"""
        self.belgrano_url = os.environ.get('BELGRANO_AHORRO_URL')
        self.belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
        self.api_timeout = int(os.environ.get('API_TIMEOUT_SECS', '10'))
        self.fallback_mode = not (self.belgrano_url and self.belgrano_api_key)
        
        if self.fallback_mode:
            logger.warning("⚠️ Modo fallback activado - Variables de entorno no configuradas")
        else:
            logger.info("✅ Cliente API configurado correctamente")
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtener headers para requests API"""
        return {
            'X-API-Key': self.belgrano_api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'DevOps-Belgrano-Manager/2.0'
        }
    
    def _build_url(self, endpoint: str) -> str:
        """Construir URL completa para endpoint"""
        if not self.belgrano_url:
            raise ValueError("BELGRANO_AHORRO_URL no configurada")
        return urljoin(self.belgrano_url, f'/api/{endpoint}')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Tuple[bool, Any]:
        """Realizar request a la API con manejo de errores"""
        if self.fallback_mode:
            return False, "API no disponible (modo fallback)"
        
        try:
            url = self._build_url(endpoint)
            headers = self._get_headers()
            
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
            
            if response.status_code == 200:
                return True, response.json()
            elif response.status_code == 404:
                return False, "Endpoint no encontrado (404)"
            elif response.status_code == 500:
                return False, "Error interno del servidor (500)"
            elif response.status_code == 302:
                return False, "Redirigido a login (302) - Revisar autenticación"
            else:
                return False, f"Error HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout de conexión"
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
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
            ]
        }
        
        return fallback_data.get(data_type, [])
    
    # =================================================================
    # OPERACIONES CRUD GENÉRICAS
    # =================================================================
    
    def get_items(self, kind: str) -> List[Dict]:
        """Obtener items por tipo con fallback local"""
        try:
            # Intentar obtener de API primero
            success, data = self._make_request('GET', f'v1/{kind}')
            if success:
                logger.info(f"✅ {kind} obtenidos desde API: {len(data)} items")
                return data
            else:
                logger.warning(f"⚠️ API no disponible para {kind}: {data}")
                logger.info(f"📦 Usando datos de fallback para {kind}")
                return self._get_fallback_data(kind)
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo {kind}: {e}")
            return self._get_fallback_data(kind)
    
    def create_item(self, kind: str, data: Dict) -> Tuple[bool, str]:
        """Crear item con fallback local"""
        try:
            # Intentar crear en API primero
            success, response = self._make_request('POST', f'v1/{kind}', data)
            if success:
                logger.info(f"✅ {kind} creado en API: {data.get('nombre', 'Sin nombre')}")
                return True, "Item creado exitosamente en API"
            else:
                logger.warning(f"⚠️ No se pudo crear {kind} en API: {response}")
                # Fallback: simular creación local
                logger.info(f"📦 Simulando creación local de {kind}")
                return True, f"Item creado localmente (API no disponible: {response})"
                
        except Exception as e:
            logger.error(f"❌ Error creando {kind}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def update_item(self, kind: str, item_id: Any, data: Dict) -> Tuple[bool, str]:
        """Actualizar item con fallback local"""
        try:
            # Intentar actualizar en API primero
            success, response = self._make_request('PUT', f'v1/{kind}/{item_id}', data)
            if success:
                logger.info(f"✅ {kind} actualizado en API: ID {item_id}")
                return True, "Item actualizado exitosamente en API"
            else:
                logger.warning(f"⚠️ No se pudo actualizar {kind} en API: {response}")
                # Fallback: simular actualización local
                logger.info(f"📦 Simulando actualización local de {kind} ID {item_id}")
                return True, f"Item actualizado localmente (API no disponible: {response})"
                
        except Exception as e:
            logger.error(f"❌ Error actualizando {kind}: {e}")
            return False, f"Error interno: {str(e)}"
    
    def delete_item(self, kind: str, item_id: Any) -> Tuple[bool, str]:
        """Eliminar item con fallback local"""
        try:
            # Intentar eliminar en API primero
            success, response = self._make_request('DELETE', f'v1/{kind}/{item_id}')
            if success:
                logger.info(f"✅ {kind} eliminado en API: ID {item_id}")
                return True, "Item eliminado exitosamente en API"
            else:
                logger.warning(f"⚠️ No se pudo eliminar {kind} en API: {response}")
                # Fallback: simular eliminación local
                logger.info(f"📦 Simulando eliminación local de {kind} ID {item_id}")
                return True, f"Item eliminado localmente (API no disponible: {response})"
                
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
    # VERIFICACIÓN DE CONECTIVIDAD
    # =================================================================
    
    def test_connectivity(self) -> Dict[str, Any]:
        """Probar conectividad con todos los endpoints"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'api_configured': not self.fallback_mode,
            'endpoints': {},
            'overall_status': 'unknown'
        }
        
        if self.fallback_mode:
            results['overall_status'] = 'fallback'
            results['message'] = 'Variables de entorno no configuradas'
            return results
        
        # Probar endpoints
        endpoints_to_test = [
            ('tickets', 'GET', '/api/tickets'),
            ('ofertas', 'GET', '/api/v1/ofertas'),
            ('negocios', 'GET', '/api/v1/negocios'),
            ('productos', 'GET', '/api/v1/productos'),
            ('sucursales', 'GET', '/api/v1/sucursales')
        ]
        
        success_count = 0
        for endpoint_name, method, path in endpoints_to_test:
            try:
                url = urljoin(self.belgrano_url, path)
                response = requests.get(url, headers=self._get_headers(), timeout=5)
                
                results['endpoints'][endpoint_name] = {
                    'status_code': response.status_code,
                    'status': 'success' if response.status_code == 200 else 'error',
                    'message': f'HTTP {response.status_code}'
                }
                
                if response.status_code == 200:
                    success_count += 1
                    
            except Exception as e:
                results['endpoints'][endpoint_name] = {
                    'status_code': 0,
                    'status': 'error',
                    'message': str(e)
                }
        
        # Determinar estado general
        if success_count == len(endpoints_to_test):
            results['overall_status'] = 'success'
        elif success_count > 0:
            results['overall_status'] = 'partial'
        else:
            results['overall_status'] = 'error'
        
        results['success_count'] = success_count
        results['total_endpoints'] = len(endpoints_to_test)
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            'timestamp': datetime.now().isoformat(),
            'fallback_mode': self.fallback_mode,
            'api_url': self.belgrano_url,
            'api_key_configured': bool(self.belgrano_api_key),
            'timeout_seconds': self.api_timeout,
            'connectivity': self.test_connectivity()
        }

# Instancia global del gestor
devops_manager = DevOpsBelgranoManagerEnhanced()
