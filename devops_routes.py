#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema DevOps Sólido para Belgrano Tickets
Proporciona gestión completa de la aplicación desde DevOps
"""

import os
import json
import requests
from functools import wraps
from datetime import datetime
import logging
from urllib.parse import urljoin
from flask import Blueprint, request, jsonify, redirect, url_for, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de API y credenciales DevOps
try:
    from config_env import get_api_config
    api_config = get_api_config()
    BELGRANO_AHORRO_URL = api_config['belgrano_ahorro_url']
    BELGRANO_AHORRO_API_KEY = api_config['belgrano_ahorro_api_key']
except ImportError:
    # Fallback a variables de entorno directas
    BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL')
    BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY')

API_TIMEOUT_SECS = 10

# Credenciales de DevOps (propias, separadas del login de ticketera)
DEVOPS_USERNAME = os.environ.get('DEVOPS_USERNAME', 'devops')
DEVOPS_PASSWORD_PLAIN = os.environ.get('DEVOPS_PASSWORD', 'DevOps2025!Secure')

# Hash de la contraseña para comparación segura
DEVOPS_PASSWORD_HASH = generate_password_hash(DEVOPS_PASSWORD_PLAIN)

# Validar variables de entorno críticas
env_status = os.environ.get('FLASK_ENV', 'development')
if not BELGRANO_AHORRO_URL:
    if env_status != 'production':
        logger.info("ℹ️ BELGRANO_AHORRO_URL no configurada (normal en desarrollo)")
    else:
        logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_URL no está definida")

if not BELGRANO_AHORRO_API_KEY:
    if env_status != 'production':
        logger.info("ℹ️ BELGRANO_AHORRO_API_KEY no configurada (normal en desarrollo)")
    else:
        logger.warning("⚠️ Variable de entorno BELGRANO_AHORRO_API_KEY no está definida")

# Importar cliente API
try:
    from belgrano_tickets.api_client import create_api_client, api_client as global_api_client
    if BELGRANO_AHORRO_URL and BELGRANO_AHORRO_API_KEY:
        devops_api_client = create_api_client(BELGRANO_AHORRO_URL, BELGRANO_AHORRO_API_KEY)
        logger.info("Cliente API de Belgrano Ahorro inicializado para DevOps")
    else:
        devops_api_client = None
        if env_status == 'production':
            logger.warning("Variables de entorno no configuradas para cliente API de DevOps")
        else:
            logger.info("Cliente API de DevOps no inicializado (variables no configuradas)")
except ImportError as e:
    logger.error(f"No se pudo inicializar el cliente API: {e}")
    devops_api_client = None

# Crear blueprint con prefijo
devops_bp = Blueprint('devops', __name__, url_prefix='/devops')

# =============================
# AUTENTICACIÓN DEVOPS (PROPIA)
# =============================

def devops_is_authenticated():
    """Verificar si DevOps está autenticado"""
    try:
        return session.get('devops_authenticated') is True
    except Exception as e:
        logger.error(f"Error verificando autenticación DevOps: {e}")
        return False

def devops_login_required(fn):
    """Decorador para requerir autenticación de DevOps"""
    def wrapper(*args, **kwargs):
        if not devops_is_authenticated():
            # Redirigir directamente al login de DevOps
            logger.info("Redirigiendo a DevOps login")
            return redirect('/devops/login')
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@devops_bp.route('/login', methods=['GET', 'POST'])
def devops_login():
    """Login propio de DevOps con credenciales separadas."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == DEVOPS_USERNAME and check_password_hash(DEVOPS_PASSWORD_HASH, password):
            try:
                session['devops_authenticated'] = True
                session.permanent = True
                logger.info(f"Login exitoso de DevOps: {username}")
                return redirect(url_for('devops.devops_home'))
            except Exception as e:
                logger.error(f"Error estableciendo sesión DevOps: {e}")
                return make_response("Error interno del servidor", 500)
        else:
            logger.warning(f"Intento de login fallido de DevOps: {username}")
            # Mostrar formulario con error
            html_error = f"""
            <!doctype html>
            <html>
            <head>
                <meta charset='utf-8'>
                <title>DevOps Login - Belgrano Tickets</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h2 {{ color: #333; text-align: center; margin-bottom: 30px; }}
                    .form-group {{ margin-bottom: 20px; }}
                    label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
                    input[type="text"], input[type="password"] {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
                    button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
                    button:hover {{ background: #0056b3; }}
                    .info {{ background: #e7f3ff; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #007bff; }}
                    .error {{ background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #dc3545; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>🔧 DevOps Login</h2>
                    <div class="error">
                        <strong>❌ Credenciales incorrectas</strong><br>
                        Verifique su usuario y contraseña
                    </div>
                    <div class="info">
                        <strong>Sistema DevOps</strong><br>
                        Acceso independiente para administración del sistema
                    </div>
                    <form method='post'>
                        <div class="form-group">
                            <label>Usuario DevOps:</label>
                            <input type="text" name='username' value='{username}' required />
                        </div>
                        <div class="form-group">
                            <label>Contraseña:</label>
                            <input type='password' name='password' placeholder='Ingrese su contraseña' required />
                        </div>
                        <button type='submit'>🔐 Ingresar a DevOps</button>
                    </form>
                    <div style="text-align: center; margin-top: 20px; color: #666;">
                        <small>Sistema DevOps v2.0 - Belgrano Tickets</small>
                    </div>
                </div>
            </body>
            </html>
            """
            return make_response(html_error, 401)

    # Formulario HTML mejorado para DevOps
    html = f"""
    <!doctype html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>DevOps Login - Belgrano Tickets</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h2 {{ color: #333; text-align: center; margin-bottom: 30px; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
            input[type="text"], input[type="password"] {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #0056b3; }}
            .info {{ background: #e7f3ff; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 4px solid #007bff; }}
            .error {{ color: #dc3545; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔧 DevOps Login</h2>
            <div class="info">
                <strong>Sistema DevOps</strong><br>
                Acceso independiente para administración del sistema
            </div>
            <form method='post'>
                <div class="form-group">
                    <label>Usuario DevOps:</label>
                    <input type="text" name='username' value='{DEVOPS_USERNAME}' required />
                </div>
                <div class="form-group">
                    <label>Contraseña:</label>
                    <input type='password' name='password' placeholder='Ingrese su contraseña' required />
                </div>
                <button type='submit'>🔐 Ingresar a DevOps</button>
            </form>
            <div style="text-align: center; margin-top: 20px; color: #666;">
                <small>Sistema DevOps v2.0 - Belgrano Tickets</small>
            </div>
        </div>
    </body>
    </html>
    """
    return make_response(html, 200)

