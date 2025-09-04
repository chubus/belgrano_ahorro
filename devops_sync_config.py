# =================================================================
# CONFIGURACIÓN DE SINCRONIZACIÓN DEVOPS
# SISTEMA DE GESTIÓN CENTRALIZADA
# =================================================================

import os
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsSyncConfig:
    """Configuración centralizada para sincronización DevOps"""
    
    # URLs DE PRODUCCIÓN
    BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
    BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
    
    # CONFIGURACIÓN DE SINCRONIZACIÓN
    SYNC_TIMEOUT = int(os.environ.get('DEVOPS_SYNC_TIMEOUT', 10))
    SYNC_RETRY_ATTEMPTS = int(os.environ.get('DEVOPS_SYNC_RETRY_ATTEMPTS', 3))
    SYNC_RETRY_DELAY = int(os.environ.get('DEVOPS_SYNC_RETRY_DELAY', 2))
    
    # ENDPOINTS DE SINCRONIZACIÓN
    SYNC_ENDPOINTS = {
        'sucursales': '/api/v1/sucursales',
        'negocios': '/api/v1/negocios',
        'ofertas': '/api/v1/ofertas',
        'productos': '/api/v1/productos',
        'categorias': '/api/v1/categorias',
        'usuarios': '/api/v1/usuarios',
        'pedidos': '/api/v1/pedidos'
    }
    
    # CONFIGURACIÓN DE LOGGING
    LOG_LEVEL = os.environ.get('DEVOPS_LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # CONFIGURACIÓN DE SEGURIDAD
    ALLOWED_ORIGINS = ['devops', 'admin', 'system']
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('DEVOPS_RATE_LIMIT', 100))
    
    # CONFIGURACIÓN DE VALIDACIÓN
    REQUIRED_SUCURSAL_FIELDS = ['nombre', 'negocio_id', 'direccion', 'telefono']
    REQUIRED_NEGOCIO_FIELDS = ['nombre', 'descripcion', 'categoria']
    REQUIRED_OFERTA_FIELDS = ['titulo', 'descripcion', 'descuento', 'fecha_inicio', 'fecha_fin']
    
    # CONFIGURACIÓN DE METADATOS
    METADATA_FIELDS = {
        'created': 'creado_desde',
        'modified': 'modificado_desde',
        'deleted': 'eliminado_desde',
        'timestamp': 'fecha_creacion',
        'mod_timestamp': 'fecha_modificacion',
        'del_timestamp': 'fecha_eliminacion'
    }
    
    def get_sync_headers(self, origin='devops'):
        """Headers para sincronización con Belgrano Ahorro"""
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.BELGRANO_AHORRO_API_KEY,
            'X-Origin': origin,
            'X-Timestamp': datetime.now().isoformat(),
            'User-Agent': 'DevOpsSync/1.0.0'
        }
    
    def validate_sync_data(self, data_type, data):
        """Validar datos antes de sincronización"""
        if data_type == 'sucursal':
            required_fields = self.REQUIRED_SUCURSAL_FIELDS
        elif data_type == 'negocio':
            required_fields = self.REQUIRED_NEGOCIO_FIELDS
        elif data_type == 'oferta':
            required_fields = self.REQUIRED_OFERTA_FIELDS
        else:
            return False, f"Tipo de datos no válido: {data_type}"
        
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return False, f"Campos requeridos faltantes: {', '.join(missing_fields)}"
        
        return True, "Datos válidos"
    
    def add_sync_metadata(self, data, operation='create', origin='devops'):
        """Agregar metadatos de sincronización"""
        timestamp = datetime.now().isoformat()
        
        if operation == 'create':
            data[self.METADATA_FIELDS['created']] = origin
            data[self.METADATA_FIELDS['timestamp']] = timestamp
            data['activo'] = True
        elif operation == 'update':
            data[self.METADATA_FIELDS['modified']] = origin
            data[self.METADATA_FIELDS['mod_timestamp']] = timestamp
        elif operation == 'delete':
            data[self.METADATA_FIELDS['deleted']] = origin
            data[self.METADATA_FIELDS['del_timestamp']] = timestamp
        
        return data
    
    def get_sync_status(self):
        """Obtener estado de configuración de sincronización"""
        return {
            'config_version': '1.0.0',
            'belgrano_ahorro_url': self.BELGRANO_AHORRO_URL,
            'sync_timeout': self.SYNC_TIMEOUT,
            'retry_attempts': self.SYNC_RETRY_ATTEMPTS,
            'rate_limit': self.RATE_LIMIT_PER_MINUTE,
            'endpoints_configured': len(self.SYNC_ENDPOINTS),
            'last_config_check': datetime.now().isoformat()
        }

# Configuración por defecto
devops_sync_config = DevOpsSyncConfig()
