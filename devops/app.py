#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask application factory for DevOps service.
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from flask import Flask, jsonify, redirect, url_for

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('devops.app')

def load_environment():
    """Cargar variables de entorno desde archivos .env"""
    try:
        from dotenv import load_dotenv
        
        # Rutas posibles para el archivo .env
        current_dir = Path(__file__).parent.absolute()
        project_root = current_dir.parent.absolute()
        
        env_paths = [
            current_dir / '.env',
            project_root / '.env',
            project_root / 'devops' / '.env',
            Path('/opt/render/project/src/.env'),
            Path('/opt/render/project/src/devops/.env')
        ]
        
        # Cargar el primer archivo .env encontrado
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                logger.info(f"✅ Variables de entorno cargadas desde: {env_path}")
                return True
        
        logger.warning("⚠️ No se encontró ningún archivo .env, usando solo variables de entorno del sistema")
        return False
        
    except ImportError:
        logger.warning("⚠️ python-dotenv no está instalado. Usando solo variables de entorno del sistema.")
        return False
    except Exception as e:
        logger.error(f"❌ Error cargando variables de entorno: {e}")
        logger.error(traceback.format_exc())
        return False

def create_app():
    """
    Factory function que crea y configura la aplicación Flask.
    
    Returns:
        Flask: La aplicación Flask configurada
    """
    logger.info("🚀 Inicializando la aplicación Flask...")
    
    # Cargar variables de entorno
    load_environment()
    
    # Obtener configuración del entorno
    env = os.environ.get('FLASK_ENV', 'production')
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Crear la aplicación Flask
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    # Validar variables de entorno requeridas
    required_vars = [
        'SECRET_KEY',
        'BELGRANO_AHORRO_API_KEY',
        'TICKETS_API_PASSWORD',  # Standardized name
        'DEVOPS_USERNAME',
        'DEVOPS_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars and env != 'testing':
        logger.warning(f"⚠️  Variables de entorno faltantes: {', '.join(missing_vars)}")
    
    # Configuración básica
    app.config.update(
        ENV=env,
        DEBUG=debug,
        TESTING=env == 'testing',
        # Configuración de seguridad
        SECRET_KEY=os.environ.get('SECRET_KEY', 'devops_secret_key_2025_production_secure_def456uvw'),
        # Configuración de sesión segura
        SESSION_COOKIE_SECURE=env == 'production',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600,  # 1 hora
        # Configuración de CSRF
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_SECRET_KEY=os.environ.get('CSRF_SECRET_KEY', 'csrf_secure_key_2025_xyz789'),
        # Configuración de base de datos
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=debug,
        # Configuración de la aplicación
        BELGRANO_AHORRO_API_KEY=os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025'),
        TICKETS_API_PASSWORD=os.environ.get('TICKETS_API_PASSWORD', 'admin123'), # Standardized name
        DEVOPS_USERNAME=os.environ.get('DEVOPS_USERNAME', 'devops'),
        DEVOPS_PASSWORD=os.environ.get('DEVOPS_PASSWORD', 'DevOps2025!Secure')
    )
    
    # Configuración específica por entorno
    if env == 'development':
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Configurar logging
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('Modo DEBUG activado')
    else:
        app.logger.setLevel(logging.INFO)
    
    # Inicializar CSRF Protection
    try:
        from flask_wtf.csrf import CSRFProtect
        csrf = CSRFProtect(app)
        logger.info("✅ CSRF Protection habilitado")
    except ImportError:
        logger.warning("⚠️ Flask-WTF no está instalado. CSRF protection deshabilitado.")
        app.config['WTF_CSRF_ENABLED'] = False
    
    # Inicializar Cloudinary
    try:
        # Agregar directorio raíz al path para importar cloudinary_config
        project_root = Path(__file__).parent.parent.absolute()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from cloudinary_config import init_cloudinary
        cloudinary_configured = init_cloudinary()
        if cloudinary_configured:
            logger.info("[INIT] ✅ Cloudinary configurado correctamente")
        else:
            logger.warning("[INIT] ⚠️ Cloudinary no está configurado - las imágenes pueden no funcionar")
    except ImportError:
        logger.warning("[INIT] ⚠️ cloudinary_config no disponible - las imágenes pueden no funcionar")
    except Exception as e:
        logger.error(f"[INIT] ❌ Error inicializando Cloudinary: {e}")
    
    # Configurar CORS
    try:
        from flask_cors import CORS
        CORS(app)
        logger.info("[INIT] ✅ CORS configurado correctamente")
    except ImportError:
        logger.warning("[INIT] ⚠️ Flask-CORS no está instalado - instalar con: pip install Flask-CORS")
        
    # Configuración de base de datos si es necesario
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.logger.info('Configuración de base de datos cargada')
    
    # Verificar que las variables críticas estén configuradas
    belgrano_url = os.environ.get('BELGRANO_AHORRO_URL', '').strip().rstrip('/')
    belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY', '').strip()

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

    # Log de configuración
    logger.info("=" * 60)
    logger.info("🔍 CONFIGURACIÓN DE LA APLICACIÓN")
    logger.info("=" * 60)
    logger.info(f"   ENTORNO: {app.config.get('ENV', 'production')}")
    logger.info(f"   MODO DEBUG: {app.debug}")
    logger.info(f"   BELGRANO_AHORRO_URL: {belgrano_url}")
    logger.info(f"   BELGRANO_AHORRO_API_KEY: {'*' * min(len(belgrano_api_key), 10)}... ({len(belgrano_api_key)} caracteres)")
    logger.info("=" * 60)
    
    # Registrar blueprints
    # Registrar blueprints
    try:
        # Intentar importación como paquete primero
        try:
            from devops.routes import devops_bp
            logger.info("✅ Importado devops.routes como paquete")
        except ImportError:
            # Fallback: importación directa (cuando se corre desde el directorio devops)
            from routes import devops_bp
            logger.info("✅ Importado routes directamente (fallback)")
        
        # Verificar que no esté ya registrado
        blueprint_name = devops_bp.name if hasattr(devops_bp, 'name') else 'devops'
        if blueprint_name not in [bp.name for bp in app.blueprints.values()]:
            app.register_blueprint(devops_bp)
            logger.info("✅ Blueprint de DevOps registrado correctamente")
        else:
            logger.info("ℹ️  Blueprint de DevOps ya estaba registrado (omitiendo duplicado)")
    except Exception as e:
        logger.error(f"❌ Error registrando blueprint de DevOps: {e}")
        logger.error(traceback.format_exc())
        raise
    
    # Rutas básicas
    @app.route('/')
    def index():
        return redirect(url_for('devops.dashboard'))
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'ok',
            'service': 'devops',
            'environment': app.config.get('ENV', 'production')
        })
    
    # =================================================================
    # ENDPOINTS UNIFICADOS DE CLOUDINARY
    # =================================================================
    
    @app.route('/api/upload-image', methods=['POST'])
    def upload_image():
        """
        Endpoint unificado para subir imágenes a Cloudinary.
        
        Acepta:
        - multipart/form-data
        - Campo obligatorio: file
        - Campo opcional: folder (por defecto "belgrano-ahorro")
        
        Retorna:
        - secure_url: URL pública de la imagen en Cloudinary
        - public_id: ID público de la imagen
        """
        from flask import request
        try:
            # Verificar que se envió un archivo
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            
            # Verificar que el archivo tenga nombre
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Obtener folder opcional
            folder = request.form.get('folder', 'belgrano-ahorro')
            
            # Importar cloudinary
            try:
                import cloudinary.uploader
            except ImportError:
                return jsonify({"error": "Cloudinary not installed"}), 500
            
            # Subir a Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type='auto'
            )
            
            logger.info(f"✅ Imagen subida a Cloudinary: {result['secure_url']}")
            
            return jsonify({
                "secure_url": result["secure_url"],
                "public_id": result["public_id"]
            })
        
        except Exception as e:
            logger.error(f"❌ Error subiendo imagen a Cloudinary: {e}")
            return jsonify({"error": str(e)}), 500
    
    
    @app.route('/api/ping-cloudinary', methods=['GET'])
    def ping_cloudinary():
        """
        Endpoint para verificar la conexión con Cloudinary.
        
        Retorna:
        - status: "ok" si la conexión es exitosa
        - error: mensaje de error si falla
        """
        try:
            import cloudinary.api
            cloudinary.api.ping()
            
            # Obtener configuración
            project_root = Path(__file__).parent.parent.absolute()
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            from cloudinary_config import get_cloudinary_status
            status = get_cloudinary_status()
            
            return jsonify({
                "status": "ok",
                "configured": status['configured'],
                "cloud_name": status['cloud_name']
            })
        except ImportError:
            return jsonify({"error": "Cloudinary not installed"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    logger.info("✅ Aplicación Flask configurada correctamente")
    return app
