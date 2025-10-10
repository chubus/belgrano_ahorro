#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración y validación de variables de entorno
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EnvConfig:
    """Configuración de variables de entorno"""
    
    def __init__(self):
        self.config = {}
        self.load_config()
        self.validate_config()
    
    def load_config(self):
        """Cargar configuración desde variables de entorno"""
        
        # Configuración de la aplicación
        self.config.update({
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'development'),
            'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'belgrano_ahorro_secret_key_2025'),
            'DATABASE_PATH': os.environ.get('DATABASE_PATH', 'belgrano_ahorro.db'),
        })
        
        # Configuración de API
        self.config.update({
            'BELGRANO_AHORRO_URL': os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com'),
            'BELGRANO_AHORRO_API_KEY': os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025'),
            'TICKETERA_URL': os.environ.get('TICKETERA_URL', 'https://ticketerabelgrano.onrender.com'),
            'TICKETERA_API_KEY': os.environ.get('TICKETERA_API_KEY', 'ticketera_api_key_2025'),
        })
        
        # Configuración de DevOps
        self.config.update({
            'DEVOPS_URL': os.environ.get('DEVOPS_URL'),
            'SYNC_ENABLED': os.environ.get('SYNC_ENABLED', 'True').lower() == 'true',
            'SYNC_TIMEOUT': int(os.environ.get('SYNC_TIMEOUT', '10')),
        })
        
        # Configuración de logging
        self.config.update({
            'LOG_LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),
            'LOG_FORMAT': os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        })
        
        # Configuración de seguridad
        self.config.update({
            'SESSION_TIMEOUT': int(os.environ.get('SESSION_TIMEOUT', '3600')),
            'MAX_LOGIN_ATTEMPTS': int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5')),
            'CORS_ORIGINS': os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000,http://localhost:5001'),
        })
    
    def validate_config(self):
        """Validar configuración crítica"""
        
        env_status = self.config['FLASK_ENV']
        warnings = []
        errors = []
        
        # Validar URLs críticas - Solo errores si realmente se necesitan
        if not self.config['BELGRANO_AHORRO_URL']:
            if env_status == 'production':
                warnings.append("BELGRANO_AHORRO_URL no está definida (usando valores por defecto)")
            else:
                warnings.append("BELGRANO_AHORRO_URL no está definida (normal en desarrollo)")
        
        if not self.config['BELGRANO_AHORRO_API_KEY']:
            if env_status == 'production':
                warnings.append("BELGRANO_AHORRO_API_KEY no está definida (usando valores por defecto)")
            else:
                warnings.append("BELGRANO_AHORRO_API_KEY no está definida (normal en desarrollo)")
        
        if not self.config['TICKETERA_URL']:
            if env_status == 'production':
                warnings.append("TICKETERA_URL no está definida (usando valores por defecto)")
            else:
                warnings.append("TICKETERA_URL no está definida (normal en desarrollo)")
        
        # Mostrar advertencias
        for warning in warnings:
            logger.warning(f"⚠️ {warning}")
        
        # Mostrar errores críticos
        for error in errors:
            logger.error(f"❌ {error}")
        
        if errors:
            raise ValueError(f"Configuración inválida: {', '.join(errors)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        return self.config.get(key, default)
    
    def get_api_config(self) -> Dict[str, Optional[str]]:
        """Obtener configuración de API"""
        return {
            'belgrano_ahorro_url': self.config['BELGRANO_AHORRO_URL'],
            'belgrano_ahorro_api_key': self.config['BELGRANO_AHORRO_API_KEY'],
            'ticketera_url': self.config['TICKETERA_URL'],
            'ticketera_api_key': self.config['TICKETERA_API_KEY'],
        }
    
    def is_production(self) -> bool:
        """Verificar si está en producción"""
        return self.config['FLASK_ENV'] == 'production'
    
    def is_development(self) -> bool:
        """Verificar si está en desarrollo"""
        return self.config['FLASK_ENV'] == 'development'
    
    def get_database_config(self) -> Dict[str, Any]:
        """Obtener configuración de base de datos"""
        return {
            'database': self.config['DATABASE_PATH'],
            'check_same_thread': False
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Obtener configuración de logging"""
        return {
            'level': self.config['LOG_LEVEL'],
            'format': self.config['LOG_FORMAT']
        }

# Instancia global de configuración
env_config = EnvConfig()

def get_config() -> EnvConfig:
    """Obtener instancia de configuración"""
    return env_config

def get_api_config() -> Dict[str, Optional[str]]:
    """Obtener configuración de API"""
    return env_config.get_api_config()

def is_production() -> bool:
    """Verificar si está en producción"""
    return env_config.is_production()

def is_development() -> bool:
    """Verificar si está en desarrollo"""
    return env_config.is_development()
