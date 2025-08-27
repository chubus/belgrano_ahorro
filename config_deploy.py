"""
Configuración unificada para deploy de Belgrano Ahorro y Belgrano Tickets
"""

import os
from datetime import datetime

class DeployConfig:
    """Configuración centralizada para deploy en producción"""
    
    # ==========================================
    # CONFIGURACIÓN GENERAL
    # ==========================================
    
    # Entorno
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'production')
    DEBUG = ENVIRONMENT == 'development'
    
    # Versiones
    PYTHON_VERSION = '3.12.0'
    APP_VERSION = '1.0.0'
    
    # ==========================================
    # CONFIGURACIÓN BELGRANO AHORRO
    # ==========================================
    
    # Secret keys
    AHORRO_SECRET_KEY = os.environ.get('AHORRO_SECRET_KEY', 'belgrano_ahorro_secret_key_2025')
    
    # Puerto y host
    AHORRO_PORT = int(os.environ.get('AHORRO_PORT', 5000))
    AHORRO_HOST = os.environ.get('AHORRO_HOST', '0.0.0.0')
    
    # Base de datos
    AHORRO_DB_PATH = os.environ.get('AHORRO_DB_PATH', 'belgrano_ahorro.db')
    
    # URLs de producción
    AHORRO_URL = os.environ.get('AHORRO_URL', 'https://belgrano-ahorro.onrender.com')
    
    # ==========================================
    # CONFIGURACIÓN BELGRANO TICKETS
    # ==========================================
    
    # Secret keys
    TICKETS_SECRET_KEY = os.environ.get('TICKETS_SECRET_KEY', 'belgrano_tickets_secret_2025')
    
    # Puerto y host
    TICKETS_PORT = int(os.environ.get('TICKETS_PORT', 5001))
    TICKETS_HOST = os.environ.get('TICKETS_HOST', '0.0.0.0')
    
    # Base de datos
    TICKETS_DB_PATH = os.environ.get('TICKETS_DB_PATH', 'belgrano_tickets.db')
    
    # URLs de producción
    TICKETS_URL = os.environ.get('TICKETS_URL', 'https://belgrano-tickets.onrender.com')
    
    # ==========================================
    # CONFIGURACIÓN DE INTEGRACIÓN
    # ==========================================
    
    # URLs de comunicación entre plataformas
    TICKETERA_URL = os.environ.get('TICKETERA_URL', TICKETS_URL)
    BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', AHORRO_URL)
    
    # Timeouts para API
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 10))
    API_RETRY_ATTEMPTS = int(os.environ.get('API_RETRY_ATTEMPTS', 3))
    
    # ==========================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ==========================================
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    LOGIN_TIMEOUT = int(os.environ.get('LOGIN_TIMEOUT', 300))  # 5 minutos
    
    # Sesiones
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))  # 1 hora
    
    # ==========================================
    # CONFIGURACIÓN DE LOGGING
    # ==========================================
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ==========================================
    # CONFIGURACIÓN DE MONITOREO
    # ==========================================
    
    # Health checks
    HEALTH_CHECK_INTERVAL = int(os.environ.get('HEALTH_CHECK_INTERVAL', 30))  # segundos
    
    # Métricas
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'true').lower() == 'true'
    
    # ==========================================
    # CONFIGURACIÓN DE BACKUP
    # ==========================================
    
    # Backup automático
    AUTO_BACKUP = os.environ.get('AUTO_BACKUP', 'true').lower() == 'true'
    BACKUP_INTERVAL = int(os.environ.get('BACKUP_INTERVAL', 24))  # horas
    
    # ==========================================
    # MÉTODOS DE CONFIGURACIÓN
    # ==========================================
    
    @classmethod
    def get_ahorro_config(cls):
        """Obtener configuración específica para Belgrano Ahorro"""
        return {
            'SECRET_KEY': cls.AHORRO_SECRET_KEY,
            'DEBUG': cls.DEBUG,
            'HOST': cls.AHORRO_HOST,
            'PORT': cls.AHORRO_PORT,
            'DATABASE_PATH': cls.AHORRO_DB_PATH,
            'TICKETERA_URL': cls.TICKETERA_URL,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'ENVIRONMENT': cls.ENVIRONMENT
        }
    
    @classmethod
    def get_tickets_config(cls):
        """Obtener configuración específica para Belgrano Tickets"""
        return {
            'SECRET_KEY': cls.TICKETS_SECRET_KEY,
            'DEBUG': cls.DEBUG,
            'HOST': cls.TICKETS_HOST,
            'PORT': cls.TICKETS_PORT,
            'DATABASE_PATH': cls.TICKETS_DB_PATH,
            'BELGRANO_AHORRO_URL': cls.BELGRANO_AHORRO_URL,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'ENVIRONMENT': cls.ENVIRONMENT
        }
    
    @classmethod
    def get_integration_config(cls):
        """Obtener configuración de integración"""
        return {
            'AHORRO_URL': cls.AHORRO_URL,
            'TICKETS_URL': cls.TICKETS_URL,
            'API_TIMEOUT': cls.API_TIMEOUT,
            'API_RETRY_ATTEMPTS': cls.API_RETRY_ATTEMPTS
        }
    
    @classmethod
    def validate_config(cls):
        """Validar configuración completa"""
        errors = []
        
        # Validar URLs
        if not cls.AHORRO_URL.startswith('http'):
            errors.append("AHORRO_URL debe ser una URL válida")
        
        if not cls.TICKETS_URL.startswith('http'):
            errors.append("TICKETS_URL debe ser una URL válida")
        
        # Validar puertos
        if not (1024 <= cls.AHORRO_PORT <= 65535):
            errors.append("AHORRO_PORT debe estar entre 1024 y 65535")
        
        if not (1024 <= cls.TICKETS_PORT <= 65535):
            errors.append("TICKETS_PORT debe estar entre 1024 y 65535")
        
        # Validar secret keys
        if len(cls.AHORRO_SECRET_KEY) < 16:
            errors.append("AHORRO_SECRET_KEY debe tener al menos 16 caracteres")
        
        if len(cls.TICKETS_SECRET_KEY) < 16:
            errors.append("TICKETS_SECRET_KEY debe tener al menos 16 caracteres")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Imprimir configuración actual"""
        print("🔧 CONFIGURACIÓN DE DEPLOY")
        print("=" * 40)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌍 Entorno: {cls.ENVIRONMENT}")
        print(f"🐍 Python: {cls.PYTHON_VERSION}")
        print(f"📦 Versión: {cls.APP_VERSION}")
        print()
        
        print("🌐 BELGRANO AHORRO:")
        print(f"   URL: {cls.AHORRO_URL}")
        print(f"   Puerto: {cls.AHORRO_PORT}")
        print(f"   Host: {cls.AHORRO_HOST}")
        print(f"   Base de datos: {cls.AHORRO_DB_PATH}")
        print()
        
        print("🎫 BELGRANO TICKETS:")
        print(f"   URL: {cls.TICKETS_URL}")
        print(f"   Puerto: {cls.TICKETS_PORT}")
        print(f"   Host: {cls.TICKETS_HOST}")
        print(f"   Base de datos: {cls.TICKETS_DB_PATH}")
        print()
        
        print("🔗 INTEGRACIÓN:")
        print(f"   TICKETERA_URL: {cls.TICKETERA_URL}")
        print(f"   BELGRANO_AHORRO_URL: {cls.BELGRANO_AHORRO_URL}")
        print(f"   Timeout API: {cls.API_TIMEOUT}s")
        print(f"   Reintentos: {cls.API_RETRY_ATTEMPTS}")
        print()
        
        print("🔒 SEGURIDAD:")
        print(f"   Max login attempts: {cls.MAX_LOGIN_ATTEMPTS}")
        print(f"   Session timeout: {cls.SESSION_TIMEOUT}s")
        print(f"   Login timeout: {cls.LOGIN_TIMEOUT}s")
        print()
        
        print("📊 MONITOREO:")
        print(f"   Health check interval: {cls.HEALTH_CHECK_INTERVAL}s")
        print(f"   Log level: {cls.LOG_LEVEL}")
        print(f"   Metrics enabled: {cls.ENABLE_METRICS}")
        print()
        
        # Validar configuración
        errors = cls.validate_config()
        if errors:
            print("🚨 ERRORES DE CONFIGURACIÓN:")
            for error in errors:
                print(f"   ❌ {error}")
        else:
            print("✅ Configuración válida")

# Configuración por defecto
config = DeployConfig()

# Configuraciones específicas por entorno
class DevelopmentConfig(DeployConfig):
    """Configuración para desarrollo"""
    ENVIRONMENT = 'development'
    DEBUG = True
    AHORRO_URL = 'http://localhost:5000'
    TICKETS_URL = 'http://localhost:5001'
    TICKETERA_URL = 'http://localhost:5001'
    BELGRANO_AHORRO_URL = 'http://localhost:5000'

class ProductionConfig(DeployConfig):
    """Configuración para producción"""
    ENVIRONMENT = 'production'
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(DeployConfig):
    """Configuración para testing"""
    ENVIRONMENT = 'testing'
    DEBUG = True
    AHORRO_DB_PATH = ':memory:'
    TICKETS_DB_PATH = ':memory:'

# Función para obtener configuración según entorno
def get_config():
    """Obtener configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'production')
    
    if env == 'development':
        return DevelopmentConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return ProductionConfig()

