# =================================================================
# CONFIGURACIÓN DE SINCRONIZACIÓN BIDIRECCIONAL
# BELGRANO AHORRO ↔ BELGRANO TICKETERA
# =================================================================

import os
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncConfig:
    """Configuración centralizada para sincronización bidireccional"""
    
    # URLs DE PRODUCCIÓN (RENDER.COM)
    BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
    BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
    
    TICKETERA_URL = os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com')
    TICKETERA_API_KEY = os.environ.get('TICKETERA_API_KEY', 'ticketera_api_key_2025')
    
    # CONFIGURACIÓN DE SINCRONIZACIÓN
    SYNC_INTERVAL_PRODUCTOS = int(os.environ.get('SYNC_INTERVAL_PRODUCTOS', 300))
    SYNC_INTERVAL_TICKETS = int(os.environ.get('SYNC_INTERVAL_TICKETS', 60))
    SYNC_INTERVAL_ESTADOS = int(os.environ.get('SYNC_INTERVAL_ESTADOS', 120))
    
    # Timeouts y reintentos
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 15))
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 5))
    RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 2))
    
    # ENDPOINTS DE SINCRONIZACIÓN
    AHORRO_ENDPOINTS = {
        'productos': '/api/v1/productos',
        'categorias': '/api/v1/categorias',
        'negocios': '/api/v1/negocios',
        'sucursales': '/api/v1/sucursales',
        'ofertas': '/api/v1/ofertas',
        'pedidos': '/api/v1/pedidos',
        'usuarios': '/api/v1/usuarios',
        'health': '/healthz',
        'sync_status': '/api/v1/sync/status'
    }
    
    TICKETERA_ENDPOINTS = {
        'tickets': '/api/tickets',
        'productos': '/api/productos',
        'repartidores': '/api/repartidores',
        'estados': '/api/estados',
        'health': '/health',
        'sync_status': '/api/sync/status'
    }
    
    def get_ahorro_headers(self):
        """Headers para autenticación con Belgrano Ahorro"""
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.BELGRANO_AHORRO_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0',
            'X-Origin': 'ticketera'
        }
    
    def get_ticketera_headers(self):
        """Headers para autenticación con Ticketera"""
        return {
            'Content-Type': 'application/json',
            'X-API-Key': self.TICKETERA_API_KEY,
            'User-Agent': 'BelgranoSync/1.0.0',
            'X-Origin': 'ahorro'
        }
    
    def validate_config(self):
        """Validar configuración completa"""
        errors = []
        
        if not self.BELGRANO_AHORRO_URL.startswith('http'):
            errors.append("BELGRANO_AHORRO_URL debe ser una URL válida")
        
        if not self.TICKETERA_URL.startswith('http'):
            errors.append("TICKETERA_URL debe ser una URL válida")
        
        if len(self.BELGRANO_AHORRO_API_KEY) < 10:
            errors.append("BELGRANO_AHORRO_API_KEY debe tener al menos 10 caracteres")
        
        if len(self.TICKETERA_API_KEY) < 10:
            errors.append("TICKETERA_API_KEY debe tener al menos 10 caracteres")
        
        return errors

# Configuración por defecto
sync_config = SyncConfig()