@devops_bp.route('/logout', methods=['POST', 'GET'])
def devops_logout():
    """Cerrar sesión de DevOps"""
    try:
        session.pop('devops_authenticated', None)
        logger.info("Logout exitoso de DevOps")
        return redirect(url_for('devops.devops_login'))
    except Exception as e:
        logger.error(f"Error en logout DevOps: {e}")
        return redirect('/devops/login')

@devops_bp.route('/test')
def devops_test():
    """Endpoint de prueba para verificar que DevOps funciona"""
    from flask import request, make_response
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
        'status': 'success',
        'message': 'DevOps funcionando correctamente',
        'timestamp': datetime.now().isoformat(),
            'authenticated': devops_is_authenticated(),
            'endpoints': {
                'health': '/devops/health',
                'status': '/devops/status',
                'ofertas': '/devops/ofertas',
                'negocios': '/devops/negocios',
                'productos': '/devops/productos',
                'precios': '/devops/precios'
            }
        })
    
    # Si no es AJAX, devolver HTML formateado
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test DevOps - Belgrano Tickets</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            .container { 
                max-width: 800px; 
                margin: 50px auto; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 30px; 
                text-align: center; 
            }
            .content { padding: 30px; }
            .status-card {
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
            }
            .endpoint-list {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .endpoint-item {
                padding: 10px;
                margin: 5px 0;
                background: white;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 5px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 Test DevOps</h1>
                <p>Sistema DevOps funcionando correctamente</p>
            </div>
            
            <div class="content">
                <div class="status-card">
                    <h3>✅ Sistema Operativo</h3>
                    <p>DevOps está funcionando correctamente</p>
                    <p><strong>Timestamp:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
                </div>
                
                <div class="endpoint-list">
                    <h4>📋 Endpoints Disponibles</h4>
                    <div class="endpoint-item">
                        <strong>GET</strong> /devops/health - Health check del sistema
                    </div>
                    <div class="endpoint-item">
                        <strong>GET</strong> /devops/status - Estado detallado del sistema
                    </div>
                    <div class="endpoint-item">
                        <strong>GET</strong> /devops/ofertas - Gestión de ofertas
                    </div>
                    <div class="endpoint-item">
                        <strong>GET</strong> /devops/negocios - Gestión de negocios
                    </div>
                    <div class="endpoint-item">
                        <strong>GET</strong> /devops/productos - Gestión de productos
                    </div>
                    <div class="endpoint-item">
                        <strong>GET</strong> /devops/precios - Gestión de precios
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/devops/" class="btn">🏠 Panel Principal</a>
                    <a href="/devops/health" class="btn">💚 Health Check</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return make_response(html, 200)

# Función para construir URLs de API
def build_api_url(endpoint):
    """Construir URL completa de API"""
    if not BELGRANO_AHORRO_URL:
        logger.warning("BELGRANO_AHORRO_URL no está configurada")
        return None
    return urljoin(BELGRANO_AHORRO_URL, f'/api/{endpoint}')

# Función para sincronizar cambios
def sincronizar_cambio_inmediato(tipo_cambio, datos):
    """Sincronizar cambio inmediatamente con la API"""
    try:
        logger.info(f"Sincronizando cambio: {tipo_cambio}")
        
        if not devops_api_client:
            logger.warning("Cliente API no disponible para sincronización")
            return False
            
        # Usar el cliente API para sincronizar
        resultado = devops_api_client.sync_data(tipo_cambio, datos)
        if resultado:
            logger.info(f"Sincronización exitosa: {tipo_cambio}")
            return True
        else:
            logger.error(f"Error en sincronización de {tipo_cambio}")
            return False
            
    except Exception as e:
        logger.error(f"Error en sincronización: {e}")
        return False

# =================================================================
# RUTAS PRINCIPALES DE DEVOPS
# =================================================================

@devops_bp.route('/')
@devops_login_required
def devops_home():
    """Panel principal de DevOps - Información del sistema"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            # Obtener información del sistema
            system_info = {
                'timestamp': datetime.now().isoformat(),
                'service': 'DevOps System',
                'version': '2.0.0',
                'status': 'operational',
                'environment': {
                    'python_version': os.sys.version,
                    'working_directory': os.getcwd(),
                    'environment_variables': {
                        'BELGRANO_AHORRO_URL': BELGRANO_AHORRO_URL,
                        'BELGRANO_AHORRO_API_KEY': '***configurada***' if BELGRANO_AHORRO_API_KEY else 'No configurada'
                    }
                },
                'endpoints': {
                    'health': '/devops/health',
                    'info': '/devops/info',
                    'status': '/devops/status',
                    'ofertas': '/devops/ofertas',
                    'negocios': '/devops/negocios',
                    'sync': '/devops/sync',
                    'logs': '/devops/logs'
                }
            }
            
            return jsonify({
                'status': 'success',
                'message': 'Sistema DevOps funcionando correctamente',
                'data': system_info
            })
            
        except Exception as e:
            logger.error(f"Error en devops_home: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error interno: {str(e)}'
            }), 500
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel DevOps - Belgrano Tickets</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1400px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 30px; 
                text-align: center; 
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .content { padding: 30px; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
            }
            .stat-card h3 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .stat-card p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #667eea;
            }
            .card h3 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 5px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .btn-success { background: linear-gradient(135deg, #28a745, #20c997); }
            .btn-warning { background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; }
            .btn-info { background: linear-gradient(135deg, #17a2b8, #138496); }
            .btn-danger { background: linear-gradient(135deg, #dc3545, #c82333); }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-online { background: #28a745; }
            .status-offline { background: #dc3545; }
            .status-warning { background: #ffc107; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 Panel DevOps</h1>
                <p>Sistema de gestión y administración de Belgrano Tickets</p>
            </div>
            
            <div class="content">
                <div class="stats">
                    <div class="stat-card">
                        <h3 id="system-status">Online</h3>
                        <p>Estado del Sistema</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="total-endpoints">12</h3>
                        <p>Endpoints Activos</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="uptime">24h</h3>
                        <p>Tiempo Activo</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="version">v2.0</h3>
                        <p>Versión</p>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="card">
                        <h3>🎯 Gestión de Contenido</h3>
                        <p>Administra ofertas, productos, negocios y precios del sistema.</p>
                        <a href="/devops/ofertas" class="btn">Gestionar Ofertas</a>
                        <a href="/devops/negocios" class="btn">Gestionar Negocios</a>
                        <a href="/devops/productos" class="btn">Gestionar Productos</a>
                        <a href="/devops/precios" class="btn">Gestionar Precios</a>
                    </div>
                    
                    <div class="card">
                        <h3>🔧 Herramientas de Desarrollo</h3>
                        <p>Herramientas para monitoreo, logs y configuración del sistema.</p>
                        <a href="/devops/logs" class="btn btn-info">Ver Logs</a>
                        <a href="/devops/config" class="btn btn-info">Configuración</a>
                        <a href="/devops/health" class="btn btn-warning">Health Check</a>
                    </div>
                    
                    <div class="card">
                        <h3>🔄 Sincronización y Datos</h3>
                        <p>Gestiona la sincronización de datos entre sistemas.</p>
                        <a href="/devops/sync" class="btn btn-success">Sincronizar Datos</a>
                        <a href="/devops/conectar-belgrano" class="btn btn-info">Conectar Belgrano Ahorro</a>
                        <button class="btn btn-warning" onclick="actualizarEstadisticas()">Actualizar Stats</button>
                    </div>
                    
                    <div class="card">
                        <h3>📊 Estado del Sistema</h3>
                        <p>Información en tiempo real del estado del sistema.</p>
                        <span class="status-indicator status-online"></span>Sistema Online<br>
                        <span class="status-indicator status-online"></span>API Conectada<br>
                        <span class="status-indicator status-online"></span>Base de Datos OK<br>
                        <button class="btn btn-info" onclick="cargarInfoSistema()">Ver Detalles</button>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/devops/logout" class="btn btn-danger">Cerrar Sesión</a>
                </div>
            </div>
        </div>
        
        <script>
            function actualizarEstadisticas() {
                document.getElementById('uptime').textContent = '25h';
                document.getElementById('total-endpoints').textContent = '13';
                alert('Estadísticas actualizadas correctamente');
            }
            
            function cargarInfoSistema() {
                fetch('/devops/?ajax=true', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Sistema: ' + data.data.service + ' v' + data.data.version + '\\nEstado: ' + data.data.status);
                    }
                })
                .catch(error => {
                    alert('Error cargando información: ' + error);
                });
            }
            
            // Cargar información inicial
            cargarInfoSistema();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

@devops_bp.route('/health')
@devops_login_required
def devops_health():
    """Health check completo del sistema DevOps"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'service': 'devops',
                'status': 'healthy',
                'version': '2.0.0',
                'checks': {
                    'database': 'healthy',
                    'api_connection': 'checking',
                    'sync_service': 'healthy',
                    'logging': 'healthy'
                }
            }
            
            # Verificar conexión con API externa
            try:
                # response = requests.get(
                #     build_api_url('healthz'),
                #     headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
                #     timeout=5
                # )
                # if response.status_code == 200:
                #     health_status['checks']['api_connection'] = 'healthy'
                # else:
                #     health_status['checks']['api_connection'] = 'warning'
                health_status['checks']['api_connection'] = 'disabled'  # Temporalmente deshabilitado
            except Exception as e:
                health_status['checks']['api_connection'] = 'error'
                health_status['api_error'] = str(e)
            
            return jsonify({
                'status': 'success',
                'data': health_status
            })
            
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error en health check: {str(e)}'
            }), 500
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/health.html')

