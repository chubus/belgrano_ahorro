"""
Configuración de la aplicación Belgrano Ahorro
"""

import os

# Configuración de la aplicación
class Config:
    SECRET_KEY = 'belgrano_ahorro_secret_key_2025'
    DEBUG = True
    DATABASE_PATH = 'belgrano_ahorro.db'
    
    # Configuración de la base de datos
    DATABASE_CONFIG = {
        'database': DATABASE_PATH,
        'check_same_thread': False
    }
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuración de la aplicación
    APP_NAME = 'Belgrano Ahorro'
    APP_VERSION = '1.0.0'
    
    # Configuración de seguridad
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT = 3600  # 1 hora
    
    # Configuración de archivos
    PRODUCTOS_FILE = 'productos.json'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

# Configuración de desarrollo
class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000

# Configuración de producción
class ProductionConfig(Config):
    DEBUG = False
    HOST = '127.0.0.1'
    PORT = 5000

# Configuración por defecto
config = DevelopmentConfig() 