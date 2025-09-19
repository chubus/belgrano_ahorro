#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración específica para DevOps
Variables de entorno y configuración segura
"""

import os
from werkzeug.security import generate_password_hash

class DevOpsConfig:
    """Configuración específica para DevOps"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Cargar configuración de DevOps"""
        
        # Credenciales DevOps (con valores por defecto seguros)
        self.DEVOPS_USERNAME = os.environ.get('DEVOPS_USERNAME', 'devops')
        self.DEVOPS_PASSWORD_PLAIN = os.environ.get('DEVOPS_PASSWORD', 'DevOps2025!Secure')
        
        # Generar hash seguro de la contraseña
        self.DEVOPS_PASSWORD_HASH = generate_password_hash(self.DEVOPS_PASSWORD_PLAIN)
        
        # Configuración de API
        self.BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
        self.BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        
        # Configuración de base de datos
        self.BELGRANO_AHORRO_DB_PATH = os.environ.get('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        self.TICKETS_DB_PATH = os.environ.get('TICKETS_DB_PATH', 'belgrano_tickets.db')
        
        # Configuración de sesión
        self.SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1 hora
        self.SECRET_KEY = os.environ.get('SECRET_KEY', 'devops_secret_key_2025')
        
        # Configuración de logging
        self.LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
        
        # Configuración de seguridad
        self.MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
        self.LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION', '300'))  # 5 minutos
    
    def get_credentials(self):
        """Obtener credenciales de DevOps"""
        return {
            'username': self.DEVOPS_USERNAME,
            'password_hash': self.DEVOPS_PASSWORD_HASH,
            'password_plain': self.DEVOPS_PASSWORD_PLAIN
        }
    
    def get_api_config(self):
        """Obtener configuración de API"""
        return {
            'belgrano_ahorro_url': self.BELGRANO_AHORRO_URL,
            'belgrano_ahorro_api_key': self.BELGRANO_AHORRO_API_KEY
        }
    
    def get_database_config(self):
        """Obtener configuración de base de datos"""
        return {
            'belgrano_ahorro_db': self.BELGRANO_AHORRO_DB_PATH,
            'tickets_db': self.TICKETS_DB_PATH
        }
    
    def is_production(self):
        """Verificar si está en producción"""
        return os.environ.get('FLASK_ENV', 'development') == 'production'
    
    def get_security_config(self):
        """Obtener configuración de seguridad"""
        return {
            'secret_key': self.SECRET_KEY,
            'session_timeout': self.SESSION_TIMEOUT,
            'max_login_attempts': self.MAX_LOGIN_ATTEMPTS,
            'lockout_duration': self.LOCKOUT_DURATION
        }

# Instancia global de configuración DevOps
devops_config = DevOpsConfig()

def get_devops_config():
    """Obtener instancia de configuración DevOps"""
    return devops_config

def setup_devops_environment():
    """Configurar variables de entorno para DevOps"""
    
    # Variables de entorno recomendadas para producción
    env_vars = {
        'DEVOPS_USERNAME': 'devops',
        'DEVOPS_PASSWORD': 'DevOps2025!Secure',
        'BELGRANO_AHORRO_URL': 'https://belgranoahorro-hp30.onrender.com',
        'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025',
        'BELGRANO_AHORRO_DB_PATH': 'belgrano_ahorro.db',
        'TICKETS_DB_PATH': 'belgrano_tickets.db',
        'SECRET_KEY': 'devops_secret_key_2025',
        'SESSION_TIMEOUT': '3600',
        'MAX_LOGIN_ATTEMPTS': '5',
        'LOCKOUT_DURATION': '300',
        'LOG_LEVEL': 'INFO'
    }
    
    print("🔧 Variables de entorno recomendadas para DevOps:")
    for key, value in env_vars.items():
        if 'PASSWORD' in key or 'KEY' in key:
            display_value = f"{value[:10]}..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"   {key}={display_value}")
    
    return env_vars

if __name__ == "__main__":
    print("🔧 Configuración DevOps")
    print("=" * 40)
    
    config = get_devops_config()
    
    print(f"👤 Usuario DevOps: {config.DEVOPS_USERNAME}")
    print(f"🔐 Contraseña configurada: {'Sí' if config.DEVOPS_PASSWORD_PLAIN else 'No'}")
    print(f"🌐 URL API: {config.BELGRANO_AHORRO_URL}")
    print(f"🗄️ DB Ahorro: {config.BELGRANO_AHORRO_DB_PATH}")
    print(f"🗄️ DB Tickets: {config.TICKETS_DB_PATH}")
    print(f"🔒 Entorno: {'Producción' if config.is_production() else 'Desarrollo'}")
    
    print("\n📋 Variables de entorno recomendadas:")
    setup_devops_environment()
