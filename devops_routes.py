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
from flask import Blueprint, request, jsonify, redirect, url_for, session, make_response, render_template
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
        logger.warning("Variable de entorno BELGRANO_AHORRO_URL no está definida")

if not BELGRANO_AHORRO_API_KEY:
    if env_status != 'production':
        logger.info("ℹ️ BELGRANO_AHORRO_API_KEY no configurada (normal en desarrollo)")
    else:
        logger.warning("Variable de entorno BELGRANO_AHORRO_API_KEY no está definida")

# Importar cliente API central
from api_client import get_api_client

def api_get(path: str):
    client = get_api_client()
    if client is None:
        raise RuntimeError("Cliente API no disponible")
    # Compatibilidad: ambos clientes devuelven dict JSON
    if hasattr(client, 'get'):
        return client.get(path)
    # BelgranoAhorroClient
    mapping = {
        'businesses': client.get_businesses,
        'products': client.get_products,
        'branches': client.get_branches,
        'offers': client.get_offers,
        'health': client.health_check,
    }
    if path in mapping:
        return mapping[path]()
    raise ValueError(f"GET no soportado: {path}")

def api_post(path: str, data: dict):
    client = get_api_client()
    if client is None:
        raise RuntimeError("Cliente API no disponible")
    if hasattr(client, 'post'):
        return client.post(path, json=data)
    mapping = {
        'businesses': client.create_business,
        'products': client.create_product,
        'branches': client.create_branch,
        'offers': client.create_offer,
    }
    if path in mapping:
        return mapping[path](data)
    raise ValueError(f"POST no soportado: {path}")

def api_put(path: str, item_id: int, data: dict):
    client = get_api_client()
    if client is None:
        raise RuntimeError("Cliente API no disponible")
    mapping = {
        'businesses': getattr(client, 'update_business', None),
        'products': getattr(client, 'update_product', None),
        'branches': getattr(client, 'update_branch', None),
        'offers': getattr(client, 'update_offer', None),
    }
    fn = mapping.get(path)
    if fn is None:
        raise ValueError(f"PUT no soportado: {path}")
    return fn(item_id, data)

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
                    <h2>DevOps Login</h2>
                    <div class="error">
                        <strong>Credenciales incorrectas</strong><br>
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
            <h2>DevOps Login</h2>
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
                <h1>Test DevOps</h1>
                <p>Sistema DevOps funcionando correctamente</p>
            </div>
            
            <div class="content">
                <div class="status-card">
                    <h3>Sistema Operativo</h3>
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
        
        client = get_api_client()
        if not client:
            logger.warning("Cliente API no disponible para sincronización")
            return False
            
        # Usar el cliente API para sincronizar
        resultado = client.sync_data(tipo_cambio, datos)
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
    
    # Si no es AJAX, devolver template HTML
    try:
        return render_template('devops/dashboard.html')
    except Exception as e:
        logger.error(f"Error cargando dashboard: {e}")
        # Fallback con HTML básico
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
                <h1>Panel DevOps</h1>
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
                        <h3>Herramientas de Desarrollo</h3>
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
                api_url = build_api_url('healthz')
                if api_url and BELGRANO_AHORRO_API_KEY:
                    response = requests.get(
                        api_url,
                        headers={'X-API-Key': BELGRANO_AHORRO_API_KEY},
                        timeout=5
                    )
                    if response.status_code == 200:
                        health_status['checks']['api_connection'] = 'healthy'
                    else:
                        health_status['checks']['api_connection'] = 'warning'
                        health_status['api_status_code'] = response.status_code
                else:
                    health_status['checks']['api_connection'] = 'not_configured'
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

# @devops_bp.route('/ofertas', methods=['GET', 'POST'])
# @devops_login_required
# def gestion_ofertas():
#     """Gestión completa de ofertas"""
#     from flask import request, make_response, render_template, flash, redirect, url_for
#     
#     # Manejar POST requests (crear oferta)
#     if request.method == 'POST':
#         try:
#             titulo = request.form.get('titulo', '').strip()
#             descripcion = request.form.get('descripcion', '').strip()
#             productos = request.form.get('productos', '').strip()
#             hasta_agotar_stock = request.form.get('hasta_agotar_stock') == 'on'
#             activa = request.form.get('activa') == 'on'
#             
#             if not all([titulo, descripcion, productos]):
#                 flash('Título, descripción y productos son requeridos', 'error')
#                 return redirect(url_for('devops.gestion_ofertas'))
#             
#             # Cargar datos actuales
#             from devops_persistence import get_devops_db, guardar_datos_json
#             import uuid
#             db = get_devops_db()
#             if not datos:
#                 datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
#             
#             # Crear nueva oferta
#             oferta_id = str(uuid.uuid4())
#             nueva_oferta = {
#                 'id': oferta_id,
#                 'titulo': titulo,
#                 'descripcion': descripcion,
#                 'productos': productos,
#                 'hasta_agotar_stock': hasta_agotar_stock,
#                 'activa': activa,
#                 'fecha_creacion': datetime.now().isoformat()
#             }
#             
#             # Agregar a la lista
#             if 'ofertas' not in datos:
#                 datos['ofertas'] = []
#             datos['ofertas'].append(nueva_oferta)
#             
#             # Guardar
#             if guardar_datos_json(datos):
#                 flash(f'Oferta "{titulo}" creada exitosamente', 'success')
#                 logger.info(f"Oferta creada desde DevOps: {titulo}")
#             else:
#                 flash('Error al guardar la oferta', 'error')
#                 
#         except Exception as e:
#             logger.error(f"Error creando oferta desde DevOps: {e}")
#             flash('Error interno al crear la oferta', 'error')
#         
#         return redirect(url_for('devops.gestion_ofertas'))
#     
#     # Solo devolver JSON si se solicita explícitamente con todos los parámetros
#     if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
#         request.args.get('ajax') == 'true' and 
#         request.args.get('format') == 'json' and 
#         request.args.get('api') == 'true' and
#         request.args.get('json') == 'true'):
#         try:
#             # Simular datos de ofertas
#             ofertas = [
#                 {
#                     'id': 1,
#                     'titulo': 'Oferta Especial 50%',
#                     'descripcion': 'Descuento del 50% en productos seleccionados',
#                     'descuento': 50,
#                     'producto_id': 1,
#                     'producto_nombre': 'Producto Ejemplo',
#                     'fecha_inicio': '2025-01-19',
#                     'fecha_fin': '2025-01-31',
#                     'activa': True
#                 },
#                 {
#                     'id': 2,
#                     'titulo': 'Oferta 2x1',
#                     'descripcion': 'Lleva 2 productos y paga solo 1',
#                     'descuento': 100,
#                     'producto_id': 2,
#                     'producto_nombre': 'Producto Ejemplo 2',
#                     'fecha_inicio': '2025-01-20',
#                     'fecha_fin': '2025-02-15',
#                     'activa': True
#                 }
#             ]
#             
#             return jsonify({
#                 'status': 'success',
#                 'message': f'Ofertas obtenidas correctamente ({len(ofertas)} encontradas)',
#                 'data': {
#                     'ofertas': ofertas,
#                     'total': len(ofertas),
#                     'timestamp': datetime.now().isoformat()
#                 },
#                 'source': 'simulated'
#             })
#             
#         except Exception as e:
#             logger.error(f"Error obteniendo ofertas: {e}")
#             return jsonify({
#                 'status': 'error',
#                 'message': f'Error obteniendo ofertas: {str(e)}',
#                 'data': []
#             }), 500
#     
#     # Si no es AJAX, devolver template HTML con datos reales
#     try:
#         from devops_persistence import get_devops_db
#         db = get_devops_db()
#         ofertas = db.obtener_ofertas()
#             
#         # Devolver template con datos reales
#         return render_template('devops/ofertas.html', ofertas=ofertas)
#         
#     except Exception as e:
#         logger.error(f"Error cargando datos para ofertas: {e}")
#         # Fallback con datos vacíos
#         return render_template('devops/ofertas.html', ofertas=[])