# Función para generar variables de entorno
def generate_env_vars():
    """Generar archivo .env con variables de entorno"""
    
    env_content = f"""# Configuración de deploy - Belgrano Ahorro y Tickets
# Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Entorno
FLASK_ENV=production
PYTHON_VERSION=3.12.0

# Belgrano Ahorro
AHORRO_SECRET_KEY={config.AHORRO_SECRET_KEY}
AHORRO_PORT={config.AHORRO_PORT}
AHORRO_HOST={config.AHORRO_HOST}
AHORRO_DB_PATH={config.AHORRO_DB_PATH}
AHORRO_URL={config.AHORRO_URL}

# Belgrano Tickets
TICKETS_SECRET_KEY={config.TICKETS_SECRET_KEY}
TICKETS_PORT={config.TICKETS_PORT}
TICKETS_HOST={config.TICKETS_HOST}
TICKETS_DB_PATH={config.TICKETS_DB_PATH}
TICKETS_URL={config.TICKETS_URL}

# Integración
TICKETERA_URL={config.TICKETERA_URL}
BELGRANO_AHORRO_URL={config.BELGRANO_AHORRO_URL}
API_TIMEOUT={config.API_TIMEOUT}
API_RETRY_ATTEMPTS={config.API_RETRY_ATTEMPTS}

# Seguridad
MAX_LOGIN_ATTEMPTS={config.MAX_LOGIN_ATTEMPTS}
LOGIN_TIMEOUT={config.LOGIN_TIMEOUT}
SESSION_TIMEOUT={config.SESSION_TIMEOUT}

# Logging y monitoreo
LOG_LEVEL={config.LOG_LEVEL}
HEALTH_CHECK_INTERVAL={config.HEALTH_CHECK_INTERVAL}
ENABLE_METRICS={str(config.ENABLE_METRICS).lower()}

# Backup
AUTO_BACKUP={str(config.AUTO_BACKUP).lower()}
BACKUP_INTERVAL={config.BACKUP_INTERVAL}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Archivo .env generado correctamente")

if __name__ == "__main__":
    # Mostrar configuración actual
    config.print_config()
    
    # Generar archivo .env
    print("\n📝 Generando archivo .env...")
    generate_env_vars()
