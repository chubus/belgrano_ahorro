#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURACIÓN DE DEPLOY - BELGRANO AHORRO Y TICKETS
Configuración centralizada para deploy en producción
"""

import os
from datetime import datetime

class DeployConfig:
    """Configuración centralizada para deploy"""
    
    # Información básica
    APP_VERSION = "1.0.0"
    PYTHON_VERSION = "3.12.0"
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'production')
    
    # Belgrano Ahorro
    AHORRO_SECRET_KEY = os.environ.get('AHORRO_SECRET_KEY', 'belgrano_ahorro_secret_key_2025')
    AHORRO_PORT = int(os.environ.get('AHORRO_PORT', '5000'))
    AHORRO_HOST = os.environ.get('AHORRO_HOST', '0.0.0.0')
    AHORRO_DB_PATH = os.environ.get('AHORRO_DB_PATH', 'belgrano_ahorro.db')
    AHORRO_URL = os.environ.get('AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
    
    # Belgrano Tickets
    TICKETS_SECRET_KEY = os.environ.get('TICKETS_SECRET_KEY', 'belgrano_tickets_secret_key_2025')
    TICKETS_PORT = int(os.environ.get('TICKETS_PORT', '5001'))
    TICKETS_HOST = os.environ.get('TICKETS_HOST', '0.0.0.0')
    TICKETS_DB_PATH = os.environ.get('TICKETS_DB_PATH', 'belgrano_tickets.db')
    TICKETS_URL = os.environ.get('TICKETS_URL', 'https://belgranoahorro-hp30.onrender.com')
    
    # Integración
    TICKETERA_URL = os.environ.get('TICKETERA_URL', 'https://belgranoahorro-hp30.onrender.com')
    BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-hp30.onrender.com')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', '30'))
    API_RETRY_ATTEMPTS = int(os.environ.get('API_RETRY_ATTEMPTS', '3'))
    
    # Seguridad
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    LOGIN_TIMEOUT = int(os.environ.get('LOGIN_TIMEOUT', '300'))
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))
    
    # Logging y monitoreo
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', '60'))
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'true').lower() == 'true'
    
    # Backup
    AUTO_BACKUP = os.environ.get('AUTO_BACKUP', 'true').lower() == 'true'
    BACKUP_INTERVAL = int(os.environ.get('BACKUP_INTERVAL', '3600'))

def configure_deploy():
    """Configurar variables de entorno para deploy"""
    print("🔧 CONFIGURANDO DEPLOY...")
    print("=" * 40)
    
    # Variables esenciales
    essential_vars = {
        'FLASK_ENV': 'production',
        'SECRET_KEY': 'belgrano_ahorro_secret_key_2025',
        'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025',
        'TICKETERA_API_KEY': 'ticketera_api_key_2025'
    }
    
    for var, default_value in essential_vars.items():
        if not os.environ.get(var):
            os.environ[var] = default_value
            print(f"⚠️ {var}: {default_value} (por defecto)")
        else:
            print(f"✅ {var}: {os.environ[var]}")
    
    print("\n✅ CONFIGURACIÓN DE DEPLOY COMPLETADA")
    return True

if __name__ == "__main__":
    configure_deploy()