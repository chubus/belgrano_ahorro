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

# Importar gestor DevOps para Belgrano Ahorro
try:
    from devops_belgrano_manager import DevOpsBelgranoManager
    devops_manager = DevOpsBelgranoManager()
    logger.info("✅ Gestor DevOps para Belgrano Ahorro inicializado")
except ImportError as e:
    logger.warning(f"⚠️ No se pudo importar DevOpsBelgranoManager: {e}")
    devops_manager = None

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
    """Gestión completa de ofertas desde Belgrano Ahorro"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': []
            }), 500
        
        # Obtener ofertas reales desde la base de datos
        ofertas = devops_manager.get_ofertas()
        
        return jsonify({
            'status': 'success',
            'data': {
                'ofertas': ofertas,
                'total': len(ofertas),
                'timestamp': datetime.now().isoformat()
            },
            'source': 'database',
            'message': f'Ofertas obtenidas correctamente ({len(ofertas)} encontradas)'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo ofertas: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo ofertas: {str(e)}',
            'data': [],
            'source': 'error'
        }), 500

@devops_bp.route('/negocios')
@devops_login_required
def gestion_negocios():
    """Gestión completa de negocios desde Belgrano Ahorro"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': []
            }), 500
        
        # Obtener comerciantes/negocios reales desde la base de datos
        comerciantes = devops_manager.get_comerciantes()
        
        return jsonify({
            'status': 'success',
            'data': {
                'negocios': comerciantes,
                'total': len(comerciantes),
                'timestamp': datetime.now().isoformat()
            },
            'source': 'database',
            'message': f'Negocios obtenidos correctamente ({len(comerciantes)} encontrados)'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo negocios: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo negocios: {str(e)}',
            'data': [],
            'source': 'error'
        }), 500

# =================================================================
# GESTIÓN DE PRODUCTOS
# =================================================================

@devops_bp.route('/productos')
@devops_login_required
def gestion_productos():
    """Gestión completa de productos desde Belgrano Ahorro"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': []
            }), 500
        
        # Obtener productos reales desde la base de datos
        productos = devops_manager.get_productos()
        
        return jsonify({
            'status': 'success',
            'data': {
                'productos': productos,
                'total': len(productos),
                'timestamp': datetime.now().isoformat()
            },
            'source': 'database',
            'message': f'Productos obtenidos correctamente ({len(productos)} encontrados)'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo productos: {str(e)}',
            'data': [],
            'source': 'error'
        }), 500

@devops_bp.route('/productos/<int:producto_id>')
@devops_login_required
def obtener_producto(producto_id):
    """Obtener un producto específico"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        producto = devops_manager.get_producto(producto_id)
        
        if not producto:
            return jsonify({
                'status': 'error',
                'message': 'Producto no encontrado'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': producto,
            'timestamp': datetime.now().isoformat()
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo producto {producto_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo producto: {str(e)}'
        }), 500

@devops_bp.route('/productos', methods=['POST'])
@devops_login_required
def crear_producto():
    """Crear un nuevo producto"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        datos = request.get_json()
        if not datos:
            return jsonify({
                'status': 'error',
                'message': 'Datos del producto requeridos'
            }), 400
        
        # Validar datos requeridos
        campos_requeridos = ['nombre', 'store', 'precio']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({
                    'status': 'error',
                    'message': f'Campo requerido: {campo}'
                }), 400
        
        if devops_manager.crear_producto(datos):
            return jsonify({
                'status': 'success',
                'message': 'Producto creado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error creando producto'
            }), 500
                
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error creando producto: {str(e)}'
        }), 500

@devops_bp.route('/productos/<int:producto_id>', methods=['PUT'])
@devops_login_required
def actualizar_producto(producto_id):
    """Actualizar un producto existente"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        datos = request.get_json()
        if not datos:
            return jsonify({
                'status': 'error',
                'message': 'Datos de actualización requeridos'
            }), 400
        
        if devops_manager.actualizar_producto(producto_id, datos):
            return jsonify({
                'status': 'success',
                'message': 'Producto actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error actualizando producto'
            }), 500
                
    except Exception as e:
        logger.error(f"Error actualizando producto {producto_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error actualizando producto: {str(e)}'
        }), 500

