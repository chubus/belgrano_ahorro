#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor DevOps Unificado - Conecta con Belgrano Ahorro y Ticketera
Soporta operaciones CRUD, sincronización bidireccional y sincronización masiva
"""
import os
import sys
import logging
import time
from datetime import datetime
from typing import Any, Dict, Tuple, List, Optional

# Asegurar que el directorio padre esté en sys.path para imports absolutos
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Importar api_helpers con múltiples métodos
try:
    from devops.api_helpers import cached_request, clear_cache
except ImportError:
    try:
        from .api_helpers import cached_request, clear_cache
    except ImportError:
        # Fallback: import directo
        if _current_dir not in sys.path:
            sys.path.insert(0, _current_dir)
        from api_helpers import cached_request, clear_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsBelgranoManagerUnified:
    """Gestor para conexión con API de Belgrano Ahorro"""
    def __init__(self) -> None:
        # Importar configuración centralizada
        try:
            from config import (
                BELGRANO_AHORRO_URL,
                BELGRANO_AHORRO_API_KEY,
                API_TIMEOUT_SECS,
                API_RETRY_TOTAL
            )
            belgrano_url = BELGRANO_AHORRO_URL
            api_key = BELGRANO_AHORRO_API_KEY
            timeout = API_TIMEOUT_SECS
            retries = API_RETRY_TOTAL
        except ImportError:
            # Fallback si config.py no está disponible
            logger.warning("[DEVOPS] ⚠️ No se pudo importar config.py, usando os.getenv()")
            belgrano_url = os.getenv('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com').strip().rstrip('/')
            api_key = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025').strip()
            timeout = int(os.getenv('API_TIMEOUT_SECS', '60'))
            retries = int(os.getenv('API_RETRY_TOTAL', '1'))
        
        self.belgrano_url = belgrano_url.rstrip('/')
        self.api_key = api_key
        if timeout < 60:
            logger.warning(f"[DEVOPS] ⚠️ Timeout configurado ({timeout}s) es bajo. Ajustando a 60s para evitar timeouts.")
        self.timeout = max(timeout, 60)
        self.cache_ttl = int(os.getenv('API_CACHE_TTL_SECS', '120'))  # Cache por 120 segundos
        if retries != 1:
            logger.info(f"[DEVOPS] ℹ️ Ajustando retires de {retries} a 1 para evitar saturar la API.")
        self.retries = max(1, min(retries, 1))
        
        logger.info("[DEVOPS] ✅ Cliente API Belgrano Ahorro configurado")
        logger.info(f"[DEVOPS]    URL: {self.belgrano_url}")
        logger.info(f"[DEVOPS]    Timeout: {self.timeout}s")
        logger.info(f"[DEVOPS]    Cache TTL: {self.cache_ttl}s")
        logger.info(f"[DEVOPS]    Retries: {self.retries}")
        logger.info(f"[DEVOPS]    API Key: {'*' * min(len(self.api_key), 10)}... ({len(self.api_key)} caracteres)")

    def is_configured(self) -> bool:
        """Verificar si el manager está correctamente configurado"""
        # Intentar usar config.py primero
        try:
            from config import BELGRANO_AHORRO_URL, BELGRANO_AHORRO_API_KEY
            current_url = BELGRANO_AHORRO_URL
            current_api_key = BELGRANO_AHORRO_API_KEY
        except ImportError:
            # Fallback a variables de entorno
            current_url = os.getenv('BELGRANO_AHORRO_URL', '').strip().rstrip('/')
            current_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', '').strip()
        
        # Actualizar valores internos
        if current_url:
            self.belgrano_url = current_url.rstrip('/')
        if current_api_key:
            self.api_key = current_api_key
        
        # Verificar que ambas estén configuradas
        is_ok = bool(current_api_key and current_url)
        
        if not is_ok:
            logger.debug(f"[DEVOPS] ⚠️ Manager no configurado - URL: {'✅' if current_url else '❌'}, API_KEY: {'✅' if current_api_key else '❌'}")
        
        return is_ok

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    def _req(self, method: str, path: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Tuple[bool, Any]:
        """
        Realizar request usando el helper robusto cached_request
        """
        url = f"{self.belgrano_url}/{path.lstrip('/')}"
        headers = self._headers()
        
        start_time = time.time()
        if method.upper() == 'GET':
            data = cached_request(
                url,
                method='GET',
                timeout=self.timeout,
                retries=self.retries,
                cache_ttl=self.cache_ttl,
                headers=headers,
                **kwargs
            )
        else:
            data = cached_request(
                url,
                method=method.upper(),
                timeout=self.timeout,
                retries=self.retries,
                cache_ttl=0,
                headers=headers,
                json_data=json_data,
                **kwargs
            )
        elapsed = time.time() - start_time
        success = not (isinstance(data, dict) and 'error' in data)
        logger.info(f"[DEVOPS] {method.upper()} {url} respondido en {elapsed:.2f}s ({'ok' if success else 'error'})")
        
        if not success:
            error_msg = data.get('message', data.get('error', 'Error desconocido')) if isinstance(data, dict) else 'Error desconocido'
            status_code = data.get('status_code', 0) if isinstance(data, dict) else None
            logger.warning(f"[DEVOPS] ⚠️ Error en {method.upper()} {url}: {error_msg}")
            if method.upper() == 'GET':
                logger.info("[DEVOPS] ℹ️ Activando fallback vacío ([]) para mantener el panel funcionando.")
                return False, []
            return False, {'error': error_msg, 'status_code': status_code}
        
        return True, data

    def get_items(self, kind: str):
        """Obtener items con cache habilitado por defecto"""
        ok, data = self._req('GET', f"/api/{kind}")
        if ok and isinstance(data, dict):
            # Si tiene estructura de API estándar con 'data'
            if 'data' in data:
                return data['data']
            # Si es una lista directamente
            if isinstance(data, list):
                return data
        return data if ok else []

    def create_item(self, kind: str, payload: Dict[str, Any]):
        ok, data = self._req('POST', f"/api/{kind}", json_data=payload)
        # Limpiar cache del tipo de item creado para forzar refresh
        if ok:
            clear_cache(f"GET:{self.belgrano_url}/api/{kind}")
            return (True, 'ok')
        else:
            # Mejorar el manejo de errores para mostrar el mensaje correcto
            if isinstance(data, dict):
                error_msg = data.get('error', data.get('message', 'Error desconocido'))
                status_code = data.get('status_code', 0)
                if status_code:
                    error_msg = f"{error_msg} (código: {status_code})"
                return (False, error_msg)
            else:
                return (False, str(data))

    def update_item(self, kind: str, item_id: Any, payload: Dict[str, Any]):
        ok, data = self._req('PUT', f"/api/{kind}/{item_id}", json_data=payload)
        # Limpiar cache del tipo de item actualizado
        if ok:
            clear_cache(f"GET:{self.belgrano_url}/api/{kind}")
        return (True, 'ok') if ok else (False, str(data))

    def delete_item(self, kind: str, item_id: Any):
        ok, data = self._req('DELETE', f"/api/{kind}/{item_id}")
        # Limpiar cache del tipo de item eliminado
        if ok:
            clear_cache(f"GET:{self.belgrano_url}/api/{kind}")
        return (True, 'ok') if ok else (False, str(data))

    def get_productos(self):
        return self.get_items('productos')

    def get_negocios(self):
        return self.get_items('negocios')

    def get_ofertas(self):
        return self.get_items('ofertas')

    def get_sucursales(self):
        return self.get_items('sucursales')

    def create_sucursal(self, payload: Dict[str, Any]):
        return self.create_item('sucursales', payload)
    
    def get_categorias(self):
        return self.get_items('categorias')

    def test_connectivity(self) -> Dict[str, Any]:
        ok, data = self._req('GET', '/api/health')
        return {"overall_status": "success" if ok else "error", "details": data}

    def get_system_status(self) -> Dict[str, Any]:
        return {
            'timestamp': datetime.now().isoformat(),
            'fallback_mode': False,
            'api_url': self.belgrano_url,
            'api_configured': bool(self.api_key),
        }
    
    def get_item_detail(self, kind: str, item_id: Any) -> Tuple[bool, Any]:
        """Obtener un item específico por ID"""
        ok, data = self._req('GET', f"/api/{kind}/{item_id}")
        if ok and isinstance(data, dict) and 'data' in data:
            return True, data['data']
        return ok, data
    
    def get_categorias(self) -> List[Dict[str, Any]]:
        """Obtener todas las categorías"""
        return self.get_items('categorias')
    
    def get_precios(self, producto_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener precios - si se especifica producto_id, obtiene precios de ese producto"""
        if producto_id:
            ok, data = self._req('GET', f"/api/precios/{producto_id}")
            if ok and isinstance(data, dict) and 'data' in data:
                return [data['data']]
            return [data] if ok else []
        return self.get_items('precios')
    
    def update_precio(self, producto_id: int, precio_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Actualizar precio de un producto"""
        ok, data = self._req('PUT', f"/api/precios/{producto_id}", json=precio_data)
        return (True, 'ok') if ok else (False, str(data))
    
    def actualizar_negocio(self, negocio_id: int, payload: Dict[str, Any]) -> Tuple[bool, Any]:
        """Actualizar un negocio específico"""
        return self.update_item('negocios', negocio_id, payload)
    
    def actualizar_sucursal(self, sucursal_id: Any, payload: Dict[str, Any]) -> Tuple[bool, Any]:
        """Actualizar una sucursal específica"""
        return self.update_item('sucursales', sucursal_id, payload)
    
    def actualizar_producto(self, producto_id: int, payload: Dict[str, Any]) -> Tuple[bool, Any]:
        """Actualizar un producto específico"""
        return self.update_item('productos', producto_id, payload)


class DevOpsTicketeraManager:
    """Gestor para conexión con API de Ticketera"""
    def __init__(self) -> None:
        self.ticketera_url = (
            os.getenv('TICKETS_API_URL') or 
            os.getenv('TICKETERA_URL') or 
            os.getenv('DEVOPS_API_URL') or ''
        ).rstrip('/')
        self.api_key = (
            os.getenv('TICKETS_API_KEY') or 
            os.getenv('TICKETERA_API_KEY') or 
            os.getenv('DEVOPS_API_KEY') or ''
        )
        self.username = os.getenv('TICKETS_API_USERNAME', '')
        self.password = os.getenv('TICKETS_API_PASSWORD', '')
        # Importar configuración centralizada
        try:
            from config import API_TIMEOUT_SECS, API_RETRY_TOTAL, API_RETRY_BACKOFF
            timeout = API_TIMEOUT_SECS
            retries = API_RETRY_TOTAL
            backoff = API_RETRY_BACKOFF
        except ImportError:
            # Fallback si config.py no está disponible
            timeout = int(os.getenv('API_TIMEOUT_SECS', '20'))
            retries = int(os.getenv('API_RETRY_TOTAL', '3'))
            backoff = float(os.getenv('API_RETRY_BACKOFF', '1.0'))
        
        self.timeout = timeout  # 20s para producción
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff,  # 1.0s para producción
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT", "DELETE", "PATCH")
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        self._session_token = None
        logger.info("[DEVOPS] ✅ Cliente API Ticketera configurado")
        logger.info(f"[DEVOPS]    URL: {self.ticketera_url}")
        logger.info(f"[DEVOPS]    API Key: {'*' * len(self.api_key) if self.api_key else 'no-set'}")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        elif self._session_token:
            headers["Authorization"] = f"Bearer {self._session_token}"
        # Si hay username/password pero no token, intentar login
        elif self.username and self.password and not self._session_token:
            self._authenticate()
            if self._session_token:
                headers["Authorization"] = f"Bearer {self._session_token}"
        return headers

    def _authenticate(self) -> bool:
        """Autenticar con username/password si está configurado"""
        if not (self.username and self.password):
            return False
        try:
            resp = self.session.post(
                f"{self.ticketera_url}/api/login",
                json={"username": self.username, "password": self.password},
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                self._session_token = data.get('token') or data.get('access_token')
                return bool(self._session_token)
        except Exception as e:
            logger.error(f"Error autenticando con Ticketera: {e}")
        return False

    def _req(self, method: str, path: str, **kwargs) -> Tuple[bool, Any]:
        if not self.ticketera_url:
            return False, "TICKETERA_URL no configurada"
        url = f"{self.ticketera_url}/{path.lstrip('/')}"
        try:
            resp = self.session.request(method, url, headers=self._headers(), timeout=self.timeout, **kwargs)
            # Si 401, intentar re-autenticar una vez
            if resp.status_code == 401 and self.username and self.password:
                if self._authenticate():
                    resp = self.session.request(method, url, headers=self._headers(), timeout=self.timeout, **kwargs)
            try:
                data = resp.json()
            except Exception:
                data = resp.text
            return (200 <= resp.status_code < 300), data
        except requests.RequestException as e:
            logger.error(f"HTTP error {method} {url}: {e}")
            return False, str(e)

    def get_tickets(self) -> List[Dict[str, Any]]:
        """Obtener todos los tickets"""
        ok, data = self._req('GET', '/api/tickets')
        if ok and isinstance(data, dict) and 'data' in data:
            return data['data']
        return data if ok and isinstance(data, list) else []

    def get_ticket(self, ticket_id: Any) -> Tuple[bool, Any]:
        """Obtener un ticket específico"""
        ok, data = self._req('GET', f'/api/tickets/{ticket_id}')
        return ok, data

    def create_ticket(self, ticket_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Crear un nuevo ticket"""
        ok, data = self._req('POST', '/api/tickets', json=ticket_data)
        return (True, data) if ok else (False, str(data))

    def update_ticket(self, ticket_id: Any, ticket_data: Dict[str, Any]) -> Tuple[bool, Any]:
        """Actualizar un ticket"""
        ok, data = self._req('PUT', f'/api/tickets/{ticket_id}', json=ticket_data)
        return (True, data) if ok else (False, str(data))

    def delete_ticket(self, ticket_id: Any) -> Tuple[bool, Any]:
        """Eliminar un ticket"""
        ok, data = self._req('DELETE', f'/api/tickets/{ticket_id}')
        return (True, 'ok') if ok else (False, str(data))

    def test_connectivity(self) -> Dict[str, Any]:
        """Verificar conectividad con Ticketera"""
        for health_path in ['/api/health', '/health', '/status', '/api/status']:
            ok, data = self._req('GET', health_path)
            if ok:
                return {"overall_status": "success", "details": data}
        return {"overall_status": "error", "details": "No se pudo conectar"}


class DevOpsUnifiedSyncManager:
    """Gestor unificado para sincronización entre DevOps, Belgrano Ahorro y Ticketera"""
    def __init__(self):
        self.belgrano = DevOpsBelgranoManagerUnified()
        self.ticketera = DevOpsTicketeraManager()

    def sync_negocios_to_ticketera(self) -> Dict[str, Any]:
        """Sincronizar negocios de Belgrano Ahorro a Ticketera"""
        negocios = self.belgrano.get_negocios()
        results = {'success': 0, 'failed': 0, 'errors': []}
        for negocio in negocios:
            try:
                # Convertir formato de negocio a formato de ticket si es necesario
                ticket_data = {
                    'titulo': f"Negocio: {negocio.get('nombre', 'Sin nombre')}",
                    'descripcion': negocio.get('descripcion', ''),
                    'negocio_id': negocio.get('id'),
                    'estado': 'activo' if negocio.get('activo', True) else 'inactivo'
                }
                success, result = self.ticketera.create_ticket(ticket_data)
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Negocio {negocio.get('id')}: {result}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Negocio {negocio.get('id', 'unknown')}: {str(e)}")
        return results

    def sync_productos_to_ticketera(self) -> Dict[str, Any]:
        """Sincronizar productos de Belgrano Ahorro a Ticketera"""
        productos = self.belgrano.get_productos()
        results = {'success': 0, 'failed': 0, 'errors': []}
        for producto in productos:
            try:
                ticket_data = {
                    'titulo': f"Producto: {producto.get('nombre', 'Sin nombre')}",
                    'descripcion': producto.get('descripcion', ''),
                    'producto_id': producto.get('id'),
                    'precio': producto.get('precio', 0),
                    'negocio_id': producto.get('negocio_id'),
                    'estado': 'activo' if producto.get('activo', True) else 'inactivo'
                }
                success, result = self.ticketera.create_ticket(ticket_data)
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Producto {producto.get('id')}: {result}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Producto {producto.get('id', 'unknown')}: {str(e)}")
        return results

    def full_sync_all(self) -> Dict[str, Any]:
        """Sincronización completa de todos los datos"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'negocios': self.sync_negocios_to_ticketera(),
            'productos': self.sync_productos_to_ticketera(),
            'overall_status': 'success'
        }
        # Verificar si hay errores
        total_failed = results['negocios']['failed'] + results['productos']['failed']
        if total_failed > 0:
            results['overall_status'] = 'partial'
        return results

    def get_sync_status(self) -> Dict[str, Any]:
        """Obtener estado de sincronización entre sistemas"""
        belgrano_status = self.belgrano.test_connectivity()
        ticketera_status = self.ticketera.test_connectivity()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'belgrano_ahorro': {
                'connected': belgrano_status.get('overall_status') == 'success',
                'url': self.belgrano.belgrano_url,
                'details': belgrano_status
            },
            'ticketera': {
                'connected': ticketera_status.get('overall_status') == 'success',
                'url': self.ticketera.ticketera_url,
                'details': ticketera_status
            },
            'sync_ready': (
                belgrano_status.get('overall_status') == 'success' and
                ticketera_status.get('overall_status') == 'success'
            )
        }


# Instancias globales exportadas - Inicialización lazy
# Se inicializan solo cuando se acceden por primera vez
# Esto asegura que las variables de entorno estén cargadas antes de la inicialización
_devops_manager_unified = None
_devops_ticketera_manager = None
_devops_sync_manager = None

def _get_manager_unified():
    """Obtener instancia de DevOpsBelgranoManagerUnified (lazy initialization)"""
    global _devops_manager_unified
    if _devops_manager_unified is None:
        _devops_manager_unified = DevOpsBelgranoManagerUnified()
    return _devops_manager_unified

def _get_ticketera_manager():
    """Obtener instancia de DevOpsTicketeraManager (lazy initialization)"""
    global _devops_ticketera_manager
    if _devops_ticketera_manager is None:
        _devops_ticketera_manager = DevOpsTicketeraManager()
    return _devops_ticketera_manager

def _get_sync_manager():
    """Obtener instancia de DevOpsUnifiedSyncManager (lazy initialization)"""
    global _devops_sync_manager
    if _devops_sync_manager is None:
        _devops_sync_manager = DevOpsUnifiedSyncManager()
    return _devops_sync_manager

# Clase wrapper para acceso lazy a los managers
class _LazyManager:
    """Wrapper lazy para los managers - se inicializa solo cuando se accede"""
    def __init__(self, getter_func):
        self._getter = getter_func
        self._instance = None
    
    def _ensure_instance(self):
        """Asegurar que la instancia esté inicializada"""
        if self._instance is None:
            self._instance = self._getter()
        return self._instance
    
    def __getattr__(self, name):
        """Delegar todos los atributos a la instancia real"""
        return getattr(self._ensure_instance(), name)
    
    def __bool__(self):
        """Permite verificar si el manager está disponible"""
        try:
            instance = self._ensure_instance()
            return instance is not None and (hasattr(instance, 'is_configured') and instance.is_configured() if hasattr(instance, 'is_configured') else True)
        except:
            return False
    
    def __call__(self, *args, **kwargs):
        """Permite llamar al manager como función"""
        return self._ensure_instance()(*args, **kwargs)
    
    def __repr__(self):
        """Representación del wrapper"""
        try:
            instance = self._ensure_instance()
            return f"<LazyManager: {type(instance).__name__}>"
        except:
            return "<LazyManager: not initialized>"

# Exportar como atributos del módulo (se inicializan lazy cuando se acceden)
devops_manager_unified = _LazyManager(_get_manager_unified)
devops_ticketera_manager = _LazyManager(_get_ticketera_manager)
devops_sync_manager = _LazyManager(_get_sync_manager)