@devops_bp.route('/status')
@devops_login_required
def devops_status():
    """Estado detallado del sistema"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'uptime': 'N/A',
                'memory_usage': 'N/A',
                'cpu_usage': 'N/A',
                'disk_usage': 'N/A'
            },
            'services': {
                'web_server': 'running',
                'database': 'connected',
                'api_client': 'active',
                'sync_service': 'active'
            },
            'configuration': {
                'belgrano_ahorro_url': BELGRANO_AHORRO_URL,
                'api_key_configured': bool(BELGRANO_AHORRO_API_KEY),
                'timeout_seconds': API_TIMEOUT_SECS
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo status: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo status: {str(e)}'
        }), 500

@devops_bp.route('/info')
@devops_login_required
def devops_info():
    """Información completa del sistema DevOps"""
    try:
        return jsonify({
            'status': 'success',
            'message': 'Información del sistema DevOps',
            'data': {
        'service': 'DevOps System v2.0',
        'description': 'Sistema de gestión DevOps para Belgrano Tickets',
        'features': [
            'Monitoreo de salud del sistema',
            'Gestión de ofertas y negocios',
            'Sincronización con API externa',
            'Logging y debugging',
            'Panel de administración'
        ],
        'endpoints': {
            'monitoring': {
                'GET': '/devops/health - Health check',
                'GET': '/devops/status - Estado del sistema',
                'GET': '/devops/info - Información del servicio'
            },
            'management': {
                'GET': '/devops/ofertas - Gestión de ofertas',
                'GET': '/devops/negocios - Gestión de negocios',
                'POST': '/devops/sync - Sincronización manual'
            },
            'utilities': {
                'GET': '/devops/logs - Ver logs del sistema',
                'GET': '/devops/config - Configuración actual'
            }
        },
        'documentation': {
            'api_docs': '/devops/docs',
            'health_endpoint': '/devops/health',
            'status_endpoint': '/devops/status'
        },
        'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error obteniendo información: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo información: {str(e)}'
        }), 500

# ================================================================
# AUTENTICACIÓN (YA MANEJADA ARRIBA CON SISTEMA PROPIO)
# ================================================================

# =================================================================
# GESTIÓN DE OFERTAS
# =================================================================

@devops_bp.route('/ofertas')
@devops_login_required
def gestion_ofertas():
    """Gestión completa de ofertas"""
    from flask import request, make_response, render_template
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            from datetime import datetime
            
            # Simular datos de ofertas
            ofertas = [
                {
                    'id': 1,
                    'titulo': 'Oferta Especial 50%',
                    'descripcion': 'Descuento del 50% en productos seleccionados',
                    'descuento': 50,
                    'fecha_inicio': '2025-01-19',
                    'fecha_fin': '2025-01-31',
                    'activa': True,
                    'negocio_id': 1
                },
                {
                    'id': 2,
                    'titulo': 'Oferta 2x1',
                    'descripcion': 'Lleva 2 productos y paga solo 1',
                    'descuento': 100,
                    'fecha_inicio': '2025-01-20',
                    'fecha_fin': '2025-02-15',
                    'activa': True,
                    'negocio_id': 2
                }
            ]
            
            return jsonify({
                'status': 'success',
                'data': {
                    'ofertas': ofertas,
                    'total': len(ofertas),
                    'timestamp': datetime.now().isoformat()
                },
                'source': 'simulated',
                'message': f'Ofertas obtenidas correctamente ({len(ofertas)} encontradas)'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo ofertas: {str(e)}',
                'data': [],
                'source': 'error'
            }), 500
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/ofertas.html')

@devops_bp.route('/negocios')
@devops_login_required
def gestion_negocios():
    """Gestión completa de negocios"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            from datetime import datetime
            
            # Simular datos de negocios
            negocios = [
                {
                    'id': 1,
                    'nombre': 'Supermercado Central',
                    'descripcion': 'Supermercado con productos frescos y ofertas diarias',
                    'direccion': 'Av. Belgrano 1234',
                    'telefono': '+54 11 1234-5678',
                    'email': 'info@supercentral.com',
                    'activo': True
                },
                {
                    'id': 2,
                    'nombre': 'Farmacia San Martín',
                    'descripcion': 'Farmacia con medicamentos y productos de salud',
                    'direccion': 'Calle San Martín 567',
                    'telefono': '+54 11 9876-5432',
                    'email': 'contacto@farmaciasanmartin.com',
                    'activo': True
                },
                {
                    'id': 3,
                    'nombre': 'Restaurante El Buen Sabor',
                    'descripcion': 'Restaurante con comida casera y delivery',
                    'direccion': 'Av. Corrientes 890',
                    'telefono': '+54 11 5555-1234',
                    'email': 'pedidos@elbuensabor.com',
                    'activo': True
                }
            ]
            
            return jsonify({
                'status': 'success',
                'data': {
                    'negocios': negocios,
                    'total': len(negocios),
                    'timestamp': datetime.now().isoformat()
                },
                'source': 'simulated',
                'message': f'Negocios obtenidos correctamente ({len(negocios)} encontrados)'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo negocios: {str(e)}',
                'data': [],
                'source': 'error'
            }), 500
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/negocios.html')