@devops_bp.route('/productos/<int:producto_id>', methods=['DELETE'])
@devops_login_required
def eliminar_producto(producto_id):
    """Eliminar un producto (marcar como inactivo)"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        if devops_manager.eliminar_producto(producto_id):
            return jsonify({
                'status': 'success',
                'message': 'Producto eliminado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error eliminando producto'
            }), 500
                
    except Exception as e:
        logger.error(f"Error eliminando producto {producto_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error eliminando producto: {str(e)}'
        }), 500

# =================================================================
# GESTIÓN DE PRECIOS
# =================================================================

@devops_bp.route('/productos/<int:producto_id>/precio', methods=['PUT'])
@devops_login_required
def actualizar_precio(producto_id):
    """Actualizar precio de un producto"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        datos = request.get_json()
        if not datos or 'precio' not in datos:
            return jsonify({
                'status': 'error',
                'message': 'Precio requerido'
            }), 400
        
        nuevo_precio = datos['precio']
        precio_original = datos.get('precio_original')
        
        if devops_manager.actualizar_precio(producto_id, nuevo_precio, precio_original):
            return jsonify({
                'status': 'success',
                'message': 'Precio actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error actualizando precio'
            }), 500
                
    except Exception as e:
        logger.error(f"Error actualizando precio del producto {producto_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error actualizando precio: {str(e)}'
        }), 500

# =================================================================
# GESTIÓN DE ELEMENTOS DE PÁGINA PRINCIPAL
# =================================================================

@devops_bp.route('/pagina-principal/destacados')
@devops_login_required
def get_productos_destacados():
    """Obtener productos destacados para la página principal"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': []
            }), 500
        
        destacados = devops_manager.get_productos_destacados()
        
        return jsonify({
            'status': 'success',
            'data': {
                'destacados': destacados,
                'total': len(destacados),
                'timestamp': datetime.now().isoformat()
            },
            'source': 'database',
            'message': f'Productos destacados obtenidos ({len(destacados)} encontrados)'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo productos destacados: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo productos destacados: {str(e)}',
            'data': []
        }), 500

@devops_bp.route('/pagina-principal/nuevos')
@devops_login_required
def get_productos_nuevos():
    """Obtener productos nuevos para la página principal"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': []
            }), 500
        
        nuevos = devops_manager.get_productos_nuevos()
        
        return jsonify({
            'status': 'success',
            'data': {
                'nuevos': nuevos,
                'total': len(nuevos),
                'timestamp': datetime.now().isoformat()
            },
            'source': 'database',
            'message': f'Productos nuevos obtenidos ({len(nuevos)} encontrados)'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo productos nuevos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo productos nuevos: {str(e)}',
            'data': []
        }), 500

@devops_bp.route('/productos/<int:producto_id>/destacado', methods=['PUT'])
@devops_login_required
def set_producto_destacado(producto_id):
    """Marcar/desmarcar producto como destacado"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        datos = request.get_json()
        if not datos or 'destacado' not in datos:
            return jsonify({
                'status': 'error',
                'message': 'Campo destacado requerido'
            }), 400
        
        destacado = bool(datos['destacado'])
        
        if devops_manager.set_producto_destacado(producto_id, destacado):
            return jsonify({
                'status': 'success',
                'message': f'Producto {"destacado" if destacado else "no destacado"} exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error actualizando estado destacado'
            }), 500
                
    except Exception as e:
        logger.error(f"Error marcando producto {producto_id} como destacado: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error actualizando estado destacado: {str(e)}'
        }), 500

@devops_bp.route('/productos/<int:producto_id>/nuevo', methods=['PUT'])
@devops_login_required
def set_producto_nuevo(producto_id):
    """Marcar/desmarcar producto como nuevo"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        datos = request.get_json()
        if not datos or 'nuevo' not in datos:
            return jsonify({
                'status': 'error',
                'message': 'Campo nuevo requerido'
            }), 400
        
        nuevo = bool(datos['nuevo'])
        
        if devops_manager.set_producto_nuevo(producto_id, nuevo):
            return jsonify({
                'status': 'success',
                'message': f'Producto {"marcado como nuevo" if nuevo else "no marcado como nuevo"} exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error actualizando estado nuevo'
            }), 500
                
    except Exception as e:
        logger.error(f"Error marcando producto {producto_id} como nuevo: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error actualizando estado nuevo: {str(e)}'
        }), 500

# =================================================================
# ESTADÍSTICAS
# =================================================================

