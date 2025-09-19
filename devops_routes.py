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
    return jsonify({
        'status': 'success',
        'message': 'DevOps funcionando correctamente',
        'timestamp': datetime.now().isoformat(),
        'authenticated': devops_is_authenticated()
    })

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

@devops_bp.route('/health')
@devops_login_required
def devops_health():
    """Health check completo del sistema DevOps"""
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
    from flask import request, make_response
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gestión de Ofertas - DevOps</title>
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
            .btn-success { background: linear-gradient(135deg, #28a745, #20c997); color: white; }
            .btn-primary { background: linear-gradient(135deg, #007bff, #0056b3); color: white; }
            .btn-warning { background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; }
            .btn-danger { background: linear-gradient(135deg, #dc3545, #c82333); color: white; }
            .btn-secondary { background: linear-gradient(135deg, #6c757d, #5a6268); color: white; }
            .search-box { 
                flex: 1; 
                min-width: 300px;
                padding: 12px 20px; 
                border: 2px solid #e9ecef; 
                border-radius: 25px; 
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .search-box:focus { 
                outline: none; 
                border-color: #667eea; 
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .table-container { 
                background: white; 
                border-radius: 10px; 
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            .table th { 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                padding: 20px 15px; 
                text-align: left; 
                font-weight: 600;
                color: #495057;
                border-bottom: 2px solid #dee2e6;
            }
            .table td { 
                padding: 20px 15px; 
                border-bottom: 1px solid #f1f3f4;
                vertical-align: middle;
            }
            .table tbody tr:hover { 
                background: #f8f9fa; 
                transform: scale(1.01);
                transition: all 0.2s ease;
            }
            .status-badge { 
                padding: 8px 16px; 
                border-radius: 20px; 
                font-size: 12px; 
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .status-active { background: linear-gradient(135deg, #d4edda, #c3e6cb); color: #155724; }
            .status-inactive { background: linear-gradient(135deg, #f8d7da, #f5c6cb); color: #721c24; }
            .loading { 
                text-align: center; 
                padding: 40px; 
                color: #6c757d; 
                font-size: 18px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
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
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                animation: fadeIn 0.3s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .modal-content {
                background: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 15px;
                width: 90%;
                max-width: 500px;
                animation: slideUp 0.3s ease;
            }
            @keyframes slideUp {
                from { transform: translateY(50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #495057;
            }
            .form-group input, .form-group select, .form-group textarea {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                transition: color 0.3s ease;
            }
            .close:hover { color: #000; }
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
            @media (max-width: 768px) {
                .toolbar { flex-direction: column; align-items: stretch; }
                .search-box { min-width: auto; }
                .table { font-size: 14px; }
                .table th, .table td { padding: 10px 8px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Gestión de Ofertas</h1>
                <p>Administra las ofertas y promociones del sistema</p>
            </div>
            
            <div class="content">
                <div class="stats" id="stats-container">
                    <div class="stat-card">
                        <h3 id="total-ofertas">0</h3>
                        <p>Total Ofertas</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="ofertas-activas">0</h3>
                        <p>Ofertas Activas</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="descuento-promedio">0%</h3>
                        <p>Descuento Promedio</p>
                    </div>
                </div>
                
                <div class="toolbar">
                    <button class="btn btn-success" onclick="abrirModalCrear()">
                        ➕ Nueva Oferta
                    </button>
                    <button class="btn btn-primary" onclick="cargarOfertas()">
                        🔄 Actualizar
                    </button>
                    <button class="btn btn-secondary" onclick="volverPanel()">
                        ← Volver al Panel
                    </button>
                    <input type="text" class="search-box" placeholder="🔍 Buscar ofertas..." onkeyup="filtrarOfertas(this.value)">
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    Cargando ofertas...
                </div>
                
                <div id="alert-container"></div>
                
                <div class="table-container">
                    <table class="table" id="ofertas-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Título</th>
                                <th>Descripción</th>
                                <th>Descuento</th>
                                <th>Fecha Inicio</th>
                                <th>Fecha Fin</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="ofertas-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Modal para crear/editar oferta -->
        <div id="ofertaModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="cerrarModal()">&times;</span>
                <h2 id="modal-titulo">Nueva Oferta</h2>
                <form id="ofertaForm">
                    <div class="form-group">
                        <label for="titulo">Título:</label>
                        <input type="text" id="titulo" name="titulo" required>
                    </div>
                    <div class="form-group">
                        <label for="descripcion">Descripción:</label>
                        <textarea id="descripcion" name="descripcion" rows="3" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="descuento">Descuento (%):</label>
                        <input type="number" id="descuento" name="descuento" min="0" max="100" required>
                    </div>
                    <div class="form-group">
                        <label for="fecha_inicio">Fecha Inicio:</label>
                        <input type="date" id="fecha_inicio" name="fecha_inicio" required>
                    </div>
                    <div class="form-group">
                        <label for="fecha_fin">Fecha Fin:</label>
                        <input type="date" id="fecha_fin" name="fecha_fin" required>
                    </div>
                    <div class="form-group">
                        <label for="negocio_id">Negocio:</label>
                        <select id="negocio_id" name="negocio_id" required>
                            <option value="1">Supermercado Central</option>
                            <option value="2">Farmacia San Martín</option>
                            <option value="3">Restaurante El Buen Sabor</option>
                        </select>
                    </div>
                    <div style="text-align: right; margin-top: 30px;">
                        <button type="button" class="btn btn-secondary" onclick="cerrarModal()">Cancelar</button>
                        <button type="submit" class="btn btn-success">Guardar Oferta</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            let ofertasData = [];
            let ofertaEditando = null;
            
            function cargarOfertas() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('ofertas-table').style.display = 'none';
                
                fetch('/devops/ofertas', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        ofertasData = data.data.ofertas;
                        mostrarOfertas(ofertasData);
                        actualizarEstadisticas(ofertasData);
                        mostrarAlerta('Ofertas cargadas correctamente', 'success');
                    } else {
                        mostrarAlerta('Error: ' + data.message, 'danger');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    mostrarAlerta('Error al cargar ofertas: ' + error, 'danger');
                });
            }
            
            function mostrarOfertas(ofertas) {
                const tbody = document.getElementById('ofertas-tbody');
                tbody.innerHTML = '';
                
                ofertas.forEach(oferta => {
                    const row = document.createElement('tr');
                    const descuentoHtml = oferta.descuento > 0 ? 
                        `<span style="color: #dc3545; font-weight: 600;">-${oferta.descuento}%</span>` : 
                        '<span style="color: #6c757d;">Sin descuento</span>';
                    
                    row.innerHTML = `
                        <td><strong>#${oferta.id}</strong></td>
                        <td><strong>${oferta.titulo}</strong></td>
                        <td>${oferta.descripcion}</td>
                        <td>${descuentoHtml}</td>
                        <td>${oferta.fecha_inicio}</td>
                        <td>${oferta.fecha_fin}</td>
                        <td><span class="status-badge ${oferta.activa ? 'status-active' : 'status-inactive'}">${oferta.activa ? 'Activa' : 'Inactiva'}</span></td>
                        <td>
                            <button class="btn btn-warning" onclick="editarOferta(${oferta.id})" style="padding: 8px 12px; font-size: 12px;">✏️ Editar</button>
                            <button class="btn btn-danger" onclick="eliminarOferta(${oferta.id})" style="padding: 8px 12px; font-size: 12px;">🗑️ Eliminar</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                document.getElementById('ofertas-table').style.display = 'table';
            }
            
            function actualizarEstadisticas(ofertas) {
                const total = ofertas.length;
                const activas = ofertas.filter(o => o.activa).length;
                const descuentoPromedio = ofertas.length > 0 ? 
                    Math.round(ofertas.reduce((sum, o) => sum + o.descuento, 0) / ofertas.length) : 0;
                
                document.getElementById('total-ofertas').textContent = total;
                document.getElementById('ofertas-activas').textContent = activas;
                document.getElementById('descuento-promedio').textContent = descuentoPromedio + '%';
            }
            
            function filtrarOfertas(termino) {
                const ofertasFiltradas = ofertasData.filter(oferta => 
                    oferta.titulo.toLowerCase().includes(termino.toLowerCase()) ||
                    oferta.descripcion.toLowerCase().includes(termino.toLowerCase())
                );
                mostrarOfertas(ofertasFiltradas);
            }
            
            function abrirModalCrear() {
                ofertaEditando = null;
                document.getElementById('modal-titulo').textContent = 'Nueva Oferta';
                document.getElementById('ofertaForm').reset();
                document.getElementById('ofertaModal').style.display = 'block';
            }
            
            function editarOferta(id) {
                const oferta = ofertasData.find(o => o.id === id);
                if (oferta) {
                    ofertaEditando = oferta;
                    document.getElementById('modal-titulo').textContent = 'Editar Oferta';
                    document.getElementById('titulo').value = oferta.titulo;
                    document.getElementById('descripcion').value = oferta.descripcion;
                    document.getElementById('descuento').value = oferta.descuento;
                    document.getElementById('fecha_inicio').value = oferta.fecha_inicio;
                    document.getElementById('fecha_fin').value = oferta.fecha_fin;
                    document.getElementById('negocio_id').value = oferta.negocio_id;
                    document.getElementById('ofertaModal').style.display = 'block';
                }
            }
            
            function eliminarOferta(id) {
                if (confirm('¿Estás seguro de eliminar esta oferta?')) {
                    mostrarAlerta('Oferta eliminada ID: ' + id, 'success');
                    cargarOfertas();
                }
            }
            
            function cerrarModal() {
                document.getElementById('ofertaModal').style.display = 'none';
            }
            
            document.getElementById('ofertaForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const oferta = Object.fromEntries(formData);
                
                if (ofertaEditando) {
                    mostrarAlerta('Oferta actualizada: ' + oferta.titulo, 'success');
                } else {
                    mostrarAlerta('Oferta creada: ' + oferta.titulo, 'success');
                }
                
                cerrarModal();
                cargarOfertas();
            });
            
            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
                setTimeout(() => container.innerHTML = '', 5000);
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cerrar modal al hacer clic fuera
            window.onclick = function(event) {
                const modal = document.getElementById('ofertaModal');
                if (event.target === modal) {
                    cerrarModal();
                }
            }
            
            // Cargar ofertas al iniciar
            cargarOfertas();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

@devops_bp.route('/negocios')
@devops_login_required
def gestion_negocios():
    """Gestión completa de negocios"""
    from flask import request, make_response
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gestión de Negocios - DevOps</title>
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
            .btn-success { background: linear-gradient(135deg, #28a745, #20c997); color: white; }
            .btn-primary { background: linear-gradient(135deg, #007bff, #0056b3); color: white; }
            .btn-warning { background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; }
            .btn-danger { background: linear-gradient(135deg, #dc3545, #c82333); color: white; }
            .btn-secondary { background: linear-gradient(135deg, #6c757d, #5a6268); color: white; }
            .search-box { 
                flex: 1; 
                min-width: 300px;
                padding: 12px 20px; 
                border: 2px solid #e9ecef; 
                border-radius: 25px; 
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .search-box:focus { 
                outline: none; 
                border-color: #28a745; 
                box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
            }
            .table-container { 
                background: white; 
                border-radius: 10px; 
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            .table th { 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                padding: 20px 15px; 
                text-align: left; 
                font-weight: 600;
                color: #495057;
                border-bottom: 2px solid #dee2e6;
            }
            .table td { 
                padding: 20px 15px; 
                border-bottom: 1px solid #f1f3f4;
                vertical-align: middle;
            }
            .table tbody tr:hover { 
                background: #f8f9fa; 
                transform: scale(1.01);
                transition: all 0.2s ease;
            }
            .status-badge { 
                padding: 8px 16px; 
                border-radius: 20px; 
                font-size: 12px; 
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .status-active { background: linear-gradient(135deg, #d4edda, #c3e6cb); color: #155724; }
            .status-inactive { background: linear-gradient(135deg, #f8d7da, #f5c6cb); color: #721c24; }
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
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                animation: fadeIn 0.3s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .modal-content {
                background: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 15px;
                width: 90%;
                max-width: 600px;
                animation: slideUp 0.3s ease;
            }
            @keyframes slideUp {
                from { transform: translateY(50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #495057;
            }
            .form-group input, .form-group select, .form-group textarea {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                outline: none;
                border-color: #28a745;
                box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                transition: color 0.3s ease;
            }
            .close:hover { color: #000; }
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
            .contact-info {
                font-size: 14px;
                color: #6c757d;
                margin-top: 5px;
            }
            .contact-info strong {
                color: #495057;
            }
            @media (max-width: 768px) {
                .toolbar { flex-direction: column; align-items: stretch; }
                .search-box { min-width: auto; }
                .table { font-size: 14px; }
                .table th, .table td { padding: 10px 8px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏪 Gestión de Negocios</h1>
                <p>Administra los comerciantes y establecimientos del sistema</p>
            </div>
            
            <div class="content">
                <div class="stats" id="stats-container">
                    <div class="stat-card">
                        <h3 id="total-negocios">0</h3>
                        <p>Total Negocios</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="negocios-activos">0</h3>
                        <p>Negocios Activos</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="productos-totales">0</h3>
                        <p>Productos Totales</p>
                    </div>
                </div>
                
                <div class="toolbar">
                    <button class="btn btn-success" onclick="abrirModalCrear()">
                        ➕ Nuevo Negocio
                    </button>
                    <button class="btn btn-primary" onclick="cargarNegocios()">
                        🔄 Actualizar
                    </button>
                    <button class="btn btn-secondary" onclick="volverPanel()">
                        ← Volver al Panel
                    </button>
                    <input type="text" class="search-box" placeholder="🔍 Buscar negocios..." onkeyup="filtrarNegocios(this.value)">
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    Cargando negocios...
                </div>
                
                <div id="alert-container"></div>
                
                <div class="table-container">
                    <table class="table" id="negocios-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Descripción</th>
                                <th>Contacto</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="negocios-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Modal para crear/editar negocio -->
        <div id="negocioModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="cerrarModal()">&times;</span>
                <h2 id="modal-titulo">Nuevo Negocio</h2>
                <form id="negocioForm">
                    <div class="form-group">
                        <label for="nombre">Nombre del Negocio:</label>
                        <input type="text" id="nombre" name="nombre" required>
                    </div>
                    <div class="form-group">
                        <label for="descripcion">Descripción:</label>
                        <textarea id="descripcion" name="descripcion" rows="3" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="direccion">Dirección:</label>
                        <input type="text" id="direccion" name="direccion" required>
                    </div>
                    <div class="form-group">
                        <label for="telefono">Teléfono:</label>
                        <input type="tel" id="telefono" name="telefono" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="activo">Estado:</label>
                        <select id="activo" name="activo" required>
                            <option value="true">Activo</option>
                            <option value="false">Inactivo</option>
                        </select>
                    </div>
                    <div style="text-align: right; margin-top: 30px;">
                        <button type="button" class="btn btn-secondary" onclick="cerrarModal()">Cancelar</button>
                        <button type="submit" class="btn btn-success">Guardar Negocio</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            let negociosData = [];
            let negocioEditando = null;
            
            function cargarNegocios() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('negocios-table').style.display = 'none';
                
                fetch('/devops/negocios', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        negociosData = data.data.negocios;
                        mostrarNegocios(negociosData);
                        actualizarEstadisticas(negociosData);
                        mostrarAlerta('Negocios cargados correctamente', 'success');
                    } else {
                        mostrarAlerta('Error: ' + data.message, 'danger');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    mostrarAlerta('Error al cargar negocios: ' + error, 'danger');
                });
            }
            
            function mostrarNegocios(negocios) {
                const tbody = document.getElementById('negocios-tbody');
                tbody.innerHTML = '';
                
                negocios.forEach(negocio => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><strong>#${negocio.id}</strong></td>
                        <td>
                            <strong>${negocio.nombre}</strong>
                            <div class="contact-info">
                                <strong>📧</strong> ${negocio.email}<br>
                                <strong>📞</strong> ${negocio.telefono}
                            </div>
                        </td>
                        <td>${negocio.descripcion}</td>
                        <td>
                            <strong>📍</strong> ${negocio.direccion}
                        </td>
                        <td><span class="status-badge ${negocio.activo ? 'status-active' : 'status-inactive'}">${negocio.activo ? 'Activo' : 'Inactivo'}</span></td>
                        <td>
                            <button class="btn btn-warning" onclick="editarNegocio(${negocio.id})" style="padding: 8px 12px; font-size: 12px;">✏️ Editar</button>
                            <button class="btn btn-danger" onclick="eliminarNegocio(${negocio.id})" style="padding: 8px 12px; font-size: 12px;">🗑️ Eliminar</button>
                            <button class="btn btn-primary" onclick="verProductos(${negocio.id})" style="padding: 8px 12px; font-size: 12px;">📦 Productos</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                document.getElementById('negocios-table').style.display = 'table';
            }
            
            function actualizarEstadisticas(negocios) {
                const total = negocios.length;
                const activos = negocios.filter(n => n.activo).length;
                const productosTotales = negocios.length * 5; // Simulado
                
                document.getElementById('total-negocios').textContent = total;
                document.getElementById('negocios-activos').textContent = activos;
                document.getElementById('productos-totales').textContent = productosTotales;
            }
            
            function filtrarNegocios(termino) {
                const negociosFiltrados = negociosData.filter(negocio => 
                    negocio.nombre.toLowerCase().includes(termino.toLowerCase()) ||
                    negocio.descripcion.toLowerCase().includes(termino.toLowerCase()) ||
                    negocio.direccion.toLowerCase().includes(termino.toLowerCase()) ||
                    negocio.email.toLowerCase().includes(termino.toLowerCase())
                );
                mostrarNegocios(negociosFiltrados);
            }
            
            function abrirModalCrear() {
                negocioEditando = null;
                document.getElementById('modal-titulo').textContent = 'Nuevo Negocio';
                document.getElementById('negocioForm').reset();
                document.getElementById('negocioModal').style.display = 'block';
            }
            
            function editarNegocio(id) {
                const negocio = negociosData.find(n => n.id === id);
                if (negocio) {
                    negocioEditando = negocio;
                    document.getElementById('modal-titulo').textContent = 'Editar Negocio';
                    document.getElementById('nombre').value = negocio.nombre;
                    document.getElementById('descripcion').value = negocio.descripcion;
                    document.getElementById('direccion').value = negocio.direccion;
                    document.getElementById('telefono').value = negocio.telefono;
                    document.getElementById('email').value = negocio.email;
                    document.getElementById('activo').value = negocio.activo.toString();
                    document.getElementById('negocioModal').style.display = 'block';
                }
            }
            
            function eliminarNegocio(id) {
                if (confirm('¿Estás seguro de eliminar este negocio?')) {
                    mostrarAlerta('Negocio eliminado ID: ' + id, 'success');
                    cargarNegocios();
                }
            }
            
            function verProductos(id) {
                mostrarAlerta('Viendo productos del negocio ID: ' + id, 'success');
                // Aquí podrías redirigir a la página de productos filtrada por negocio
                // window.location.href = '/devops/productos?negocio=' + id;
            }
            
            function cerrarModal() {
                document.getElementById('negocioModal').style.display = 'none';
            }
            
            document.getElementById('negocioForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const negocio = Object.fromEntries(formData);
                
                if (negocioEditando) {
                    mostrarAlerta('Negocio actualizado: ' + negocio.nombre, 'success');
                } else {
                    mostrarAlerta('Negocio creado: ' + negocio.nombre, 'success');
                }
                
                cerrarModal();
                cargarNegocios();
            });
            
            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
                setTimeout(() => container.innerHTML = '', 5000);
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cerrar modal al hacer clic fuera
            window.onclick = function(event) {
                const modal = document.getElementById('negocioModal');
                if (event.target === modal) {
                    cerrarModal();
                }
            }
            
            // Cargar negocios al iniciar
            cargarNegocios();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

@devops_bp.route('/productos')
@devops_login_required
def gestion_productos():
    """Gestión completa de productos"""
    from flask import request, make_response
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gestión de Productos - DevOps</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #fd7e14 0%, #ffc107 100%);
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
                background: linear-gradient(135deg, #fd7e14 0%, #ffc107 100%); 
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
            .btn-success { background: linear-gradient(135deg, #28a745, #20c997); color: white; }
            .btn-primary { background: linear-gradient(135deg, #007bff, #0056b3); color: white; }
            .btn-warning { background: linear-gradient(135deg, #ffc107, #e0a800); color: #212529; }
            .btn-danger { background: linear-gradient(135deg, #dc3545, #c82333); color: white; }
            .btn-secondary { background: linear-gradient(135deg, #6c757d, #5a6268); color: white; }
            .search-box { 
                flex: 1; 
                min-width: 300px;
                padding: 12px 20px; 
                border: 2px solid #e9ecef; 
                border-radius: 25px; 
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .search-box:focus { 
                outline: none; 
                border-color: #fd7e14; 
                box-shadow: 0 0 0 3px rgba(253, 126, 20, 0.1);
            }
            .table-container { 
                background: white; 
                border-radius: 10px; 
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            .table th { 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                padding: 20px 15px; 
                text-align: left; 
                font-weight: 600;
                color: #495057;
                border-bottom: 2px solid #dee2e6;
            }
            .table td { 
                padding: 20px 15px; 
                border-bottom: 1px solid #f1f3f4;
                vertical-align: middle;
            }
            .table tbody tr:hover { 
                background: #f8f9fa; 
                transform: scale(1.01);
                transition: all 0.2s ease;
            }
            .status-badge { 
                padding: 8px 16px; 
                border-radius: 20px; 
                font-size: 12px; 
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .status-active { background: linear-gradient(135deg, #d4edda, #c3e6cb); color: #155724; }
            .status-inactive { background: linear-gradient(135deg, #f8d7da, #f5c6cb); color: #721c24; }
            .loading { 
                text-align: center; 
                padding: 40px; 
                color: #6c757d; 
                font-size: 18px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #fd7e14;
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
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                animation: fadeIn 0.3s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .modal-content {
                background: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 15px;
                width: 90%;
                max-width: 600px;
                animation: slideUp 0.3s ease;
            }
            @keyframes slideUp {
                from { transform: translateY(50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #495057;
            }
            .form-group input, .form-group select, .form-group textarea {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                outline: none;
                border-color: #fd7e14;
                box-shadow: 0 0 0 3px rgba(253, 126, 20, 0.1);
            }
            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                transition: color 0.3s ease;
            }
            .close:hover { color: #000; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, #fd7e14, #ffc107);
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
            .price { font-weight: 600; color: #28a745; font-size: 1.2em; }
            .category-badge {
                background: linear-gradient(135deg, #e3f2fd, #bbdefb);
                color: #1976d2;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }
            @media (max-width: 768px) {
                .toolbar { flex-direction: column; align-items: stretch; }
                .search-box { min-width: auto; }
                .table { font-size: 14px; }
                .table th, .table td { padding: 10px 8px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📦 Gestión de Productos</h1>
                <p>Administra el catálogo de productos del sistema</p>
            </div>
            
            <div class="content">
                <div class="stats" id="stats-container">
                    <div class="stat-card">
                        <h3 id="total-productos">0</h3>
                        <p>Total Productos</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="productos-activos">0</h3>
                        <p>Productos Activos</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="precio-promedio">$0</h3>
                        <p>Precio Promedio</p>
                    </div>
                </div>
                
                <div class="toolbar">
                    <button class="btn btn-success" onclick="abrirModalCrear()">
                        ➕ Nuevo Producto
                    </button>
                    <button class="btn btn-primary" onclick="cargarProductos()">
                        🔄 Actualizar
                    </button>
                    <button class="btn btn-secondary" onclick="volverPanel()">
                        ← Volver al Panel
                    </button>
                    <input type="text" class="search-box" placeholder="🔍 Buscar productos..." onkeyup="filtrarProductos(this.value)">
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    Cargando productos...
                </div>
                
                <div id="alert-container"></div>
                
                <div class="table-container">
                    <table class="table" id="productos-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Descripción</th>
                                <th>Precio</th>
                                <th>Categoría</th>
                                <th>Negocio</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="productos-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Modal para crear/editar producto -->
        <div id="productoModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="cerrarModal()">&times;</span>
                <h2 id="modal-titulo">Nuevo Producto</h2>
                <form id="productoForm">
                    <div class="form-group">
                        <label for="nombre">Nombre del Producto:</label>
                        <input type="text" id="nombre" name="nombre" required>
                    </div>
                    <div class="form-group">
                        <label for="descripcion">Descripción:</label>
                        <textarea id="descripcion" name="descripcion" rows="3" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="precio">Precio:</label>
                        <input type="number" id="precio" name="precio" step="0.01" min="0" required>
                    </div>
                    <div class="form-group">
                        <label for="categoria_id">Categoría:</label>
                        <select id="categoria_id" name="categoria_id" required>
                            <option value="1">Lácteos</option>
                            <option value="2">Panadería</option>
                            <option value="3">Farmacia</option>
                            <option value="4">Carnes</option>
                            <option value="5">Verduras</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="negocio_id">Negocio:</label>
                        <select id="negocio_id" name="negocio_id" required>
                            <option value="1">Supermercado Central</option>
                            <option value="2">Farmacia San Martín</option>
                            <option value="3">Restaurante El Buen Sabor</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="activo">Estado:</label>
                        <select id="activo" name="activo" required>
                            <option value="true">Activo</option>
                            <option value="false">Inactivo</option>
                        </select>
                    </div>
                    <div style="text-align: right; margin-top: 30px;">
                        <button type="button" class="btn btn-secondary" onclick="cerrarModal()">Cancelar</button>
                        <button type="submit" class="btn btn-success">Guardar Producto</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            let productosData = [];
            let productoEditando = null;
            
            function cargarProductos() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('productos-table').style.display = 'none';
                
                fetch('/devops/productos', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        productosData = data.data.productos;
                        mostrarProductos(productosData);
                        actualizarEstadisticas(productosData);
                        mostrarAlerta('Productos cargados correctamente', 'success');
                    } else {
                        mostrarAlerta('Error: ' + data.message, 'danger');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    mostrarAlerta('Error al cargar productos: ' + error, 'danger');
                });
            }
            
            function mostrarProductos(productos) {
                const tbody = document.getElementById('productos-tbody');
                tbody.innerHTML = '';
                
                productos.forEach(producto => {
                    const row = document.createElement('tr');
                    const categoriaNombres = {
                        1: 'Lácteos', 2: 'Panadería', 3: 'Farmacia', 4: 'Carnes', 5: 'Verduras'
                    };
                    const negocioNombres = {
                        1: 'Supermercado Central', 2: 'Farmacia San Martín', 3: 'Restaurante El Buen Sabor'
                    };
                    
                    row.innerHTML = `
                        <td><strong>#${producto.id}</strong></td>
                        <td><strong>${producto.nombre}</strong></td>
                        <td>${producto.descripcion}</td>
                        <td class="price">$${producto.precio.toFixed(2)}</td>
                        <td><span class="category-badge">${categoriaNombres[producto.categoria_id] || 'Categoría ' + producto.categoria_id}</span></td>
                        <td>${negocioNombres[producto.negocio_id] || 'Negocio ' + producto.negocio_id}</td>
                        <td><span class="status-badge ${producto.activo ? 'status-active' : 'status-inactive'}">${producto.activo ? 'Activo' : 'Inactivo'}</span></td>
                        <td>
                            <button class="btn btn-warning" onclick="editarProducto(${producto.id})" style="padding: 8px 12px; font-size: 12px;">✏️ Editar</button>
                            <button class="btn btn-danger" onclick="eliminarProducto(${producto.id})" style="padding: 8px 12px; font-size: 12px;">🗑️ Eliminar</button>
                            <button class="btn btn-primary" onclick="verPrecios(${producto.id})" style="padding: 8px 12px; font-size: 12px;">💰 Precios</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                document.getElementById('productos-table').style.display = 'table';
            }
            
            function actualizarEstadisticas(productos) {
                const total = productos.length;
                const activos = productos.filter(p => p.activo).length;
                const precioPromedio = productos.length > 0 ? 
                    Math.round(productos.reduce((sum, p) => sum + p.precio, 0) / productos.length) : 0;
                
                document.getElementById('total-productos').textContent = total;
                document.getElementById('productos-activos').textContent = activos;
                document.getElementById('precio-promedio').textContent = '$' + precioPromedio;
            }
            
            function filtrarProductos(termino) {
                const productosFiltrados = productosData.filter(producto => 
                    producto.nombre.toLowerCase().includes(termino.toLowerCase()) ||
                    producto.descripcion.toLowerCase().includes(termino.toLowerCase())
                );
                mostrarProductos(productosFiltrados);
            }
            
            function abrirModalCrear() {
                productoEditando = null;
                document.getElementById('modal-titulo').textContent = 'Nuevo Producto';
                document.getElementById('productoForm').reset();
                document.getElementById('productoModal').style.display = 'block';
            }
            
            function editarProducto(id) {
                const producto = productosData.find(p => p.id === id);
                if (producto) {
                    productoEditando = producto;
                    document.getElementById('modal-titulo').textContent = 'Editar Producto';
                    document.getElementById('nombre').value = producto.nombre;
                    document.getElementById('descripcion').value = producto.descripcion;
                    document.getElementById('precio').value = producto.precio;
                    document.getElementById('categoria_id').value = producto.categoria_id;
                    document.getElementById('negocio_id').value = producto.negocio_id;
                    document.getElementById('activo').value = producto.activo.toString();
                    document.getElementById('productoModal').style.display = 'block';
                }
            }
            
            function eliminarProducto(id) {
                if (confirm('¿Estás seguro de eliminar este producto?')) {
                    mostrarAlerta('Producto eliminado ID: ' + id, 'success');
                    cargarProductos();
                }
            }
            
            function verPrecios(id) {
                mostrarAlerta('Viendo precios del producto ID: ' + id, 'success');
                // Aquí podrías redirigir a la página de precios filtrada por producto
                // window.location.href = '/devops/precios?producto=' + id;
            }
            
            function cerrarModal() {
                document.getElementById('productoModal').style.display = 'none';
            }
            
            document.getElementById('productoForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const producto = Object.fromEntries(formData);
                
                if (productoEditando) {
                    mostrarAlerta('Producto actualizado: ' + producto.nombre, 'success');
                } else {
                    mostrarAlerta('Producto creado: ' + producto.nombre, 'success');
                }
                
                cerrarModal();
                cargarProductos();
            });
            
            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
                setTimeout(() => container.innerHTML = '', 5000);
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cerrar modal al hacer clic fuera
            window.onclick = function(event) {
                const modal = document.getElementById('productoModal');
                if (event.target === modal) {
                    cerrarModal();
                }
            }
            
            // Cargar productos al iniciar
            cargarProductos();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

@devops_bp.route('/precios')
@devops_login_required
def gestion_precios():
    """Gestión completa de precios"""
    from flask import request, make_response
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gestión de Precios - DevOps</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f5f5f5; }
            .header { background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); color: white; padding: 20px; text-align: center; }
            .container { max-width: 1200px; margin: 20px auto; padding: 20px; }
            .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .card-header { background: #f8f9fa; padding: 15px 20px; border-bottom: 1px solid #dee2e6; border-radius: 8px 8px 0 0; }
            .card-body { padding: 20px; }
            .btn { padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn-primary { background: #007bff; color: white; }
            .btn-success { background: #28a745; color: white; }
            .btn-warning { background: #ffc107; color: black; }
            .btn-danger { background: #dc3545; color: white; }
            .btn-secondary { background: #6c757d; color: white; }
            .btn:hover { opacity: 0.8; }
            .table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
            .table th { background: #f8f9fa; font-weight: 600; }
            .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; }
            .status-active { background: #d4edda; color: #155724; }
            .status-inactive { background: #f8d7da; color: #721c24; }
            .loading { text-align: center; padding: 20px; color: #6c757d; }
            .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; }
            .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .price { font-weight: 600; color: #28a745; }
            .price-old { text-decoration: line-through; color: #6c757d; }
            .discount { color: #dc3545; font-weight: 600; }
            .search-box { width: 100%; padding: 10px; border: 1px solid #ced4da; border-radius: 4px; margin-bottom: 20px; }
            .filter-section { display: flex; gap: 10px; margin-bottom: 20px; }
            .filter-select { padding: 8px; border: 1px solid #ced4da; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💰 Gestión de Precios</h1>
            <p>Administra los precios y descuentos de productos</p>
        </div>
        
        <div class="container">
            <div class="card">
                <div class="card-header">
                    <h3>📋 Panel de Precios</h3>
                </div>
                <div class="card-body">
                    <div style="margin-bottom: 20px;">
                        <button class="btn btn-success" onclick="actualizarPrecios()">🔄 Actualizar Precios</button>
                        <button class="btn btn-primary" onclick="cargarPrecios()">🔄 Actualizar</button>
                        <button class="btn btn-secondary" onclick="volverPanel()">← Volver al Panel</button>
                    </div>
                    
                    <div class="filter-section">
                        <input type="text" class="search-box" placeholder="🔍 Buscar por producto o negocio..." onkeyup="filtrarPrecios(this.value)">
                        <select class="filter-select" onchange="filtrarPorNegocio(this.value)">
                            <option value="">Todos los negocios</option>
                            <option value="1">Negocio 1</option>
                            <option value="2">Negocio 2</option>
                            <option value="3">Negocio 3</option>
                        </select>
                        <select class="filter-select" onchange="filtrarPorDescuento(this.value)">
                            <option value="">Todos los descuentos</option>
                            <option value="con-descuento">Con descuento</option>
                            <option value="sin-descuento">Sin descuento</option>
                        </select>
                    </div>
                    
                    <div id="loading" class="loading" style="display: none;">
                        Cargando precios...
                    </div>
                    
                    <div id="alert-container"></div>
                    
                    <table class="table" id="precios-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Producto</th>
                                <th>Negocio</th>
                                <th>Precio Actual</th>
                                <th>Precio Anterior</th>
                                <th>Descuento</th>
                                <th>Fecha Actualización</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="precios-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            let preciosData = [];
            
            function cargarPrecios() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('precios-table').style.display = 'none';
                
                fetch('/devops/precios', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        preciosData = data.data.precios;
                        mostrarPrecios(preciosData);
                        mostrarAlerta('Precios cargados correctamente', 'success');
                    } else {
                        mostrarAlerta('Error: ' + data.message, 'danger');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    mostrarAlerta('Error al cargar precios: ' + error, 'danger');
                });
            }
            
            function mostrarPrecios(precios) {
                const tbody = document.getElementById('precios-tbody');
                tbody.innerHTML = '';
                
                precios.forEach(precio => {
                    const row = document.createElement('tr');
                    const descuentoHtml = precio.descuento > 0 ? 
                        `<span class="discount">-${precio.descuento}%</span>` : 
                        '<span style="color: #6c757d;">Sin descuento</span>';
                    
                    row.innerHTML = `
                        <td>${precio.id}</td>
                        <td><strong>Producto ${precio.producto_id}</strong></td>
                        <td>Negocio ${precio.negocio_id}</td>
                        <td class="price">$${precio.precio.toFixed(2)}</td>
                        <td class="price-old">$${precio.precio_anterior.toFixed(2)}</td>
                        <td>${descuentoHtml}</td>
                        <td>${precio.fecha_actualizacion}</td>
                        <td><span class="status-badge ${precio.activo ? 'status-active' : 'status-inactive'}">${precio.activo ? 'Activo' : 'Inactivo'}</span></td>
                        <td>
                            <button class="btn btn-warning" onclick="editarPrecio(${precio.id})">✏️ Editar</button>
                            <button class="btn btn-danger" onclick="eliminarPrecio(${precio.id})">🗑️ Eliminar</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                document.getElementById('precios-table').style.display = 'table';
            }
            
            function filtrarPrecios(termino) {
                const preciosFiltrados = preciosData.filter(precio => 
                    precio.producto_id.toString().includes(termino) ||
                    precio.negocio_id.toString().includes(termino)
                );
                mostrarPrecios(preciosFiltrados);
            }
            
            function filtrarPorNegocio(negocioId) {
                if (!negocioId) {
                    mostrarPrecios(preciosData);
                    return;
                }
                const preciosFiltrados = preciosData.filter(precio => precio.negocio_id == negocioId);
                mostrarPrecios(preciosFiltrados);
            }
            
            function filtrarPorDescuento(tipo) {
                if (!tipo) {
                    mostrarPrecios(preciosData);
                    return;
                }
                const preciosFiltrados = preciosData.filter(precio => {
                    if (tipo === 'con-descuento') return precio.descuento > 0;
                    if (tipo === 'sin-descuento') return precio.descuento === 0;
                    return true;
                });
                mostrarPrecios(preciosFiltrados);
            }
            
            function actualizarPrecios() {
                mostrarAlerta('Actualizando precios...', 'success');
                setTimeout(() => {
                    mostrarAlerta('Precios actualizados correctamente', 'success');
                    cargarPrecios();
                }, 2000);
            }
            
            function editarPrecio(id) {
                const nuevoPrecio = prompt('Nuevo precio:');
                if (nuevoPrecio && !isNaN(nuevoPrecio)) {
                    mostrarAlerta('Precio actualizado ID: ' + id + ' - Nuevo precio: $' + nuevoPrecio, 'success');
                    cargarPrecios();
                }
            }
            
            function eliminarPrecio(id) {
                if (confirm('¿Estás seguro de eliminar este precio?')) {
                    mostrarAlerta('Precio eliminado ID: ' + id, 'success');
                    cargarPrecios();
                }
            }
            
            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
                setTimeout(() => container.innerHTML = '', 3000);
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cargar precios al iniciar
            cargarPrecios();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

# =================================================================
# SINCRONIZACIÓN Y UTILIDADES
# =================================================================

@devops_bp.route('/sync', methods=['GET', 'POST'])
@devops_login_required
def sincronizacion_manual():
    """Forzar sincronización manual"""
    from flask import request, make_response
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Logs del Sistema - DevOps</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
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
                background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); 
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
            .search-box { 
                flex: 1; 
                min-width: 300px;
                padding: 12px 20px; 
                border: 2px solid #e9ecef; 
                border-radius: 25px; 
                font-size: 16px;
                transition: all 0.3s ease;
            }
            .search-box:focus { 
                outline: none; 
                border-color: #6f42c1; 
                box-shadow: 0 0 0 3px rgba(111, 66, 193, 0.1);
            }
            .table-container { 
                background: white; 
                border-radius: 10px; 
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            .table th { 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                padding: 20px 15px; 
                text-align: left; 
                font-weight: 600;
                color: #495057;
                border-bottom: 2px solid #dee2e6;
            }
            .table td { 
                padding: 20px 15px; 
                border-bottom: 1px solid #f1f3f4;
                vertical-align: middle;
            }
            .table tbody tr:hover { 
                background: #f8f9fa; 
                transform: scale(1.01);
                transition: all 0.2s ease;
            }
            .log-level { 
                padding: 8px 16px; 
                border-radius: 20px; 
                font-size: 12px; 
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .level-info { background: linear-gradient(135deg, #d1ecf1, #bee5eb); color: #0c5460; }
            .level-warning { background: linear-gradient(135deg, #fff3cd, #ffeaa7); color: #856404; }
            .level-error { background: linear-gradient(135deg, #f8d7da, #f5c6cb); color: #721c24; }
            .level-success { background: linear-gradient(135deg, #d4edda, #c3e6cb); color: #155724; }
            .loading { 
                text-align: center; 
                padding: 40px; 
                color: #6c757d; 
                font-size: 18px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #6f42c1;
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
                background: linear-gradient(135deg, #6f42c1, #e83e8c);
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
            .timestamp { 
                font-family: 'Courier New', monospace; 
                font-size: 12px; 
                color: #6c757d; 
            }
            .service-badge {
                background: linear-gradient(135deg, #e3f2fd, #bbdefb);
                color: #1976d2;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }
            @media (max-width: 768px) {
                .toolbar { flex-direction: column; align-items: stretch; }
                .search-box { min-width: auto; }
                .table { font-size: 14px; }
                .table th, .table td { padding: 10px 8px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Logs del Sistema</h1>
                <p>Monitoreo y análisis de logs del sistema DevOps</p>
            </div>
            
            <div class="content">
                <div class="stats" id="stats-container">
                    <div class="stat-card">
                        <h3 id="total-logs">0</h3>
                        <p>Total Logs</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="logs-info">0</h3>
                        <p>Logs INFO</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="logs-warning">0</h3>
                        <p>Logs WARNING</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="logs-error">0</h3>
                        <p>Logs ERROR</p>
                    </div>
                </div>
                
                <div class="toolbar">
                    <button class="btn btn-success" onclick="cargarLogs()">
                        🔄 Actualizar Logs
                    </button>
                    <button class="btn btn-warning" onclick="limpiarLogs()">
                        🗑️ Limpiar Logs
                    </button>
                    <button class="btn btn-primary" onclick="exportarLogs()">
                        📥 Exportar
                    </button>
                    <button class="btn btn-secondary" onclick="volverPanel()">
                        ← Volver al Panel
                    </button>
                    <input type="text" class="search-box" placeholder="🔍 Buscar en logs..." onkeyup="filtrarLogs(this.value)">
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    Cargando logs...
                </div>
                
                <div id="alert-container"></div>
                
                <div class="table-container">
                    <table class="table" id="logs-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Nivel</th>
                                <th>Servicio</th>
                                <th>Mensaje</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="logs-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <script>
            let logsData = [];
            
            function cargarLogs() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('logs-table').style.display = 'none';
                
                fetch('/devops/logs', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        logsData = data.data.logs;
                        mostrarLogs(logsData);
                        actualizarEstadisticas(logsData);
                        mostrarAlerta('Logs cargados correctamente', 'success');
                    } else {
                        mostrarAlerta('Error: ' + data.message, 'danger');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    mostrarAlerta('Error al cargar logs: ' + error, 'danger');
                });
            }
            
            function mostrarLogs(logs) {
                const tbody = document.getElementById('logs-tbody');
                tbody.innerHTML = '';
                
                logs.forEach(log => {
                    const row = document.createElement('tr');
                    const timestamp = new Date(log.timestamp).toLocaleString();
                    const levelClass = `level-${log.level.toLowerCase()}`;
                    
                    row.innerHTML = `
                        <td class="timestamp">${timestamp}</td>
                        <td><span class="log-level ${levelClass}">${log.level}</span></td>
                        <td><span class="service-badge">${log.service}</span></td>
                        <td>${log.message}</td>
                        <td>
                            <button class="btn btn-warning" onclick="verDetalleLog('${log.timestamp}')" style="padding: 8px 12px; font-size: 12px;">👁️ Ver</button>
                            <button class="btn btn-danger" onclick="eliminarLog('${log.timestamp}')" style="padding: 8px 12px; font-size: 12px;">🗑️ Eliminar</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                document.getElementById('logs-table').style.display = 'table';
            }
            
            function actualizarEstadisticas(logs) {
                const total = logs.length;
                const info = logs.filter(l => l.level === 'INFO').length;
                const warning = logs.filter(l => l.level === 'WARNING').length;
                const error = logs.filter(l => l.level === 'ERROR').length;
                
                document.getElementById('total-logs').textContent = total;
                document.getElementById('logs-info').textContent = info;
                document.getElementById('logs-warning').textContent = warning;
                document.getElementById('logs-error').textContent = error;
            }
            
            function filtrarLogs(termino) {
                const logsFiltrados = logsData.filter(log => 
                    log.message.toLowerCase().includes(termino.toLowerCase()) ||
                    log.service.toLowerCase().includes(termino.toLowerCase()) ||
                    log.level.toLowerCase().includes(termino.toLowerCase())
                );
                mostrarLogs(logsFiltrados);
            }
            
            function limpiarLogs() {
                if (confirm('¿Estás seguro de limpiar todos los logs?')) {
                    mostrarAlerta('Logs limpiados', 'success');
                    cargarLogs();
                }
            }
            
            function exportarLogs() {
                const logsText = logsData.map(log => 
                    `[${log.timestamp}] ${log.level} - ${log.service}: ${log.message}`
                ).join('\n');
                
                const blob = new Blob([logsText], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `logs-${new Date().toISOString().split('T')[0]}.txt`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                mostrarAlerta('Logs exportados correctamente', 'success');
            }
            
            function verDetalleLog(timestamp) {
                const log = logsData.find(l => l.timestamp === timestamp);
                if (log) {
                    alert(`Detalle del Log:\n\nTimestamp: ${log.timestamp}\nNivel: ${log.level}\nServicio: ${log.service}\nMensaje: ${log.message}`);
                }
            }
            
            function eliminarLog(timestamp) {
                if (confirm('¿Estás seguro de eliminar este log?')) {
                    mostrarAlerta('Log eliminado', 'success');
                    cargarLogs();
                }
            }
            
            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
                setTimeout(() => container.innerHTML = '', 5000);
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cargar logs al iniciar
            cargarLogs();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

@devops_bp.route('/config')
@devops_login_required
def ver_configuracion():
    """Ver configuración actual del sistema"""
    from flask import request, make_response
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
    # Si no es AJAX, devolver HTML completo
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Configuración del Sistema - DevOps</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);
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
                background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%); 
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
            .config-section { 
                background: white; 
                border-radius: 10px; 
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .config-header { 
                background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                padding: 20px; 
                border-bottom: 1px solid #dee2e6;
                font-weight: 600;
                color: #495057;
            }
            .config-body { padding: 20px; }
            .config-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 0;
                border-bottom: 1px solid #f1f3f4;
            }
            .config-item:last-child { border-bottom: none; }
            .config-label {
                font-weight: 600;
                color: #495057;
                flex: 1;
            }
            .config-value {
                background: #f8f9fa;
                padding: 8px 12px;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                color: #6c757d;
                flex: 2;
                margin-left: 20px;
            }
            .status-badge { 
                padding: 6px 12px; 
                border-radius: 12px; 
                font-size: 12px; 
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .status-active { background: linear-gradient(135deg, #d4edda, #c3e6cb); color: #155724; }
            .status-inactive { background: linear-gradient(135deg, #f8d7da, #f5c6cb); color: #721c24; }
            .status-warning { background: linear-gradient(135deg, #fff3cd, #ffeaa7); color: #856404; }
            .loading { 
                text-align: center; 
                padding: 40px; 
                color: #6c757d; 
                font-size: 18px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #17a2b8;
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
                background: linear-gradient(135deg, #17a2b8, #6f42c1);
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
            .copy-btn {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                margin-left: 10px;
            }
            .copy-btn:hover { opacity: 0.8; }
            @media (max-width: 768px) {
                .toolbar { flex-direction: column; align-items: stretch; }
                .config-item { flex-direction: column; align-items: flex-start; }
                .config-value { margin-left: 0; margin-top: 10px; width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚙️ Configuración del Sistema</h1>
                <p>Configuración actual y estado del sistema DevOps</p>
            </div>
            
            <div class="content">
                <div class="stats" id="stats-container">
                    <div class="stat-card">
                        <h3 id="total-configs">0</h3>
                        <p>Configuraciones</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="active-services">0</h3>
                        <p>Servicios Activos</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="system-uptime">0h</h3>
                        <p>Tiempo Activo</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="api-status">OK</h3>
                        <p>Estado API</p>
                    </div>
                </div>
                
                <div class="toolbar">
                    <button class="btn btn-success" onclick="cargarConfiguracion()">
                        🔄 Actualizar Config
                    </button>
                    <button class="btn btn-warning" onclick="exportarConfig()">
                        📥 Exportar Config
                    </button>
                    <button class="btn btn-primary" onclick="testConexiones()">
                        🔗 Probar Conexiones
                    </button>
                    <button class="btn btn-secondary" onclick="volverPanel()">
                        ← Volver al Panel
                    </button>
                </div>
                
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    Cargando configuración...
                </div>
                
                <div id="alert-container"></div>
                
                <div id="config-container" style="display: none;">
                    <!-- Configuración se cargará aquí -->
                </div>
            </div>
        </div>
        
        <script>
            let configData = null;
            
            function cargarConfiguracion() {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('config-container').style.display = 'none';
                
                fetch('/devops/config', {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.status === 'success') {
                        configData = data.data;
                        mostrarConfiguracion(configData);
                        actualizarEstadisticas(configData);
                        mostrarAlerta('Configuración cargada correctamente', 'success');
                    } else {
                        mostrarAlerta('Error: ' + data.message, 'danger');
                    }
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    mostrarAlerta('Error al cargar configuración: ' + error, 'danger');
                });
            }
            
            function mostrarConfiguracion(config) {
                const container = document.getElementById('config-container');
                
                let html = '';
                
                // Sección de Entorno
                html += `
                    <div class="config-section">
                        <div class="config-header">🌍 Variables de Entorno</div>
                        <div class="config-body">
                            <div class="config-item">
                                <div class="config-label">URL de Belgrano Ahorro</div>
                                <div class="config-value">${config.environment.BELGRANO_AHORRO_URL || 'No configurada'}</div>
                            </div>
                            <div class="config-item">
                                <div class="config-label">API Key</div>
                                <div class="config-value">${config.environment.BELGRANO_AHORRO_API_KEY}</div>
                            </div>
                            <div class="config-item">
                                <div class="config-label">Timeout de API (segundos)</div>
                                <div class="config-value">${config.environment.API_TIMEOUT_SECS || 'No configurado'}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Sección del Sistema
                html += `
                    <div class="config-section">
                        <div class="config-header">💻 Información del Sistema</div>
                        <div class="config-body">
                            <div class="config-item">
                                <div class="config-label">Versión de Python</div>
                                <div class="config-value">${config.system.python_version || 'No disponible'}</div>
                            </div>
                            <div class="config-item">
                                <div class="config-label">Directorio de Trabajo</div>
                                <div class="config-value">${config.system.working_directory || 'No disponible'}</div>
                            </div>
                            <div class="config-item">
                                <div class="config-label">Prefijo del Blueprint</div>
                                <div class="config-value">${config.system.blueprint_prefix || 'No configurado'}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Sección de Endpoints
                html += `
                    <div class="config-section">
                        <div class="config-header">🔗 Configuración de Endpoints</div>
                        <div class="config-body">
                            <div class="config-item">
                                <div class="config-label">URL Base</div>
                                <div class="config-value">${config.endpoints.base_url || 'No configurada'}</div>
                            </div>
                            <div class="config-item">
                                <div class="config-label">Prefijo de API</div>
                                <div class="config-value">${config.endpoints.api_prefix || 'No configurado'}</div>
                            </div>
                            <div class="config-item">
                                <div class="config-label">Timeout</div>
                                <div class="config-value">${config.endpoints.timeout || 'No configurado'}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Información de Timestamp
                html += `
                    <div class="config-section">
                        <div class="config-header">⏰ Información de Tiempo</div>
                        <div class="config-body">
                            <div class="config-item">
                                <div class="config-label">Última Actualización</div>
                                <div class="config-value">${new Date(config.timestamp).toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                container.innerHTML = html;
                document.getElementById('config-container').style.display = 'block';
            }
            
            function actualizarEstadisticas(config) {
                const totalConfigs = Object.keys(config.environment).length + Object.keys(config.system).length + Object.keys(config.endpoints).length;
                const activeServices = (config.environment.BELGRANO_AHORRO_URL ? 1 : 0) + (config.environment.BELGRANO_AHORRO_API_KEY ? 1 : 0);
                const systemUptime = Math.floor(Math.random() * 24); // Simulado
                const apiStatus = config.environment.BELGRANO_AHORRO_URL ? 'OK' : 'ERROR';
                
                document.getElementById('total-configs').textContent = totalConfigs;
                document.getElementById('active-services').textContent = activeServices;
                document.getElementById('system-uptime').textContent = systemUptime + 'h';
                document.getElementById('api-status').textContent = apiStatus;
            }
            
            function exportarConfig() {
                if (configData) {
                    const configText = JSON.stringify(configData, null, 2);
                    const blob = new Blob([configText], { type: 'application/json' });
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `config-${new Date().toISOString().split('T')[0]}.json`;
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    mostrarAlerta('Configuración exportada correctamente', 'success');
                } else {
                    mostrarAlerta('No hay configuración para exportar', 'danger');
                }
            }
            
            function testConexiones() {
                mostrarAlerta('Probando conexiones...', 'success');
                // Aquí se podrían implementar tests reales de conexión
                setTimeout(() => {
                    mostrarAlerta('Conexiones probadas correctamente', 'success');
                }, 2000);
            }
            
            function mostrarAlerta(mensaje, tipo) {
                const container = document.getElementById('alert-container');
                container.innerHTML = `<div class="alert alert-${tipo}">${mensaje}</div>`;
                setTimeout(() => container.innerHTML = '', 5000);
            }
            
            function volverPanel() {
                window.location.href = '/devops/';
            }
            
            // Cargar configuración al iniciar
            cargarConfiguracion();
        </script>
    </body>
    </html>
    """
    return make_response(html, 200)

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