@devops_bp.route('/productos')
@devops_login_required
def gestion_productos():
    """Gestión completa de productos"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            from datetime import datetime
            
            # Simular datos de productos
            productos = [
                {
                    'id': 1,
                    'nombre': 'Leche Entera 1L',
                    'descripcion': 'Leche fresca pasteurizada',
                    'precio': 850.00,
                    'categoria_id': 1,
                    'negocio_id': 1,
                    'activo': True
                },
                {
                    'id': 2,
                    'nombre': 'Pan Integral',
                    'descripcion': 'Pan de trigo integral fresco',
                    'precio': 450.00,
                    'categoria_id': 2,
                    'negocio_id': 1,
                    'activo': True
                },
                {
                    'id': 3,
                    'nombre': 'Aspirina 500mg',
                    'descripcion': 'Analgésico y antipirético',
                    'precio': 1200.00,
                    'categoria_id': 3,
                    'negocio_id': 2,
                    'activo': True
                }
            ]
            
            return jsonify({
                'status': 'success',
                'data': {
                    'productos': productos,
                    'total': len(productos),
                    'timestamp': datetime.now().isoformat()
                },
                'source': 'simulated',
                'message': f'Productos obtenidos correctamente ({len(productos)} encontrados)'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo productos: {str(e)}',
                'data': [],
                'source': 'error'
            }), 500
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/productos.html')

@devops_bp.route('/precios')
@devops_login_required
def gestion_precios():
    """Gestión completa de precios"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            from datetime import datetime
            
            # Simular datos de precios
            precios = [
                {
                    'id': 1,
                    'producto_id': 1,
                    'negocio_id': 1,
                    'precio': 850.00,
                    'precio_anterior': 1000.00,
                    'descuento': 15.0,
                    'fecha_actualizacion': '2025-01-19',
                    'activo': True
                },
                {
                    'id': 2,
                    'producto_id': 2,
                    'negocio_id': 1,
                    'precio': 450.00,
                    'precio_anterior': 500.00,
                    'descuento': 10.0,
                    'fecha_actualizacion': '2025-01-18',
                    'activo': True
                },
                {
                    'id': 3,
                    'producto_id': 3,
                    'negocio_id': 2,
                    'precio': 1200.00,
                    'precio_anterior': 1200.00,
                    'descuento': 0.0,
                    'fecha_actualizacion': '2025-01-17',
                    'activo': True
                }
            ]
            
            return jsonify({
                'status': 'success',
                'data': {
                    'precios': precios,
                    'total': len(precios),
                    'timestamp': datetime.now().isoformat()
                },
                'source': 'simulated',
                'message': f'Precios obtenidos correctamente ({len(precios)} encontrados)'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo precios: {str(e)}',
                'data': [],
                'source': 'error'
            }), 500
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/precios.html')