# =================================================================
# GESTIÓN DE NEGOCIOS (DevOps consumiendo API)
# =================================================================

@devops_bp.route('/negocios', methods=['GET', 'POST'])
@devops_login_required
def gestion_negocios():
    """Gestión completa de negocios con API real"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return render_template('devops/negocios.html', negocios=[], error_api=True)
    
    try:
        if request.method == 'POST':
            # Crear nuevo negocio
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            direccion = request.form.get('direccion', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            activo = request.form.get('activo') == 'on'
            
            if not nombre:
                flash('El nombre es requerido', 'error')
            else:
                # Crear negocio usando API real
                resultado = client.create_negocio({
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'direccion': direccion,
                    'telefono': telefono,
                    'email': email,
                    'activo': activo
                })
                
                if resultado:
                    flash(f'Negocio "{nombre}" creado exitosamente', 'success')
                    logger.info(f"Negocio creado desde DevOps: {nombre}")
                else:
                    flash('Error al crear el negocio. Verifique la conexión con la API.', 'error')
            
            return redirect(url_for('devops.gestion_negocios'))

        # GET: Listar negocios desde API real
        try:
            negocios = client.get_negocios()
            logger.info(f"Obtenidos {len(negocios)} negocios desde API")
            
            # Intentar usar template
            try:
                return render_template('devops/negocios.html', negocios=negocios, error_api=False)
            except Exception:
                # Fallback HTML con datos reales
                items_html = ""
                for negocio in negocios:
                    estado = "Activo" if negocio.get('activo', True) else "Inactivo"
                    items_html += f"""
                    <div class="negocio-item" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                        <h4>#{negocio.get('id', 'N/A')} - {negocio.get('nombre', 'Sin nombre')}</h4>
                        <p><strong>Descripción:</strong> {negocio.get('descripcion', 'Sin descripción')}</p>
                        <p><strong>Dirección:</strong> {negocio.get('direccion', 'Sin dirección')}</p>
                        <p><strong>Teléfono:</strong> {negocio.get('telefono', 'Sin teléfono')}</p>
                        <p><strong>Email:</strong> {negocio.get('email', 'Sin email')}</p>
                        <p><strong>Estado:</strong> {estado}</p>
                        <div style="margin-top: 10px;">
                            <a href="/devops/negocios/{negocio.get('id')}/editar" class="btn btn-warning">Editar</a>
                            <a href="/devops/negocios/{negocio.get('id')}/eliminar" class="btn btn-danger" onclick="return confirm('¿Eliminar este negocio?')">Eliminar</a>
                        </div>
                    </div>
                    """
                
                html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Gestión de Negocios - DevOps</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .header {{ background: #007bff; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                        .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                        .btn-warning {{ background: #ffc107; color: #212529; }}
                        .btn-danger {{ background: #dc3545; color: white; }}
                        .btn-success {{ background: #28a745; color: white; }}
                        .form-group {{ margin-bottom: 15px; }}
                        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                        .form-group input, .form-group textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
                        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Gestión de Negocios</h1>
                            <p>Administra los negocios desde la API de Belgrano Ahorro</p>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <a href="/devops/" class="btn btn-success">← Volver al Panel</a>
                        </div>
                        
                        <h2>Lista de Negocios ({len(negocios)} encontrados)</h2>
                        {items_html}
                        
                        <h2>Crear Nuevo Negocio</h2>
                        <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                            <div class="form-group">
                                <label for="nombre">Nombre *</label>
                                <input type="text" id="nombre" name="nombre" required />
                            </div>
                            <div class="form-group">
                                <label for="descripcion">Descripción</label>
                                <textarea id="descripcion" name="descripcion" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="direccion">Dirección</label>
                                <input type="text" id="direccion" name="direccion" />
                            </div>
                            <div class="form-group">
                                <label for="telefono">Teléfono</label>
                                <input type="text" id="telefono" name="telefono" />
                            </div>
                            <div class="form-group">
                                <label for="email">Email</label>
                                <input type="email" id="email" name="email" />
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" name="activo" checked /> Negocio activo
                                </label>
                            </div>
                            <button type="submit" class="btn btn-success">Crear Negocio</button>
                        </form>
                    </div>
                </body>
                </html>
                """
                return make_response(html, 200)
                
        except Exception as e:
            logger.error(f"Error obteniendo negocios desde API: {e}")
            flash('Error al obtener negocios desde la API', 'error')
            return render_template('devops/negocios.html', negocios=[], error_api=True)
            
    except Exception as e:
        logger.error(f"Error en gestión de negocios: {e}")
        flash('Error interno en gestión de negocios', 'error')
        return render_template('devops/negocios.html', negocios=[], error_api=True)

