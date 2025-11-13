#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Flask independiente para DevOps
Punto de entrada principal del servicio DevOps
"""

import os
import sys
import logging
from flask import Flask

# Configurar logging PRIMERO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    # Buscar .env en el directorio devops y en el directorio raíz
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _parent_dir = os.path.dirname(_current_dir)
    env_paths = [
        os.path.join(_current_dir, '.env'),
        os.path.join(_current_dir, 'env', '.env'),
        os.path.join(_parent_dir, '.env'),
    ]
    
    env_loaded = False
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=False)
            logger.info(f"✅ Variables de entorno cargadas desde: {env_path}")
            env_loaded = True
            break
    
    # Si no existe .env, crear uno con valores por defecto para producción
    if not env_loaded:
        default_env_path = os.path.join(_current_dir, '.env')
        if not os.path.exists(default_env_path):
            logger.warning("⚠️ No se encontró archivo .env, creando uno con valores por defecto...")
            try:
                env_content = """# Variables de Entorno para DevOps - PRODUCCIÓN
# Configurar estas variables en Render Dashboard o editar este archivo

# Belgrano Ahorro API (OBLIGATORIO)
BELGRANO_AHORRO_URL=https://belgranoahorro-aliq.onrender.com
BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Configuración de API
API_TIMEOUT_SECS=20
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=1.0

# Ticketera (OPCIONAL)
TICKETERA_URL=https://ticketerabelgrano.onrender.com
TICKETS_API_URL=https://ticketerabelgrano.onrender.com

# Seguridad DevOps
DEVOPS_USERNAME=devops
DEVOPS_PASSWORD=devops_password

# Flask
FLASK_ENV=production
SECRET_KEY=devops_secret_key_2025_prod_segura_cambiar_en_produccion
"""
                with open(default_env_path, 'w', encoding='utf-8') as f:
                    f.write(env_content)
                load_dotenv(default_env_path, override=False)
                logger.info(f"✅ Archivo .env creado en: {default_env_path}")
                logger.info("✅ Archivo .env creado con API key por defecto: belgrano_ahorro_api_key_2025")
            except Exception as e:
                logger.error(f"❌ Error creando archivo .env: {e}")
        else:
            logger.info("ℹ️ No se encontró archivo .env, usando variables de entorno del sistema")
except ImportError:
    # python-dotenv no está instalado, usar solo variables de entorno del sistema
    logger.warning("⚠️ python-dotenv no instalado, usando solo variables de entorno del sistema")

# Determinar la ruta base del módulo devops
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)

# Asegurar que el directorio padre (raíz del proyecto) esté en sys.path
# Esto permite que los imports como 'from devops.routes import ...' funcionen
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Buscar templates y static en la ubicación correcta
_template_folder = os.path.join(_current_dir, 'templates')
_static_folder = os.path.join(_current_dir, 'static')

# Verificar que existan las carpetas, si no, usar valores relativos
if not os.path.exists(_template_folder):
    _template_folder = 'templates'
if not os.path.exists(_static_folder):
    _static_folder = 'static'

# Crear la aplicación Flask
app = Flask(__name__, 
            template_folder=_template_folder,
            static_folder=_static_folder)

# Configurar secret key desde variables de entorno
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devops_secret_key_2025_prod_segura')

# Configurar cookies de sesión
app.config.update(
    SESSION_COOKIE_SAMESITE=os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax'),
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true',
    REMEMBER_COOKIE_SECURE=os.environ.get('REMEMBER_COOKIE_SECURE', 'false').lower() == 'true',
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=3600,  # 1 hora
)

# Verificar que las variables críticas estén configuradas antes de registrar el blueprint
belgrano_url = os.environ.get('BELGRANO_AHORRO_URL', '').strip().rstrip('/')
belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY', '').strip()

# Log detallado de las variables encontradas
logger.info("=" * 60)
logger.info("🔍 VERIFICANDO VARIABLES DE ENTORNO")
logger.info("=" * 60)
logger.info(f"BELGRANO_AHORRO_URL: {belgrano_url if belgrano_url else '❌ NO CONFIGURADA'}")
logger.info(f"BELGRANO_AHORRO_API_KEY: {'✅ CONFIGURADA (' + str(len(belgrano_api_key)) + ' caracteres)' if belgrano_api_key else '❌ NO CONFIGURADA'}")

# Valores por defecto seguros
DEFAULT_URL = 'https://belgranoahorro-aliq.onrender.com'
DEFAULT_API_KEY = 'belgrano_ahorro_api_key_2025'

# Si no están configuradas, usar valores por defecto
if not belgrano_url:
    belgrano_url = DEFAULT_URL
    os.environ['BELGRANO_AHORRO_URL'] = belgrano_url
    logger.info(f"✅ Usando URL por defecto: {belgrano_url}")

if not belgrano_api_key:
    belgrano_api_key = DEFAULT_API_KEY
    os.environ['BELGRANO_AHORRO_API_KEY'] = belgrano_api_key
    logger.info("✅ Usando API key por defecto")

# Asegurar que los valores están establecidos
belgrano_url = belgrano_url or DEFAULT_URL
belgrano_api_key = belgrano_api_key or DEFAULT_API_KEY

# Establecer en entorno si no estaban
if not os.getenv('BELGRANO_AHORRO_URL'):
    os.environ['BELGRANO_AHORRO_URL'] = belgrano_url
if not os.getenv('BELGRANO_AHORRO_API_KEY'):
    os.environ['BELGRANO_AHORRO_API_KEY'] = belgrano_api_key

# Log informativo
using_defaults = (belgrano_url == DEFAULT_URL or belgrano_api_key == DEFAULT_API_KEY)

logger.info("=" * 60)
if using_defaults:
    logger.info("ℹ️ Variables de entorno usando valores por defecto")
    logger.info("   Para producción, configure BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY en Render Dashboard → Environment")
else:
    logger.info("✅ Variables de entorno configuradas desde entorno")
logger.info(f"   BELGRANO_AHORRO_URL: {belgrano_url}")
logger.info(f"   BELGRANO_AHORRO_API_KEY: {'*' * min(len(belgrano_api_key), 10)}... ({len(belgrano_api_key)} caracteres)")
logger.info("=" * 60)

# Registrar blueprint de DevOps
try:
    # Intentar importar desde diferentes ubicaciones posibles
    try:
        from devops.routes import devops_bp
    except ImportError:
        # Si estamos dentro del directorio devops, importar directamente
        from routes import devops_bp
    
    app.register_blueprint(devops_bp)
    logger.info("✅ Blueprint de DevOps registrado correctamente")
except Exception as e:
    logger.error(f"❌ Error registrando blueprint de DevOps: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise

# Ruta raíz - redirigir a DevOps
@app.route('/')
def root():
    from flask import redirect, url_for
    return redirect(url_for('devops.dashboard'))

# Health check endpoint
@app.route('/health')
def health():
    return {'status': 'ok', 'service': 'devops'}, 200

# Punto de entrada cuando se ejecuta directamente
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    
    logger.info(f"🚀 Iniciando servicio DevOps...")
    logger.info(f"📱 Puerto: {port}")
    logger.info(f"🌐 Host: {host}")
    logger.info(f"🔧 Debug: {debug}")
    
    app.run(host=host, port=port, debug=debug)