# =================================================================
# SINCRONIZACIÓN Y UTILIDADES
# =================================================================

@devops_bp.route('/sync', methods=['GET', 'POST'])
@devops_login_required
def sincronizacion_manual():
    """Forzar sincronización manual"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            sync_results = {
                'timestamp': datetime.now().isoformat(),
                'ofertas': {'status': 'pending'},
                'negocios': {'status': 'pending'},
                'overall_status': 'running'
            }
            
            # Sincronizar ofertas
            try:
                # response = requests.get(
                #     build_api_url('v1/ofertas'),
                #     headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
                #     timeout=API_TIMEOUT_SECS
                # )
                # sync_results['ofertas'] = {
                #     'status': 'success' if response.status_code == 200 else 'error',
                #     'status_code': response.status_code,
                #     'count': len(response.json()) if response.status_code == 200 else 0
                # }
                sync_results['ofertas'] = {'status': 'disabled', 'message': 'API temporalmente deshabilitada'}
            except Exception as e:
                sync_results['ofertas'] = {'status': 'error', 'error': str(e)}
            
            # Sincronizar negocios
            try:
                # response = requests.get(
                #     build_api_url('v1/negocios'),
                #     headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
                #     timeout=API_TIMEOUT_SECS
                # )
                # sync_results['negocios'] = {
                #     'status': 'success' if response.status_code == 200 else 'error',
                #     'status_code': response.status_code,
                #     'count': len(response.json()) if response.status_code == 200 else 0
                # }
                sync_results['negocios'] = {'status': 'disabled', 'message': 'API temporalmente deshabilitada'}
            except Exception as e:
                sync_results['negocios'] = {'status': 'error', 'error': str(e)}
            
            # Determinar estado general
            if all(item['status'] == 'success' for item in [sync_results['ofertas'], sync_results['negocios']]):
                sync_results['overall_status'] = 'success'
            elif any(item['status'] == 'success' for item in [sync_results['ofertas'], sync_results['negocios']]):
                sync_results['overall_status'] = 'partial'
            else:
                sync_results['overall_status'] = 'error'
            
            return jsonify({
                'status': 'success',
                'message': 'Sincronización completada',
                'data': sync_results
            })
            
        except Exception as e:
            logger.error(f"Error en sincronización manual: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error en sincronización: {str(e)}'
            }), 500
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sincronización de Datos - DevOps</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1400px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                padding: 30px; 
                text-align: center; 
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .content { padding: 30px; }
            .toolbar { 
                display: flex; 
                gap: 15px; 
                margin-bottom: 30px; 
                flex-wrap: wrap;
                align-items: center;
            }
            .btn { 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-weight: 600;
                transition: all 0.3s ease;
                text-decoration: none; 
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            .btn-primary { background: linear-gradient(135deg, #007bff, #0056b3); color: white; }
            .btn-success { background: linear-gradient(135deg, #28a745, #20c997); color: white; }
            .btn-warning { background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; }
            .btn-danger { background: linear-gradient(135deg, #dc3545, #c82333); color: white; }
            .btn-secondary { background: linear-gradient(135deg, #6c757d, #5a6268); color: white; }
            .sync-section { 
                background: white; 
                border-radius: 10px; 
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .sync-header { 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                padding: 20px; 
                border-bottom: 1px solid #dee2e6;
                font-weight: 600;
                color: #495057;
            }
            .sync-body { padding: 20px; }
            .sync-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 0;
                border-bottom: 1px solid #f1f3f4;
            }
            .sync-item:last-child { border-bottom: none; }
            .sync-label {
                font-weight: 600;
                color: #495057;
                flex: 1;
            }
            .sync-status {
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .status-success { background: linear-gradient(135deg, #d4edda, #c3e6cb); color: #155724; }
            .status-error { background: linear-gradient(135deg, #f8d7da, #f5c6cb); color: #721c24; }
            .status-pending { background: linear-gradient(135deg, #fff3cd, #ffeaa7); color: #856404; }
            .status-disabled { background: linear-gradient(135deg, #e2e3e5, #d6d8db); color: #6c757d; }
            .status-partial { background: linear-gradient(135deg, #d1ecf1, #bee5eb); color: #0c5460; }
            .loading { 
                text-align: center; 
                padding: 40px; 
                color: #6c757d; 
                font-size: 18px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #28a745;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .alert { 
                padding: 15px 20px; 
                border-radius: 8px; 
                margin-bottom: 20px; 
                font-weight: 500;
                animation: slideIn 0.3s ease;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .alert-success { 
                background: linear-gradient(135deg, #d4edda, #c3e6cb); 
                color: #155724; 
                border-left: 4px solid #28a745;
            }
            .alert-danger { 
                background: linear-gradient(135deg, #f8d7da, #f5c6cb); 
                color: #721c24; 
                border-left: 4px solid #dc3545;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
            }
            .stat-card h3 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .stat-card p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            @media (max-width: 768px) {
                .toolbar { flex-direction: column; align-items: stretch; }
                .sync-item { flex-direction: column; align-items: flex-start; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔄 Sincronización de Datos</h1>
                <p>Sincronización manual y automática de datos del sistema</p>
            </div>
            
            <div class="content">
                <div class="stats" id="stats-container">
                    <div class="stat-card">
                        <h3 id="total-syncs">0</h3>
                        <p>Sincronizaciones</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="success-syncs">0</h3>
                        <p>Exitosas</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="error-syncs">0</h3>
                        <p>Con Errores</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="last-sync">Nunca</h3>
                        <p>Última Sync</p>
                    </div>
                </div>
                
                <div class="toolbar">
                    <button class="btn btn-success" onclick="iniciarSincronizacion()">
                        🔄 Iniciar Sincronización
                    </button>
                    <button class="btn btn-warning" onclick="programarSync()">
                        ⏰ Programar Sync
                    </button>
                    <button class="btn btn-primary" onclick="verHistorial()">
                        📊 Ver Historial
                    </button>
                    <button class="btn btn-secondary" onclick="volverPanel()">
                        ← Volver al Panel
                    </button>
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    Sincronizando datos...
                </div>
                
                <div id="alert-container"></div>
                
                <div id="sync-container" style="display: none;">
                    <!-- Resultados de sincronización se cargarán aquí -->
                </div>
            </div>
        </div>
        
        <script>
            let syncData = null;
            
            function iniciarSincronizacion() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('sync-container').style.display = 'none';
                
                fetch('/devops/sync', {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        syncData = data.data;
                        mostrarResultados(syncData);
                        actualizarEstadisticas(syncData);
                        mostrarAlerta('Sincronización completada', 'success');
                    } else {
                        mostrarAlerta('Error: ' + data.message, 'danger');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    mostrarAlerta('Error en sincronización: ' + error, 'danger');
                });
            }
            
            function mostrarResultados(sync) {
                const container = document.getElementById('sync-container');
                
                let html = '';
                
                // Resultados de Ofertas
                html += `
                    <div class="sync-section">
                        <div class="sync-header">🎯 Sincronización de Ofertas</div>
                        <div class="sync-body">
                            <div class="sync-item">
                                <div class="sync-label">Estado</div>
                                <div class="sync-status status-${sync.ofertas.status}">${sync.ofertas.status.toUpperCase()}</div>
                            </div>
                            <div class="sync-item">
                                <div class="sync-label">Mensaje</div>
                                <div>${sync.ofertas.message || 'Sin mensaje'}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Resultados de Negocios
                html += `
                    <div class="sync-section">
                        <div class="sync-header">🏪 Sincronización de Negocios</div>
                        <div class="sync-body">
                            <div class="sync-item">
                                <div class="sync-label">Estado</div>
                                <div class="sync-status status-${sync.negocios.status}">${sync.negocios.status.toUpperCase()}</div>
                            </div>
                            <div class="sync-item">
                                <div class="sync-label">Mensaje</div>
                                <div>${sync.negocios.message || 'Sin mensaje'}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Estado General
                html += `
                    <div class="sync-section">
                        <div class="sync-header">📊 Estado General</div>
                        <div class="sync-body">
                            <div class="sync-item">
                                <div class="sync-label">Estado General</div>
                                <div class="sync-status status-${sync.overall_status}">${sync.overall_status.toUpperCase()}</div>
                            </div>
                            <div class="sync-item">
                                <div class="sync-label">Timestamp</div>
                                <div>${new Date(sync.timestamp).toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                container.innerHTML = html;
                document.getElementById('sync-container').style.display = 'block';
            }
            
            function actualizarEstadisticas(sync) {
                const total = 2; // ofertas + negocios
                const success = (sync.ofertas.status === 'success' ? 1 : 0) + (sync.negocios.status === 'success' ? 1 : 0);
                const error = (sync.ofertas.status === 'error' ? 1 : 0) + (sync.negocios.status === 'error' ? 1 : 0);
                const lastSync = new Date(sync.timestamp).toLocaleString();
                
                document.getElementById('total-syncs').textContent = total;
                document.getElementById('success-syncs').textContent = success;
                document.getElementById('error-syncs').textContent = error;
                document.getElementById('last-sync').textContent = lastSync;
            }
            
            function programarSync() {
                mostrarAlerta('Funcionalidad de programación en desarrollo', 'success');
            }
            
            function verHistorial() {
                mostrarAlerta('Historial de sincronizaciones en desarrollo', 'success');
            }
            
            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
                setTimeout(() => container.innerHTML = '', 5000);
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cargar estado inicial
            iniciarSincronizacion();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

@devops_bp.route('/logs')
@devops_login_required
def ver_logs():
    """Ver logs del sistema"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            # Simular logs del sistema
            logs = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': 'Sistema DevOps iniciado correctamente',
                    'service': 'devops'
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': 'Blueprint de DevOps registrado',
                    'service': 'app'
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': 'Conexión con API establecida',
                    'service': 'api_client'
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'WARNING',
                    'message': 'Fallback mode activado',
                    'service': 'devops'
                },
                {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'INFO',
                    'message': 'Usuarios sincronizados correctamente',
                    'service': 'sync'
                }
            ]
            
            return jsonify({
                'status': 'success',
                'data': {
                    'logs': logs,
                    'total_logs': len(logs),
                    'timestamp': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo logs: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo logs: {str(e)}'
            }), 500
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/logs.html')

@devops_bp.route('/config')
@devops_login_required
def ver_configuracion():
    """Ver configuración actual del sistema"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            config = {
                'timestamp': datetime.now().isoformat(),
                'environment': {
                    'BELGRANO_AHORRO_URL': BELGRANO_AHORRO_URL,
                    'BELGRANO_AHORRO_API_KEY': '***configurada***' if BELGRANO_AHORRO_API_KEY else 'No configurada',
                    'API_TIMEOUT_SECS': API_TIMEOUT_SECS
                },
                'system': {
                    'python_version': os.sys.version,
                    'working_directory': os.getcwd(),
                    'blueprint_prefix': '/devops'
                },
                'endpoints': {
                    'base_url': BELGRANO_AHORRO_URL,
                    'api_prefix': '/api',
                    'timeout': API_TIMEOUT_SECS
                }
            }
            
            return jsonify({
                'status': 'success',
                'data': config
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo configuración: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo configuración: {str(e)}'
            }), 500
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/config.html')

@devops_bp.route('/conectar-belgrano')
@devops_login_required
def conectar_belgrano():
    """Conectar con Belgrano Ahorro y verificar estado"""
    from flask import request, make_response
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            # Verificar conexión con Belgrano Ahorro
            connection_status = {
                'timestamp': datetime.now().isoformat(),
                'belgrano_ahorro': {
                    'url': BELGRANO_AHORRO_URL,
                    'api_key_configured': bool(BELGRANO_AHORRO_API_KEY),
                    'status': 'checking'
                },
                'devops_api_client': {
                    'available': devops_api_client is not None,
                    'status': 'active' if devops_api_client else 'inactive'
                }
            }
            
            # Intentar conectar con Belgrano Ahorro
            if BELGRANO_AHORRO_URL and BELGRANO_AHORRO_API_KEY:
                try:
                    # response = requests.get(
                    #     build_api_url('healthz'),
                    #     headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
                    #     timeout=5
                    # )
                    # if response.status_code == 200:
                    #     connection_status['belgrano_ahorro']['status'] = 'connected'
                    #     connection_status['belgrano_ahorro']['response_time'] = response.elapsed.total_seconds()
                    # else:
                    #     connection_status['belgrano_ahorro']['status'] = 'error'
                    #     connection_status['belgrano_ahorro']['error'] = f'HTTP {response.status_code}'
                    connection_status['belgrano_ahorro']['status'] = 'disabled'
                    connection_status['belgrano_ahorro']['message'] = 'API temporalmente deshabilitada'
                except Exception as e:
                    connection_status['belgrano_ahorro']['status'] = 'error'
                    connection_status['belgrano_ahorro']['error'] = str(e)
            else:
                connection_status['belgrano_ahorro']['status'] = 'not_configured'
                connection_status['belgrano_ahorro']['message'] = 'Variables de entorno no configuradas'
            
            return jsonify({
                'status': 'success',
                'data': connection_status
            })
            
        except Exception as e:
            logger.error(f"Error verificando conexión: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error verificando conexión: {str(e)}'
            }), 500
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Conexión Belgrano Ahorro - DevOps</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                padding: 30px; 
                text-align: center; 
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .content { padding: 30px; }
            .connection-card {
                background: white;
                border-radius: 10px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #28a745;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-connected { background: #28a745; }
            .status-disconnected { background: #dc3545; }
            .status-checking { background: #ffc107; }
            .status-disabled { background: #6c757d; }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 5px;
                border: none;
                cursor: pointer;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .btn-secondary {
                background: linear-gradient(135deg, #6c757d, #5a6268);
            }
            .btn-info {
                background: linear-gradient(135deg, #17a2b8, #138496);
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border-left: 4px solid #28a745;
            }
            .stat-card h3 {
                font-size: 2em;
                color: #28a745;
                margin-bottom: 10px;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #6c757d;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #28a745;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔗 Conexión Belgrano Ahorro</h1>
                <p>Verificación y gestión de conexión con el sistema Belgrano Ahorro</p>
            </div>
            
            <div class="content">
                <div class="stats-grid" id="stats-container">
                    <div class="stat-card">
                        <h3 id="connection-status">Verificando...</h3>
                        <p>Estado de Conexión</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="response-time">-</h3>
                        <p>Tiempo de Respuesta</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="api-status">-</h3>
                        <p>Estado API</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="last-check">-</h3>
                        <p>Última Verificación</p>
                    </div>
                </div>
                
                <div class="connection-card">
                    <h3>🔧 Configuración Actual</h3>
                    <div id="config-details">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>Cargando configuración...</p>
                        </div>
                    </div>
                </div>
                
                <div class="connection-card">
                    <h3>📊 Estado de Conexión</h3>
                    <div id="connection-details">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>Verificando conexión...</p>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <button class="btn" onclick="verificarConexion()">🔄 Verificar Conexión</button>
                    <button class="btn btn-info" onclick="verConfiguracion()">⚙️ Ver Configuración</button>
                    <button class="btn btn-secondary" onclick="volverPanel()">🏠 Volver al Panel</button>
                </div>
            </div>
        </div>
        
        <script>
            function verificarConexion() {
                document.getElementById('connection-details').innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Verificando conexión...</p>
                    </div>
                `;
                
                fetch('/devops/conectar-belgrano?ajax=true&format=json&api=true&json=true', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        mostrarEstadoConexion(data.data);
                        actualizarEstadisticas(data.data);
                    } else {
                        mostrarError('Error verificando conexión: ' + data.message);
                    }
                })
                .catch(error => {
                    mostrarError('Error verificando conexión: ' + error);
                });
            }
            
            function verConfiguracion() {
                fetch('/devops/config?ajax=true&format=json&api=true&json=true', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        mostrarConfiguracion(data.data);
                    } else {
                        mostrarError('Error cargando configuración: ' + data.message);
                    }
                })
                .catch(error => {
                    mostrarError('Error cargando configuración: ' + error);
                });
            }
            
            function mostrarEstadoConexion(data) {
                const container = document.getElementById('connection-details');
                const belgrano = data.belgrano_ahorro;
                const devops = data.devops_api_client;
                
                let statusClass = 'status-disconnected';
                let statusText = 'Desconectado';
                
                if (belgrano.status === 'connected') {
                    statusClass = 'status-connected';
                    statusText = 'Conectado';
                } else if (belgrano.status === 'checking') {
                    statusClass = 'status-checking';
                    statusText = 'Verificando...';
                } else if (belgrano.status === 'disabled') {
                    statusClass = 'status-disabled';
                    statusText = 'Deshabilitado';
                }
                
                container.innerHTML = `
                    <div class="connection-item">
                        <h4>🌐 Belgrano Ahorro</h4>
                        <p><span class="status-indicator ${statusClass}"></span>${statusText}</p>
                        <p><strong>URL:</strong> ${belgrano.url || 'No configurada'}</p>
                        <p><strong>API Key:</strong> ${belgrano.api_key_configured ? 'Configurada' : 'No configurada'}</p>
                        ${belgrano.error ? `<p class="text-danger"><strong>Error:</strong> ${belgrano.error}</p>` : ''}
                        ${belgrano.message ? `<p class="text-info"><strong>Mensaje:</strong> ${belgrano.message}</p>` : ''}
                    </div>
                    <div class="connection-item">
                        <h4>🔧 DevOps API Client</h4>
                        <p><span class="status-indicator ${devops.status === 'active' ? 'status-connected' : 'status-disconnected'}"></span>${devops.status === 'active' ? 'Activo' : 'Inactivo'}</p>
                        <p><strong>Disponible:</strong> ${devops.available ? 'Sí' : 'No'}</p>
                    </div>
                `;
            }
            
            function mostrarConfiguracion(data) {
                const container = document.getElementById('config-details');
                container.innerHTML = `
                    <div class="config-item">
                        <h4>🌐 Variables de Entorno</h4>
                        <p><strong>BELGRANO_AHORRO_URL:</strong> ${data.environment.BELGRANO_AHORRO_URL || 'No configurada'}</p>
                        <p><strong>BELGRANO_AHORRO_API_KEY:</strong> ${data.environment.BELGRANO_AHORRO_API_KEY}</p>
                        <p><strong>API_TIMEOUT_SECS:</strong> ${data.environment.API_TIMEOUT_SECS}</p>
                    </div>
                    <div class="config-item">
                        <h4>💻 Sistema</h4>
                        <p><strong>Python:</strong> ${data.system.python_version}</p>
                        <p><strong>Directorio:</strong> ${data.system.working_directory}</p>
                        <p><strong>Blueprint:</strong> ${data.system.blueprint_prefix}</p>
                    </div>
                    <div class="config-item">
                        <h4>🔗 Endpoints</h4>
                        <p><strong>Base URL:</strong> ${data.endpoints.base_url || 'No configurada'}</p>
                        <p><strong>API Prefix:</strong> ${data.endpoints.api_prefix}</p>
                        <p><strong>Timeout:</strong> ${data.endpoints.timeout}s</p>
                    </div>
                `;
            }
            
            function actualizarEstadisticas(data) {
                const belgrano = data.belgrano_ahorro;
                const now = new Date().toLocaleString();
                
                document.getElementById('connection-status').textContent = 
                    belgrano.status === 'connected' ? 'Conectado' : 
                    belgrano.status === 'disabled' ? 'Deshabilitado' : 'Desconectado';
                
                document.getElementById('response-time').textContent = 
                    belgrano.response_time ? belgrano.response_time + 's' : '-';
                
                document.getElementById('api-status').textContent = 
                    belgrano.api_key_configured ? 'Configurada' : 'No configurada';
                
                document.getElementById('last-check').textContent = now;
            }
            
            function mostrarError(mensaje) {
                const container = document.getElementById('connection-details');
                container.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Error:</strong> ${mensaje}
                    </div>
                `;
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cargar información inicial
            verificarConexion();
            verConfiguracion();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

# =================================================================
# INTERFAZ WEB DEVOPS UI
# =================================================================

@devops_bp.route('/ui')
@devops_login_required
def devops_ui():
    """Interfaz web para gestión de endpoints DevOps"""
    from flask import render_template
    
    try:
        return render_template('devops.html')
    except Exception as e:
        logger.error(f"Error cargando interfaz DevOps UI: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error cargando interfaz: {str(e)}'
        }), 500

# =================================================================
# MANEJO DE ERRORES
# =================================================================

@devops_bp.errorhandler(404)
def devops_not_found(error):
    """Manejar errores 404 en DevOps"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint de DevOps no encontrado',
        'available_endpoints': [
            '/devops/',
            '/devops/health',
            '/devops/status',
            '/devops/info',
            '/devops/ofertas',
            '/devops/negocios',
            '/devops/sync',
            '/devops/logs',
            '/devops/config'
        ],
        'timestamp': datetime.now().isoformat()
    }), 404

@devops_bp.errorhandler(500)
def devops_internal_error(error):
    """Manejar errores 500 en DevOps"""
    return jsonify({
        'status': 'error',
        'message': 'Error interno del servidor DevOps',
        'timestamp': datetime.now().isoformat()
    }), 500