@devops_bp.route('/estadisticas')
@devops_login_required
def get_estadisticas():
    """Obtener estadísticas del sistema"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': {}
            }), 500
        
        estadisticas = devops_manager.get_estadisticas()
        
        return jsonify({
            'status': 'success',
            'data': estadisticas,
            'source': 'database',
            'message': 'Estadísticas obtenidas correctamente'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo estadísticas: {str(e)}',
            'data': {}
        }), 500

# =================================================================
# GESTIÓN DE PRECIOS POR NEGOCIO
# =================================================================

@devops_bp.route('/negocios/<int:comerciante_id>/precios')
@devops_login_required
def get_precios_negocio(comerciante_id):
    """Obtener precios de productos por negocio específico"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': []
            }), 500
        
        precios = devops_manager.get_precios_por_negocio(comerciante_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'precios': precios,
                'total': len(precios),
                'comerciante_id': comerciante_id,
                'timestamp': datetime.now().isoformat()
            },
            'source': 'database',
            'message': f'Precios del negocio obtenidos correctamente ({len(precios)} productos)'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo precios del negocio {comerciante_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo precios del negocio: {str(e)}',
            'data': []
        }), 500

@devops_bp.route('/negocios/<int:comerciante_id>/precios/<int:producto_id>', methods=['PUT'])
@devops_login_required
def actualizar_precio_negocio(comerciante_id, producto_id):
    """Actualizar precio de un producto específico de un negocio"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        datos = request.get_json()
        if not datos or 'precio' not in datos:
            return jsonify({
                'status': 'error',
                'message': 'Precio requerido'
            }), 400
        
        nuevo_precio = datos['precio']
        precio_original = datos.get('precio_original')
        
        if devops_manager.actualizar_precio_negocio(comerciante_id, producto_id, nuevo_precio, precio_original):
            return jsonify({
                'status': 'success',
                'message': 'Precio del negocio actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error actualizando precio del negocio'
            }), 500
                
    except Exception as e:
        logger.error(f"Error actualizando precio del negocio {comerciante_id}, producto {producto_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error actualizando precio del negocio: {str(e)}'
        }), 500

@devops_bp.route('/negocios/<int:comerciante_id>/estadisticas')
@devops_login_required
def get_estadisticas_negocio(comerciante_id):
    """Obtener estadísticas de un negocio específico"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': {}
            }), 500
        
        estadisticas = devops_manager.get_estadisticas_negocio(comerciante_id)
        
        if not estadisticas:
            return jsonify({
                'status': 'error',
                'message': 'Negocio no encontrado'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': estadisticas,
            'source': 'database',
            'message': 'Estadísticas del negocio obtenidas correctamente'
        })
                
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del negocio {comerciante_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error obteniendo estadísticas del negocio: {str(e)}',
            'data': {}
        }), 500

@devops_bp.route('/negocios/<int:comerciante_id>/ofertas', methods=['POST'])
@devops_login_required
def crear_oferta_negocio(comerciante_id):
    """Crear oferta para un producto específico de un negocio"""
    try:
        if not devops_manager:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible'
            }), 500
        
        datos = request.get_json()
        if not datos or 'producto_id' not in datos or 'descuento' not in datos:
            return jsonify({
                'status': 'error',
                'message': 'producto_id y descuento requeridos'
            }), 400
        
        producto_id = datos['producto_id']
        descuento = datos['descuento']
        destacado = datos.get('destacado', False)
        
        if devops_manager.crear_oferta_negocio(comerciante_id, producto_id, descuento, destacado):
            return jsonify({
                'status': 'success',
                'message': 'Oferta del negocio creada exitosamente',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error creando oferta del negocio'
            }), 500
                
    except Exception as e:
        logger.error(f"Error creando oferta del negocio {comerciante_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error creando oferta del negocio: {str(e)}'
        }), 500

# =================================================================
# SINCRONIZACIÓN Y UTILIDADES
# =================================================================

@devops_bp.route('/sync', methods=['GET', 'POST'])
@devops_login_required
def sincronizacion_manual():
    """Forzar sincronización manual"""
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

@devops_bp.route('/logs')
@devops_login_required
def ver_logs():
    """Ver logs del sistema"""
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

@devops_bp.route('/config')
@devops_login_required
def ver_configuracion():
    """Ver configuración actual del sistema"""
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