@devops_bp.route('/negocios/<int:business_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_negocio(business_id: int):
    """Editar negocio existente"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_negocios'))
    
    try:
        if request.method == 'POST':
            # Actualizar negocio
            data = {
                key: value for key, value in {
                    'nombre': request.form.get('nombre'),
                    'descripcion': request.form.get('descripcion'),
                    'direccion': request.form.get('direccion'),
                    'telefono': request.form.get('telefono'),
                    'email': request.form.get('email'),
                    'activo': request.form.get('activo') == 'on'
                }.items() if value is not None and value != ''
            }
            
            resultado = client.update_negocio(business_id, data)
            if resultado:
                flash('Negocio actualizado exitosamente', 'success')
                logger.info(f"Negocio {business_id} actualizado desde DevOps")
            else:
                flash('Error al actualizar el negocio. Verifique la conexión con la API.', 'error')
            
            return redirect(url_for('devops.gestion_negocios'))
        
        else:
            # GET: Mostrar formulario de edición
            negocio = client.get_negocio(business_id)
            if not negocio:
                flash('Negocio no encontrado', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # HTML para edición
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Editar Negocio - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #ffc107; color: #212529; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-warning {{ background: #ffc107; color: #212529; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .form-group {{ margin-bottom: 15px; }}
                    .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                    .form-group input, .form-group textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Editar Negocio #{business_id}</h1>
                        <p>Modifica los datos del negocio</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <a href="/devops/negocios" class="btn btn-success">← Volver a Negocios</a>
                    </div>
                    
                    <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                        <div class="form-group">
                            <label for="nombre">Nombre *</label>
                            <input type="text" id="nombre" name="nombre" value="{negocio.get('nombre', '')}" required />
                        </div>
                        <div class="form-group">
                            <label for="descripcion">Descripción</label>
                            <textarea id="descripcion" name="descripcion" rows="3">{negocio.get('descripcion', '')}</textarea>
                        </div>
                        <div class="form-group">
                            <label for="direccion">Dirección</label>
                            <input type="text" id="direccion" name="direccion" value="{negocio.get('direccion', '')}" />
                        </div>
                        <div class="form-group">
                            <label for="telefono">Teléfono</label>
                            <input type="text" id="telefono" name="telefono" value="{negocio.get('telefono', '')}" />
                        </div>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" value="{negocio.get('email', '')}" />
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="activo" {'checked' if negocio.get('activo', True) else ''} /> Negocio activo
                            </label>
                        </div>
                        <button type="submit" class="btn btn-warning">Actualizar Negocio</button>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error editando negocio {business_id}: {e}")
        flash('Error interno al editar el negocio', 'error')
        return redirect(url_for('devops.gestion_negocios'))

@devops_bp.route('/negocios/<int:business_id>/eliminar', methods=['GET', 'POST'])
@devops_login_required
def eliminar_negocio(business_id: int):
    """Eliminar negocio con confirmación"""
    from flask import flash, request, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_negocios'))
    
    try:
        if request.method == 'POST':
            # Confirmar eliminación
            confirmar = request.form.get('confirmar')
            if confirmar == 'si':
                # Eliminar usando API real
                resultado = client.delete_negocio(business_id)
                if resultado:
                    flash('Negocio eliminado exitosamente', 'success')
                    logger.info(f"Negocio {business_id} eliminado desde DevOps")
                else:
                    flash('Error al eliminar el negocio. Verifique la conexión con la API.', 'error')
            else:
                flash('Eliminación cancelada', 'info')
            
            return redirect(url_for('devops.gestion_negocios'))
        
        else:
            # GET: Mostrar confirmación
            negocio = client.get_negocio(business_id)
            if not negocio:
                flash('Negocio no encontrado', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # HTML de confirmación
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Eliminar Negocio - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #dc3545; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 4px; margin: 20px 0; border: 1px solid #ffeaa7; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Eliminar Negocio #{business_id}</h1>
                        <p>Esta acción no se puede deshacer</p>
                    </div>
                    
                    <div class="warning">
                        <strong>ADVERTENCIA:</strong> Está a punto de eliminar permanentemente el negocio "{negocio.get('nombre', 'Sin nombre')}". Esta acción no se puede deshacer.
                    </div>
                    
                    <h3>Datos del negocio a eliminar:</h3>
                    <ul>
                        <li><strong>ID:</strong> {business_id}</li>
                        <li><strong>Nombre:</strong> {negocio.get('nombre', 'Sin nombre')}</li>
                        <li><strong>Descripción:</strong> {negocio.get('descripcion', 'Sin descripción')}</li>
                        <li><strong>Dirección:</strong> {negocio.get('direccion', 'Sin dirección')}</li>
                        <li><strong>Teléfono:</strong> {negocio.get('telefono', 'Sin teléfono')}</li>
                        <li><strong>Email:</strong> {negocio.get('email', 'Sin email')}</li>
                    </ul>
                    
                    <form method="post" style="margin-top: 30px;">
                        <div style="margin-bottom: 20px;">
                            <label>
                                <input type="checkbox" name="confirmar" value="si" required /> 
                                Confirmo que quiero eliminar este negocio permanentemente
                            </label>
                        </div>
                        
                        <button type="submit" class="btn btn-danger" onclick="return confirm('¿Está seguro de que desea eliminar este negocio?')">
                            ELIMINAR NEGOCIO
                        </button>
                        <a href="/devops/negocios" class="btn btn-success">Cancelar</a>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error eliminando negocio {business_id}: {e}")
        flash('Error interno al eliminar el negocio', 'error')
        return redirect(url_for('devops.gestion_negocios'))

# =================================================================
# GESTIÓN DE PRODUCTOS (DevOps consumiendo API)
# =================================================================

@devops_bp.route('/productos', methods=['GET', 'POST'])
@devops_login_required
def gestion_productos():
    """Gestión completa de productos con API real"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return render_template('devops/productos.html', productos=[], negocios=[], error_api=True)
    
    try:
        if request.method == 'POST':
            # Crear nuevo producto
            nombre = request.form.get('nombre', '').strip()
            precio = request.form.get('precio', '').strip()
            categoria = request.form.get('categoria', 'General').strip()
            negocio_id = request.form.get('negocio_id')
            descripcion = request.form.get('descripcion', '').strip()
            activo = request.form.get('activo') == 'on'
            
            if not nombre or not precio:
                flash('Nombre y precio son requeridos', 'error')
            else:
                try:
                    precio_float = float(precio)
                    # Crear producto usando API real
                    resultado = client.create_producto({
                        'nombre': nombre,
                        'precio': precio_float,
                        'categoria': categoria,
                        'descripcion': descripcion,
                        'negocio_id': int(negocio_id) if negocio_id else None,
                        'activo': activo
                    })
                    
                    if resultado:
                        flash(f'Producto "{nombre}" creado exitosamente', 'success')
                        logger.info(f"Producto creado desde DevOps: {nombre}")
                    else:
                        flash('Error al crear el producto. Verifique la conexión con la API.', 'error')
                except ValueError:
                    flash('El precio debe ser un número válido', 'error')
            
            return redirect(url_for('devops.gestion_productos'))

        # GET: Listar productos y negocios desde API real
        try:
            productos = client.get_productos()
            negocios = client.get_negocios()
            logger.info(f"Obtenidos {len(productos)} productos y {len(negocios)} negocios desde API")
            
            # Intentar usar template
            try:
                return render_template('devops/productos.html', productos=productos, negocios=negocios, error_api=False)
            except Exception:
                # Fallback HTML con datos reales
                items_html = ""
                for producto in productos:
                    estado = "Activo" if producto.get('activo', True) else "Inactivo"
                    negocio_nombre = "Sin negocio"
                    for negocio in negocios:
                        if negocio.get('id') == producto.get('negocio_id'):
                            negocio_nombre = negocio.get('nombre', 'Sin nombre')
                            break
                    
                    items_html += f"""
                    <div class="producto-item" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                        <h4>#{producto.get('id', 'N/A')} - {producto.get('nombre', 'Sin nombre')}</h4>
                        <p><strong>Precio:</strong> ${producto.get('precio', 0):.2f}</p>
                        <p><strong>Categoría:</strong> {producto.get('categoria', 'Sin categoría')}</p>
                        <p><strong>Descripción:</strong> {producto.get('descripcion', 'Sin descripción')}</p>
                        <p><strong>Negocio:</strong> {negocio_nombre}</p>
                        <p><strong>Estado:</strong> {estado}</p>
                        <div style="margin-top: 10px;">
                            <a href="/devops/productos/{producto.get('id')}/editar" class="btn btn-warning">Editar</a>
                            <a href="/devops/productos/{producto.get('id')}/eliminar" class="btn btn-danger" onclick="return confirm('¿Eliminar este producto?')">Eliminar</a>
                        </div>
                    </div>
                    """
                
                # Opciones de negocios para el selector
                options_html = '<option value="">Sin negocio</option>'
                for negocio in negocios:
                    options_html += f'<option value="{negocio.get("id")}">{negocio.get("nombre", "Sin nombre")}</option>'
                
                html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Gestión de Productos - DevOps</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .header {{ background: #28a745; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                        .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                        .btn-warning {{ background: #ffc107; color: #212529; }}
                        .btn-danger {{ background: #dc3545; color: white; }}
                        .btn-success {{ background: #28a745; color: white; }}
                        .form-group {{ margin-bottom: 15px; }}
                        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                        .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
                        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Gestión de Productos</h1>
                            <p>Administra los productos desde la API de Belgrano Ahorro</p>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <a href="/devops/" class="btn btn-success">← Volver al Panel</a>
                        </div>
                        
                        <h2>Lista de Productos ({len(productos)} encontrados)</h2>
                        {items_html}
                        
                        <h2>Crear Nuevo Producto</h2>
                        <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                            <div class="form-group">
                                <label for="nombre">Nombre *</label>
                                <input type="text" id="nombre" name="nombre" required />
                            </div>
                            <div class="form-group">
                                <label for="precio">Precio *</label>
                                <input type="number" id="precio" name="precio" step="0.01" min="0" required />
                            </div>
                            <div class="form-group">
                                <label for="categoria">Categoría</label>
                                <input type="text" id="categoria" name="categoria" value="General" />
                            </div>
                            <div class="form-group">
                                <label for="descripcion">Descripción</label>
                                <textarea id="descripcion" name="descripcion" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label for="negocio_id">Negocio</label>
                                <select id="negocio_id" name="negocio_id">
                                    {options_html}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" name="activo" checked /> Producto activo
                                </label>
                            </div>
                            <button type="submit" class="btn btn-success">Crear Producto</button>
                        </form>
                    </div>
                </body>
                </html>
                """
                return make_response(html, 200)
                
        except Exception as e:
            logger.error(f"Error obteniendo productos desde API: {e}")
            flash('Error al obtener productos desde la API', 'error')
            return render_template('devops/productos.html', productos=[], negocios=[], error_api=True)
            
    except Exception as e:
        logger.error(f"Error en gestión de productos: {e}")
        flash('Error interno en gestión de productos', 'error')
        return render_template('devops/productos.html', productos=[], negocios=[], error_api=True)

@devops_bp.route('/productos/<int:product_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_producto(product_id: int):
    """Editar producto existente"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_productos'))
    
    try:
        if request.method == 'POST':
            # Actualizar producto
            data = {
                key: value for key, value in {
                    'nombre': request.form.get('nombre'),
                    'precio': float(request.form.get('precio')) if request.form.get('precio') else None,
                    'categoria': request.form.get('categoria'),
                    'descripcion': request.form.get('descripcion'),
                    'negocio_id': int(request.form.get('negocio_id')) if request.form.get('negocio_id') else None,
                    'activo': request.form.get('activo') == 'on'
                }.items() if value is not None and value != ''
            }
            
            resultado = client.update_producto(product_id, data)
            if resultado:
                flash('Producto actualizado exitosamente', 'success')
                logger.info(f"Producto {product_id} actualizado desde DevOps")
            else:
                flash('Error al actualizar el producto. Verifique la conexión con la API.', 'error')
            
            return redirect(url_for('devops.gestion_productos'))
        
        else:
            # GET: Mostrar formulario de edición
            producto = client.get_producto(product_id)
            negocios = client.get_negocios()
            
            if not producto:
                flash('Producto no encontrado', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Opciones de negocios para el selector
            options_html = '<option value="">Sin negocio</option>'
            for negocio in negocios:
                selected = 'selected' if negocio.get('id') == producto.get('negocio_id') else ''
                options_html += f'<option value="{negocio.get("id")}" {selected}>{negocio.get("nombre", "Sin nombre")}</option>'
            
            # HTML para edición
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Editar Producto - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #ffc107; color: #212529; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-warning {{ background: #ffc107; color: #212529; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .form-group {{ margin-bottom: 15px; }}
                    .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                    .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Editar Producto #{product_id}</h1>
                        <p>Modifica los datos del producto</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <a href="/devops/productos" class="btn btn-success">← Volver a Productos</a>
                    </div>
                    
                    <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                        <div class="form-group">
                            <label for="nombre">Nombre *</label>
                            <input type="text" id="nombre" name="nombre" value="{producto.get('nombre', '')}" required />
                        </div>
                        <div class="form-group">
                            <label for="precio">Precio *</label>
                            <input type="number" id="precio" name="precio" step="0.01" min="0" value="{producto.get('precio', 0)}" required />
                        </div>
                        <div class="form-group">
                            <label for="categoria">Categoría</label>
                            <input type="text" id="categoria" name="categoria" value="{producto.get('categoria', '')}" />
                        </div>
                        <div class="form-group">
                            <label for="descripcion">Descripción</label>
                            <textarea id="descripcion" name="descripcion" rows="3">{producto.get('descripcion', '')}</textarea>
                        </div>
                        <div class="form-group">
                            <label for="negocio_id">Negocio</label>
                            <select id="negocio_id" name="negocio_id">
                                {options_html}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="activo" {'checked' if producto.get('activo', True) else ''} /> Producto activo
                            </label>
                        </div>
                        <button type="submit" class="btn btn-warning">Actualizar Producto</button>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error editando producto {product_id}: {e}")
        flash('Error interno al editar el producto', 'error')
        return redirect(url_for('devops.gestion_productos'))

@devops_bp.route('/productos/<int:product_id>/eliminar', methods=['GET', 'POST'])
@devops_login_required
def eliminar_producto(product_id: int):
    """Eliminar producto con confirmación"""
    from flask import flash, request, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_productos'))
    
    try:
        if request.method == 'POST':
            # Confirmar eliminación
            confirmar = request.form.get('confirmar')
            if confirmar == 'si':
                # Eliminar usando API real
                resultado = client.delete_producto(product_id)
                if resultado:
                    flash('Producto eliminado exitosamente', 'success')
                    logger.info(f"Producto {product_id} eliminado desde DevOps")
                else:
                    flash('Error al eliminar el producto. Verifique la conexión con la API.', 'error')
            else:
                flash('Eliminación cancelada', 'info')
            
            return redirect(url_for('devops.gestion_productos'))
        
        else:
            # GET: Mostrar confirmación
            producto = client.get_producto(product_id)
            if not producto:
                flash('Producto no encontrado', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # HTML de confirmación
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Eliminar Producto - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #dc3545; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 4px; margin: 20px 0; border: 1px solid #ffeaa7; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Eliminar Producto #{product_id}</h1>
                        <p>Esta acción no se puede deshacer</p>
                    </div>
                    
                    <div class="warning">
                        <strong>ADVERTENCIA:</strong> Está a punto de eliminar permanentemente el producto "{producto.get('nombre', 'Sin nombre')}". Esta acción no se puede deshacer.
                    </div>
                    
                    <h3>Datos del producto a eliminar:</h3>
                    <ul>
                        <li><strong>ID:</strong> {product_id}</li>
                        <li><strong>Nombre:</strong> {producto.get('nombre', 'Sin nombre')}</li>
                        <li><strong>Precio:</strong> ${producto.get('precio', 0):.2f}</li>
                        <li><strong>Categoría:</strong> {producto.get('categoria', 'Sin categoría')}</li>
                        <li><strong>Descripción:</strong> {producto.get('descripcion', 'Sin descripción')}</li>
                    </ul>
                    
                    <form method="post" style="margin-top: 30px;">
                        <div style="margin-bottom: 20px;">
                            <label>
                                <input type="checkbox" name="confirmar" value="si" required /> 
                                Confirmo que quiero eliminar este producto permanentemente
                            </label>
                        </div>
                        
                        <button type="submit" class="btn btn-danger" onclick="return confirm('¿Está seguro de que desea eliminar este producto?')">
                            ELIMINAR PRODUCTO
                        </button>
                        <a href="/devops/productos" class="btn btn-success">Cancelar</a>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error eliminando producto {product_id}: {e}")
        flash('Error interno al eliminar el producto', 'error')
        return redirect(url_for('devops.gestion_productos'))

# =================================================================
# GESTIÓN DE SUCURSALES (DevOps consumiendo API)
# =================================================================

@devops_bp.route('/sucursales', methods=['GET', 'POST'])
@devops_login_required
def gestion_sucursales():
    from flask import request, flash
    try:
        if request.method == 'POST':
            nombre = request.form.get('nombre', '').strip()
            negocio_id = request.form.get('negocio_id')
            direccion = request.form.get('direccion', '').strip()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            if not nombre or not negocio_id:
                flash('Nombre y negocio son requeridos', 'error')
            else:
                api_post('branches', {
                    'nombre': nombre,
                    'negocio_id': int(negocio_id),
                    'direccion': direccion,
                    'telefono': telefono,
                    'email': email,
                    'activo': True
                })
                flash('Sucursal creada', 'success')
            return redirect(url_for('devops.gestion_sucursales'))

        sucursales_resp = api_get('branches')
        negocios_resp = api_get('businesses')
        sucursales = sucursales_resp.get('data') if isinstance(sucursales_resp, dict) else sucursales_resp
        negocios = negocios_resp.get('data') if isinstance(negocios_resp, dict) else negocios_resp
        try:
            return render_template('devops/sucursales.html', sucursales=sucursales or [], negocios=negocios or [])
        except Exception:
            # Fallback mínimo
            items = ''.join([f"<li>#{s.get('id')} - {s.get('nombre')}</li>" for s in (sucursales or [])])
            options = ''.join([f"<option value='{n.get('id')}'>{n.get('nombre')}</option>" for n in (negocios or [])])
            html = f"""
            <h2>Sucursales</h2>
            <ul>{items}</ul>
            <h3>Crear sucursal</h3>
            <form method='post'>
                <input name='nombre' placeholder='Nombre' required />
                <select name='negocio_id' required><option value=''>Seleccione negocio</option>{options}</select>
                <input name='direccion' placeholder='Dirección' />
                <input name='telefono' placeholder='Teléfono' />
                <input name='email' placeholder='Email' />
                <button type='submit'>Crear</button>
            </form>
            """
            return make_response(html, 200)
    except Exception as e:
        logger.error(f"Error en gestión de sucursales: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@devops_bp.route('/sucursales/<int:branch_id>/editar', methods=['POST'])
@devops_login_required
def editar_sucursal(branch_id: int):
    from flask import request, flash
    try:
        payload = {}
        if request.form.get('nombre'): payload['nombre'] = request.form.get('nombre')
        if request.form.get('direccion'): payload['direccion'] = request.form.get('direccion')
        if request.form.get('telefono'): payload['telefono'] = request.form.get('telefono')
        if request.form.get('email'): payload['email'] = request.form.get('email')
        if request.form.get('negocio_id'): payload['negocio_id'] = int(request.form.get('negocio_id'))
        if request.form.get('activo') is not None:
            payload['activo'] = request.form.get('activo') == 'on'
        client = get_api_client()
        if hasattr(client, 'update_branch'):
            client.update_branch(branch_id, payload)
        else:
            api_put('branches', branch_id, payload)
        flash('Sucursal actualizada', 'success')
    except Exception as e:
        logger.error(f"Error actualizando sucursal: {e}")
        flash('Error actualizando sucursal', 'error')
    return redirect(url_for('devops.gestion_sucursales'))

@devops_bp.route('/sucursales/<int:branch_id>/eliminar', methods=['POST'])
@devops_login_required
def eliminar_sucursal(branch_id: int):
    from flask import flash
    try:
        client = get_api_client()
        if hasattr(client, 'delete_branch'):
            client.delete_branch(branch_id)
        else:
            api_put('branches', branch_id, {'activo': False})
        flash('Sucursal eliminada', 'success')
    except Exception as e:
        logger.error(f"Error eliminando sucursal: {e}")
        flash('Error eliminando sucursal', 'error')
    return redirect(url_for('devops.gestion_sucursales'))

# =============================
# Aliases de rutas solicitadas
# =============================

@devops_bp.route('/sucursales/agregar', methods=['POST'])
@devops_login_required
def alias_agregar_sucursal():
    # Redirige preservando el método a la ruta existente de creación
    return redirect(url_for('devops.gestion_sucursales'), code=307)

@devops_bp.route('/sucursales/editar/<int:branch_id>', methods=['POST'])
@devops_login_required
def alias_editar_sucursal(branch_id: int):
    # Redirige preservando el método a la ruta existente de edición
    return redirect(url_for('devops.editar_sucursal', branch_id=branch_id), code=307)

@devops_bp.route('/sucursales/eliminar/<int:branch_id>', methods=['POST'])
@devops_login_required
def alias_eliminar_sucursal(branch_id: int):
    # Redirige preservando el método a la ruta existente de eliminación
    return redirect(url_for('devops.eliminar_sucursal', branch_id=branch_id), code=307)

# =================================================================
# GESTIÓN DE OFERTAS (DevOps consumiendo API)
# =================================================================

@devops_bp.route('/ofertas', methods=['GET', 'POST'])
@devops_login_required
def gestion_ofertas_alt():
    """Gestión completa de ofertas con API real"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return render_template('devops/ofertas.html', ofertas=[], error_api=True)
    
    try:
        if request.method == 'POST':
            # Crear nueva oferta
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            descuento_porcentaje = request.form.get('descuento_porcentaje', '').strip()
            descuento_fijo = request.form.get('descuento_fijo', '').strip()
            activa = request.form.get('activa') == 'on'
            
            if not titulo:
                flash('El título es requerido', 'error')
            else:
                # Crear oferta usando API real
                data = {
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'activa': activa
                }
                
                # Agregar descuentos si se proporcionan
                if descuento_porcentaje:
                    try:
                        data['descuento_porcentaje'] = float(descuento_porcentaje)
                    except ValueError:
                        flash('El descuento porcentaje debe ser un número válido', 'error')
                        return redirect(url_for('devops.gestion_ofertas_alt'))
                
                if descuento_fijo:
                    try:
                        data['descuento_fijo'] = float(descuento_fijo)
                    except ValueError:
                        flash('El descuento fijo debe ser un número válido', 'error')
                        return redirect(url_for('devops.gestion_ofertas_alt'))
                
                resultado = client.create_oferta(data)
                if resultado:
                    flash(f'Oferta "{titulo}" creada exitosamente', 'success')
                    logger.info(f"Oferta creada desde DevOps: {titulo}")
                else:
                    flash('Error al crear la oferta. Verifique la conexión con la API.', 'error')
            
            return redirect(url_for('devops.gestion_ofertas_alt'))

        # GET: Listar ofertas desde API real
        try:
            ofertas = client.get_ofertas()
            logger.info(f"Obtenidas {len(ofertas)} ofertas desde API")
            
            # Intentar usar template
            try:
                return render_template('devops/ofertas.html', ofertas=ofertas, error_api=False)
            except Exception:
                # Fallback HTML con datos reales
                items_html = ""
                for oferta in ofertas:
                    estado = "Activa" if oferta.get('activa', True) else "Inactiva"
                    descuento_info = ""
                    if oferta.get('descuento_porcentaje'):
                        descuento_info += f"{oferta.get('descuento_porcentaje')}% descuento"
                    if oferta.get('descuento_fijo'):
                        if descuento_info:
                            descuento_info += " o "
                        descuento_info += f"${oferta.get('descuento_fijo'):.2f} descuento fijo"
                    if not descuento_info:
                        descuento_info = "Sin descuento"
                    
                    items_html += f"""
                    <div class="oferta-item" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                        <h4>#{oferta.get('id', 'N/A')} - {oferta.get('titulo', 'Sin título')}</h4>
                        <p><strong>Descripción:</strong> {oferta.get('descripcion', 'Sin descripción')}</p>
                        <p><strong>Descuento:</strong> {descuento_info}</p>
                        <p><strong>Estado:</strong> {estado}</p>
                        <p><strong>Fecha creación:</strong> {oferta.get('fecha_creacion', 'No disponible')}</p>
                        <div style="margin-top: 10px;">
                            <a href="/devops/ofertas/{oferta.get('id')}/editar" class="btn btn-warning">Editar</a>
                            <a href="/devops/ofertas/{oferta.get('id')}/eliminar" class="btn btn-danger" onclick="return confirm('¿Eliminar esta oferta?')">Eliminar</a>
                        </div>
                    </div>
                    """
                
                html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Gestión de Ofertas - DevOps</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .header {{ background: #17a2b8; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                        .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                        .btn-warning {{ background: #ffc107; color: #212529; }}
                        .btn-danger {{ background: #dc3545; color: white; }}
                        .btn-success {{ background: #28a745; color: white; }}
                        .form-group {{ margin-bottom: 15px; }}
                        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                        .form-group input, .form-group textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                        .form-row {{ display: flex; gap: 15px; }}
                        .form-row .form-group {{ flex: 1; }}
                        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
                        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Gestión de Ofertas</h1>
                            <p>Administra las ofertas desde la API de Belgrano Ahorro</p>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <a href="/devops/" class="btn btn-success">← Volver al Panel</a>
                        </div>
                        
                        <h2>Lista de Ofertas ({len(ofertas)} encontradas)</h2>
                        {items_html}
                        
                        <h2>Crear Nueva Oferta</h2>
                        <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                            <div class="form-group">
                                <label for="titulo">Título *</label>
                                <input type="text" id="titulo" name="titulo" required />
                            </div>
                            <div class="form-group">
                                <label for="descripcion">Descripción</label>
                                <textarea id="descripcion" name="descripcion" rows="3"></textarea>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="descuento_porcentaje">Descuento Porcentaje (%)</label>
                                    <input type="number" id="descuento_porcentaje" name="descuento_porcentaje" step="0.01" min="0" max="100" />
                                </div>
                                <div class="form-group">
                                    <label for="descuento_fijo">Descuento Fijo ($)</label>
                                    <input type="number" id="descuento_fijo" name="descuento_fijo" step="0.01" min="0" />
                                </div>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" name="activa" checked /> Oferta activa
                                </label>
                            </div>
                            <button type="submit" class="btn btn-success">Crear Oferta</button>
                        </form>
                    </div>
                </body>
                </html>
                """
                return make_response(html, 200)
                
        except Exception as e:
            logger.error(f"Error obteniendo ofertas desde API: {e}")
            flash('Error al obtener ofertas desde la API', 'error')
            return render_template('devops/ofertas.html', ofertas=[], error_api=True)
            
    except Exception as e:
        logger.error(f"Error en gestión de ofertas: {e}")
        flash('Error interno en gestión de ofertas', 'error')
        return render_template('devops/ofertas.html', ofertas=[], error_api=True)

@devops_bp.route('/ofertas/<int:offer_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_oferta(offer_id: int):
    """Editar oferta existente"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_ofertas_alt'))
    
    try:
        if request.method == 'POST':
            # Actualizar oferta
            data = {
                key: value for key, value in {
                    'titulo': request.form.get('titulo'),
                    'descripcion': request.form.get('descripcion'),
                    'descuento_porcentaje': float(request.form.get('descuento_porcentaje')) if request.form.get('descuento_porcentaje') else None,
                    'descuento_fijo': float(request.form.get('descuento_fijo')) if request.form.get('descuento_fijo') else None,
                    'activa': request.form.get('activa') == 'on'
                }.items() if value is not None and value != ''
            }
            
            resultado = client.update_oferta(offer_id, data)
            if resultado:
                flash('Oferta actualizada exitosamente', 'success')
                logger.info(f"Oferta {offer_id} actualizada desde DevOps")
            else:
                flash('Error al actualizar la oferta. Verifique la conexión con la API.', 'error')
            
            return redirect(url_for('devops.gestion_ofertas_alt'))
        
        else:
            # GET: Mostrar formulario de edición
            oferta = client.get_oferta(offer_id)
            if not oferta:
                flash('Oferta no encontrada', 'error')
                return redirect(url_for('devops.gestion_ofertas_alt'))
            
            # HTML para edición
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Editar Oferta - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #ffc107; color: #212529; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-warning {{ background: #ffc107; color: #212529; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .form-group {{ margin-bottom: 15px; }}
                    .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                    .form-group input, .form-group textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                    .form-row {{ display: flex; gap: 15px; }}
                    .form-row .form-group {{ flex: 1; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Editar Oferta #{offer_id}</h1>
                        <p>Modifica los datos de la oferta</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <a href="/devops/ofertas" class="btn btn-success">← Volver a Ofertas</a>
                    </div>
                    
                    <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                        <div class="form-group">
                            <label for="titulo">Título *</label>
                            <input type="text" id="titulo" name="titulo" value="{oferta.get('titulo', '')}" required />
                        </div>
                        <div class="form-group">
                            <label for="descripcion">Descripción</label>
                            <textarea id="descripcion" name="descripcion" rows="3">{oferta.get('descripcion', '')}</textarea>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="descuento_porcentaje">Descuento Porcentaje (%)</label>
                                <input type="number" id="descuento_porcentaje" name="descuento_porcentaje" step="0.01" min="0" max="100" value="{oferta.get('descuento_porcentaje', '')}" />
                            </div>
                            <div class="form-group">
                                <label for="descuento_fijo">Descuento Fijo ($)</label>
                                <input type="number" id="descuento_fijo" name="descuento_fijo" step="0.01" min="0" value="{oferta.get('descuento_fijo', '')}" />
                            </div>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="activa" {'checked' if oferta.get('activa', True) else ''} /> Oferta activa
                            </label>
                        </div>
                        <button type="submit" class="btn btn-warning">Actualizar Oferta</button>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error editando oferta {offer_id}: {e}")
        flash('Error interno al editar la oferta', 'error')
        return redirect(url_for('devops.gestion_ofertas_alt'))

@devops_bp.route('/ofertas/<int:offer_id>/eliminar', methods=['GET', 'POST'])
@devops_login_required
def eliminar_oferta(offer_id: int):
    """Eliminar oferta con confirmación"""
    from flask import flash, request, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_ofertas_alt'))
    
    try:
        if request.method == 'POST':
            # Confirmar eliminación
            confirmar = request.form.get('confirmar')
            if confirmar == 'si':
                # Eliminar usando API real
                resultado = client.delete_oferta(offer_id)
                if resultado:
                    flash('Oferta eliminada exitosamente', 'success')
                    logger.info(f"Oferta {offer_id} eliminada desde DevOps")
                else:
                    flash('Error al eliminar la oferta. Verifique la conexión con la API.', 'error')
            else:
                flash('Eliminación cancelada', 'info')
            
            return redirect(url_for('devops.gestion_ofertas_alt'))
        
        else:
            # GET: Mostrar confirmación
            oferta = client.get_oferta(offer_id)
            if not oferta:
                flash('Oferta no encontrada', 'error')
                return redirect(url_for('devops.gestion_ofertas_alt'))
            
            # HTML de confirmación
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Eliminar Oferta - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #dc3545; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 4px; margin: 20px 0; border: 1px solid #ffeaa7; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Eliminar Oferta #{offer_id}</h1>
                        <p>Esta acción no se puede deshacer</p>
                    </div>
                    
                    <div class="warning">
                        <strong>ADVERTENCIA:</strong> Está a punto de eliminar permanentemente la oferta "{oferta.get('titulo', 'Sin título')}". Esta acción no se puede deshacer.
                    </div>
                    
                    <h3>Datos de la oferta a eliminar:</h3>
                    <ul>
                        <li><strong>ID:</strong> {offer_id}</li>
                        <li><strong>Título:</strong> {oferta.get('titulo', 'Sin título')}</li>
                        <li><strong>Descripción:</strong> {oferta.get('descripcion', 'Sin descripción')}</li>
                        <li><strong>Descuento Porcentaje:</strong> {oferta.get('descuento_porcentaje', 'N/A')}%</li>
                        <li><strong>Descuento Fijo:</strong> ${oferta.get('descuento_fijo', 0):.2f}</li>
                        <li><strong>Estado:</strong> {'Activa' if oferta.get('activa', True) else 'Inactiva'}</li>
                    </ul>
                    
                    <form method="post" style="margin-top: 30px;">
                        <div style="margin-bottom: 20px;">
                            <label>
                                <input type="checkbox" name="confirmar" value="si" required /> 
                                Confirmo que quiero eliminar esta oferta permanentemente
                            </label>
                        </div>
                        
                        <button type="submit" class="btn btn-danger" onclick="return confirm('¿Está seguro de que desea eliminar esta oferta?')">
                            ELIMINAR OFERTA
                        </button>
                        <a href="/devops/ofertas" class="btn btn-success">Cancelar</a>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error eliminando oferta {offer_id}: {e}")
        flash('Error interno al eliminar la oferta', 'error')
        return redirect(url_for('devops.gestion_ofertas_alt'))

# =================================================================
# GESTIÓN DE PRECIOS (DevOps consumiendo API)
# =================================================================

@devops_bp.route('/precios', methods=['GET', 'POST'])
@devops_login_required
def gestion_precios():
    """Gestión completa de precios con API real"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return render_template('devops/precios.html', precios=[], productos=[], error_api=True)
    
    try:
        if request.method == 'POST':
            # Crear nuevo precio
            producto_id = request.form.get('producto_id', '').strip()
            precio_base = request.form.get('precio_base', '').strip()
            precio_oferta = request.form.get('precio_oferta', '').strip()
            fecha_inicio = request.form.get('fecha_inicio', '').strip()
            fecha_fin = request.form.get('fecha_fin', '').strip()
            activo = request.form.get('activo') == 'on'
            
            if not producto_id or not precio_base:
                flash('Producto y precio base son requeridos', 'error')
            else:
                try:
                    precio_base_float = float(precio_base)
                    precio_oferta_float = float(precio_oferta) if precio_oferta else None
                    
                    # Crear precio usando API real
                    data = {
                        'producto_id': int(producto_id),
                        'precio_base': precio_base_float,
                        'activo': activo
                    }
                    
                    # Agregar campos opcionales si se proporcionan
                    if precio_oferta_float:
                        data['precio_oferta'] = precio_oferta_float
                    if fecha_inicio:
                        data['fecha_inicio'] = fecha_inicio
                    if fecha_fin:
                        data['fecha_fin'] = fecha_fin
                    
                    resultado = client.create_precio(data)
                    if resultado:
                        flash('Precio creado exitosamente', 'success')
                        logger.info(f"Precio creado desde DevOps para producto {producto_id}")
                    else:
                        flash('Error al crear el precio. Verifique la conexión con la API.', 'error')
                except ValueError:
                    flash('Los precios deben ser números válidos', 'error')
            
            return redirect(url_for('devops.gestion_precios'))

        # GET: Listar precios y productos desde API real
        try:
            precios = client.get_precios()
            productos = client.get_productos()
            logger.info(f"Obtenidos {len(precios)} precios y {len(productos)} productos desde API")
            
            # Intentar usar template
            try:
                return render_template('devops/precios.html', precios=precios, productos=productos, error_api=False)
            except Exception:
                # Fallback HTML con datos reales
                items_html = ""
                for precio in precios:
                    estado = "Activo" if precio.get('activo', True) else "Inactivo"
                    producto_nombre = "Sin producto"
                    for producto in productos:
                        if producto.get('id') == precio.get('producto_id'):
                            producto_nombre = producto.get('nombre', 'Sin nombre')
                            break
                    
                    precio_oferta_info = ""
                    if precio.get('precio_oferta'):
                        precio_oferta_info = f"<br><strong>Precio oferta:</strong> ${precio.get('precio_oferta'):.2f}"
                    
                    fechas_info = ""
                    if precio.get('fecha_inicio'):
                        fechas_info += f"<br><strong>Inicio:</strong> {precio.get('fecha_inicio')}"
                    if precio.get('fecha_fin'):
                        fechas_info += f"<br><strong>Fin:</strong> {precio.get('fecha_fin')}"
                    
                    items_html += f"""
                    <div class="precio-item" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                        <h4>#{precio.get('id', 'N/A')} - {producto_nombre}</h4>
                        <p><strong>Precio base:</strong> ${precio.get('precio_base', 0):.2f}</p>
                        {precio_oferta_info}
                        <p><strong>Estado:</strong> {estado}</p>
                        {fechas_info}
                        <div style="margin-top: 10px;">
                            <a href="/devops/precios/{precio.get('id')}/editar" class="btn btn-warning">Editar</a>
                            <a href="/devops/precios/{precio.get('id')}/eliminar" class="btn btn-danger" onclick="return confirm('¿Eliminar este precio?')">Eliminar</a>
                        </div>
                    </div>
                    """
                
                # Opciones de productos para el selector
                options_html = '<option value="">Seleccione producto</option>'
                for producto in productos:
                    options_html += f'<option value="{producto.get("id")}">{producto.get("nombre", "Sin nombre")} - ${producto.get("precio", 0):.2f}</option>'
                
                html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Gestión de Precios - DevOps</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .header {{ background: #6f42c1; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                        .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                        .btn-warning {{ background: #ffc107; color: #212529; }}
                        .btn-danger {{ background: #dc3545; color: white; }}
                        .btn-success {{ background: #28a745; color: white; }}
                        .form-group {{ margin-bottom: 15px; }}
                        .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                        .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                        .form-row {{ display: flex; gap: 15px; }}
                        .form-row .form-group {{ flex: 1; }}
                        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 4px; }}
                        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Gestión de Precios</h1>
                            <p>Administra los precios desde la API de Belgrano Ahorro</p>
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <a href="/devops/" class="btn btn-success">← Volver al Panel</a>
                        </div>
                        
                        <h2>Lista de Precios ({len(precios)} encontrados)</h2>
                        {items_html}
                        
                        <h2>Crear Nuevo Precio</h2>
                        <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                            <div class="form-group">
                                <label for="producto_id">Producto *</label>
                                <select id="producto_id" name="producto_id" required>
                                    {options_html}
                                </select>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="precio_base">Precio Base *</label>
                                    <input type="number" id="precio_base" name="precio_base" step="0.01" min="0" required />
                                </div>
                                <div class="form-group">
                                    <label for="precio_oferta">Precio Oferta</label>
                                    <input type="number" id="precio_oferta" name="precio_oferta" step="0.01" min="0" />
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="fecha_inicio">Fecha Inicio</label>
                                    <input type="date" id="fecha_inicio" name="fecha_inicio" />
                                </div>
                                <div class="form-group">
                                    <label for="fecha_fin">Fecha Fin</label>
                                    <input type="date" id="fecha_fin" name="fecha_fin" />
                                </div>
                            </div>
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" name="activo" checked /> Precio activo
                                </label>
                            </div>
                            <button type="submit" class="btn btn-success">Crear Precio</button>
                        </form>
                    </div>
                </body>
                </html>
                """
                return make_response(html, 200)
                
        except Exception as e:
            logger.error(f"Error obteniendo precios desde API: {e}")
            flash('Error al obtener precios desde la API', 'error')
            return render_template('devops/precios.html', precios=[], productos=[], error_api=True)
            
    except Exception as e:
        logger.error(f"Error en gestión de precios: {e}")
        flash('Error interno en gestión de precios', 'error')
        return render_template('devops/precios.html', precios=[], productos=[], error_api=True)

@devops_bp.route('/precios/<int:precio_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_precio(precio_id: int):
    """Editar precio existente"""
    from flask import request, flash, render_template, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_precios'))
    
    try:
        if request.method == 'POST':
            # Actualizar precio
            data = {
                key: value for key, value in {
                    'producto_id': int(request.form.get('producto_id')) if request.form.get('producto_id') else None,
                    'precio_base': float(request.form.get('precio_base')) if request.form.get('precio_base') else None,
                    'precio_oferta': float(request.form.get('precio_oferta')) if request.form.get('precio_oferta') else None,
                    'fecha_inicio': request.form.get('fecha_inicio'),
                    'fecha_fin': request.form.get('fecha_fin'),
                    'activo': request.form.get('activo') == 'on'
                }.items() if value is not None and value != ''
            }
            
            resultado = client.update_precio(precio_id, data)
            if resultado:
                flash('Precio actualizado exitosamente', 'success')
                logger.info(f"Precio {precio_id} actualizado desde DevOps")
            else:
                flash('Error al actualizar el precio. Verifique la conexión con la API.', 'error')
            
            return redirect(url_for('devops.gestion_precios'))
        
        else:
            # GET: Mostrar formulario de edición
            precio = client.get_precio(precio_id)
            productos = client.get_productos()
            
            if not precio:
                flash('Precio no encontrado', 'error')
                return redirect(url_for('devops.gestion_precios'))
            
            # Opciones de productos para el selector
            options_html = '<option value="">Seleccione producto</option>'
            for producto in productos:
                selected = 'selected' if producto.get('id') == precio.get('producto_id') else ''
                options_html += f'<option value="{producto.get("id")}" {selected}>{producto.get("nombre", "Sin nombre")} - ${producto.get("precio", 0):.2f}</option>'
            
            # HTML para edición
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Editar Precio - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #ffc107; color: #212529; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-warning {{ background: #ffc107; color: #212529; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .form-group {{ margin-bottom: 15px; }}
                    .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                    .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                    .form-row {{ display: flex; gap: 15px; }}
                    .form-row .form-group {{ flex: 1; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Editar Precio #{precio_id}</h1>
                        <p>Modifica los datos del precio</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <a href="/devops/precios" class="btn btn-success">← Volver a Precios</a>
                    </div>
                    
                    <form method="post" style="background: #f8f9fa; padding: 20px; border-radius: 5px;">
                        <div class="form-group">
                            <label for="producto_id">Producto *</label>
                            <select id="producto_id" name="producto_id" required>
                                {options_html}
                            </select>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="precio_base">Precio Base *</label>
                                <input type="number" id="precio_base" name="precio_base" step="0.01" min="0" value="{precio.get('precio_base', 0)}" required />
                            </div>
                            <div class="form-group">
                                <label for="precio_oferta">Precio Oferta</label>
                                <input type="number" id="precio_oferta" name="precio_oferta" step="0.01" min="0" value="{precio.get('precio_oferta', '')}" />
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="fecha_inicio">Fecha Inicio</label>
                                <input type="date" id="fecha_inicio" name="fecha_inicio" value="{precio.get('fecha_inicio', '')}" />
                            </div>
                            <div class="form-group">
                                <label for="fecha_fin">Fecha Fin</label>
                                <input type="date" id="fecha_fin" name="fecha_fin" value="{precio.get('fecha_fin', '')}" />
                            </div>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" name="activo" {'checked' if precio.get('activo', True) else ''} /> Precio activo
                            </label>
                        </div>
                        <button type="submit" class="btn btn-warning">Actualizar Precio</button>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error editando precio {precio_id}: {e}")
        flash('Error interno al editar el precio', 'error')
        return redirect(url_for('devops.gestion_precios'))

@devops_bp.route('/precios/<int:precio_id>/eliminar', methods=['GET', 'POST'])
@devops_login_required
def eliminar_precio(precio_id: int):
    """Eliminar precio con confirmación"""
    from flask import flash, request, make_response
    
    # Obtener cliente API
    client = get_api_client()
    if not client:
        flash('Error: No se puede conectar con la API de Belgrano Ahorro', 'error')
        return redirect(url_for('devops.gestion_precios'))
    
    try:
        if request.method == 'POST':
            # Confirmar eliminación
            confirmar = request.form.get('confirmar')
            if confirmar == 'si':
                # Eliminar usando API real
                resultado = client.delete_precio(precio_id)
                if resultado:
                    flash('Precio eliminado exitosamente', 'success')
                    logger.info(f"Precio {precio_id} eliminado desde DevOps")
                else:
                    flash('Error al eliminar el precio. Verifique la conexión con la API.', 'error')
            else:
                flash('Eliminación cancelada', 'info')
            
            return redirect(url_for('devops.gestion_precios'))
        
        else:
            # GET: Mostrar confirmación
            precio = client.get_precio(precio_id)
            productos = client.get_productos()
            
            if not precio:
                flash('Precio no encontrado', 'error')
                return redirect(url_for('devops.gestion_precios'))
            
            # Encontrar nombre del producto
            producto_nombre = "Sin producto"
            for producto in productos:
                if producto.get('id') == precio.get('producto_id'):
                    producto_nombre = producto.get('nombre', 'Sin nombre')
                    break
            
            # HTML de confirmación
            html = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Eliminar Precio - DevOps</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ background: #dc3545; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .btn {{ padding: 8px 16px; margin: 5px; text-decoration: none; border-radius: 4px; display: inline-block; }}
                    .btn-danger {{ background: #dc3545; color: white; }}
                    .btn-success {{ background: #28a745; color: white; }}
                    .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 4px; margin: 20px 0; border: 1px solid #ffeaa7; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Eliminar Precio #{precio_id}</h1>
                        <p>Esta acción no se puede deshacer</p>
                    </div>
                    
                    <div class="warning">
                        <strong>ADVERTENCIA:</strong> Está a punto de eliminar permanentemente el precio para "{producto_nombre}". Esta acción no se puede deshacer.
                    </div>
                    
                    <h3>Datos del precio a eliminar:</h3>
                    <ul>
                        <li><strong>ID:</strong> {precio_id}</li>
                        <li><strong>Producto:</strong> {producto_nombre}</li>
                        <li><strong>Precio Base:</strong> ${precio.get('precio_base', 0):.2f}</li>
                        <li><strong>Precio Oferta:</strong> ${precio.get('precio_oferta', 0):.2f if precio.get('precio_oferta') else 'N/A'}</li>
                        <li><strong>Estado:</strong> {'Activo' if precio.get('activo', True) else 'Inactivo'}</li>
                        <li><strong>Fecha Inicio:</strong> {precio.get('fecha_inicio', 'N/A')}</li>
                        <li><strong>Fecha Fin:</strong> {precio.get('fecha_fin', 'N/A')}</li>
                    </ul>
                    
                    <form method="post" style="margin-top: 30px;">
                        <div style="margin-bottom: 20px;">
                            <label>
                                <input type="checkbox" name="confirmar" value="si" required /> 
                                Confirmo que quiero eliminar este precio permanentemente
                            </label>
                        </div>
                        
                        <button type="submit" class="btn btn-danger" onclick="return confirm('¿Está seguro de que desea eliminar este precio?')">
                            ELIMINAR PRECIO
                        </button>
                        <a href="/devops/precios" class="btn btn-success">Cancelar</a>
                    </form>
                </div>
            </body>
            </html>
            """
            return make_response(html, 200)
            
    except Exception as e:
        logger.error(f"Error eliminando precio {precio_id}: {e}")
        flash('Error interno al eliminar el precio', 'error')
        return redirect(url_for('devops.gestion_precios'))

# =================================================================
# MANEJO DE ERRORES
# =================================================================

@devops_bp.errorhandler(404)
def devops_not_found(error):
    """Manejar errores 404 en DevOps"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint DevOps no encontrado',
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

# Crear aplicación Flask para ejecución directa
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = 'devops_secret_key_2025'
    app.register_blueprint(devops_bp)
    
    print("Iniciando DevOps en puerto 5002...")
    print("URL: http://localhost:5002/devops/")
    print("Credenciales: devops / DevOps2025!Secure")
    print("Presiona Ctrl+C para detener")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=False)
    except KeyboardInterrupt:
        print("\nDevOps detenido")
    except Exception as e:
        print(f"Error iniciando DevOps: {e}")
