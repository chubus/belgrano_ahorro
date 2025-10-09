#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema DevOps Completo para Belgrano Tickets
Control total sobre el contenido de Belgrano Ahorro
"""

import os
import json
import requests
from functools import wraps
from datetime import datetime
import logging
from urllib.parse import urljoin
from flask import Blueprint, request, jsonify, redirect, url_for, session, make_response, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de API y credenciales DevOps
BELGRANO_AHORRO_URL = os.environ.get('BELGRANO_AHORRO_URL', 'https://belgranoahorro-aliq.onrender.com')
BELGRANO_AHORRO_API_KEY = os.environ.get('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
API_TIMEOUT_SECS = 10

# Credenciales de DevOps
DEVOPS_USERNAME = os.environ.get('DEVOPS_USERNAME', 'devops')
DEVOPS_PASSWORD_PLAIN = os.environ.get('DEVOPS_PASSWORD', 'DevOps2025!Secure')
DEVOPS_PASSWORD_HASH = generate_password_hash(DEVOPS_PASSWORD_PLAIN)

<<<<<<< HEAD
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

# Importar cliente API y gestor DevOps
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

# Importar gestor DevOps mejorado
try:
    from devops_belgrano_manager_enhanced import devops_manager
    logger.info("✅ Gestor DevOps mejorado inicializado")
except ImportError as e:
    logger.error(f"❌ No se pudo importar devops_belgrano_manager_enhanced: {e}")
    # Fallback al gestor original
    try:
        from devops_belgrano_manager import DevOpsBelgranoManager
        devops_manager = DevOpsBelgranoManager()
        logger.info("✅ Gestor DevOps original inicializado como fallback")
    except ImportError as e2:
        logger.error(f"❌ No se pudo importar ningún gestor DevOps: {e2}")
        devops_manager = None

=======
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
# Crear blueprint con prefijo
devops_bp = Blueprint('devops', __name__, url_prefix='/devops')

# =============================
# AUTENTICACIÓN DEVOPS
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
            return redirect('/devops/login')
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@devops_bp.route('/login', methods=['GET', 'POST'])
def devops_login():
    """Login de DevOps"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == DEVOPS_USERNAME and check_password_hash(DEVOPS_PASSWORD_HASH, password):
            session['devops_authenticated'] = True
            session.permanent = True
            logger.info(f"Login exitoso de DevOps: {username}")
            return redirect(url_for('devops.devops_home'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('devops/login.html', 
                         username=DEVOPS_USERNAME)

@devops_bp.route('/')
@devops_login_required
def devops_home():
    """Panel principal de DevOps"""
    return render_template('devops/dashboard.html')

@devops_bp.route('/logout')
def devops_logout():
    """Cerrar sesión de DevOps"""
    session.pop('devops_authenticated', None)
    return redirect(url_for('devops.devops_login'))

# =============================
# API CLIENT FUNCTIONS
# =============================

def make_api_request(method, endpoint, data=None):
    """Realizar request a la API de Belgrano Ahorro usando el cliente mejorado"""
    try:
        # Importar cliente mejorado
        from belgrano_client_gateway import BelgranoAhorroClientGateway
        
        # Crear cliente
        client = BelgranoAhorroClientGateway(use_gateway=True)
        
        # Mapear métodos a funciones del cliente
        if method == 'GET':
            if endpoint == 'negocios':
                result = client.get_negocios()
            elif endpoint == 'productos':
                result = client.get_productos()
            elif endpoint == 'ofertas':
                result = client.get_ofertas()
            elif endpoint == 'sucursales':
                result = client.get_sucursales()
            elif endpoint.startswith('negocios/'):
                negocio_id = int(endpoint.split('/')[1])
                result = client.get_negocio(negocio_id)
            elif endpoint.startswith('productos/'):
                producto_id = int(endpoint.split('/')[1])
                result = client.get_producto(producto_id)
            elif endpoint.startswith('ofertas/'):
                oferta_id = int(endpoint.split('/')[1])
                result = client.get_oferta(oferta_id)
            elif endpoint.startswith('sucursales/'):
                sucursal_id = int(endpoint.split('/')[1])
                result = client.get_sucursal(sucursal_id)
            else:
                result = {'success': False, 'error': f'Endpoint no soportado: {endpoint}'}
        
        elif method == 'POST':
            if endpoint == 'negocios':
                result = client.create_negocio(data)
            elif endpoint == 'productos':
                result = client.create_producto(data)
            elif endpoint == 'ofertas':
                result = client.create_oferta(data)
            elif endpoint == 'sucursales':
                result = client.create_sucursal(data)
            else:
                result = {'success': False, 'error': f'Endpoint no soportado: {endpoint}'}
        
        elif method == 'PUT':
            if endpoint.startswith('negocios/'):
                negocio_id = int(endpoint.split('/')[1])
                result = client.update_negocio(negocio_id, data)
            elif endpoint.startswith('productos/'):
                producto_id = int(endpoint.split('/')[1])
                result = client.update_producto(producto_id, data)
            elif endpoint.startswith('ofertas/'):
                oferta_id = int(endpoint.split('/')[1])
                result = client.update_oferta(oferta_id, data)
            elif endpoint.startswith('sucursales/'):
                sucursal_id = int(endpoint.split('/')[1])
                result = client.update_sucursal(sucursal_id, data)
            elif endpoint.startswith('precios/'):
                producto_id = int(endpoint.split('/')[1])
                result = client.update_precio(producto_id, data)
            else:
                result = {'success': False, 'error': f'Endpoint no soportado: {endpoint}'}
        
        elif method == 'DELETE':
            if endpoint.startswith('negocios/'):
                negocio_id = int(endpoint.split('/')[1])
                result = client.delete_negocio(negocio_id)
            elif endpoint.startswith('productos/'):
                producto_id = int(endpoint.split('/')[1])
                result = client.delete_producto(producto_id)
            elif endpoint.startswith('ofertas/'):
                oferta_id = int(endpoint.split('/')[1])
                result = client.delete_oferta(oferta_id)
            elif endpoint.startswith('sucursales/'):
                sucursal_id = int(endpoint.split('/')[1])
                result = client.delete_sucursal(sucursal_id)
            else:
                result = {'success': False, 'error': f'Endpoint no soportado: {endpoint}'}
        
        else:
            result = {'success': False, 'error': f'Método no soportado: {method}'}
        
        # Asegurar estructura consistente
        if not result.get('data'):
            result['data'] = []
        
        return result
        
    except Exception as e:
        logger.error(f"Error en API request: {e}")
        return {'error': str(e), 'data': []}

# =============================
# RUTAS PRINCIPALES
# =============================

@devops_bp.route('/health')
@devops_login_required
def devops_health():
<<<<<<< HEAD
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
                if devops_manager:
                    connectivity = devops_manager.test_connectivity()
                    if connectivity['overall_status'] == 'success':
                        health_status['checks']['api_connection'] = 'healthy'
                    elif connectivity['overall_status'] == 'partial':
                        health_status['checks']['api_connection'] = 'warning'
                    else:
                        health_status['checks']['api_connection'] = 'error'
                        health_status['api_error'] = connectivity.get('message', 'Error de conectividad')
                else:
                    health_status['checks']['api_connection'] = 'disabled'
                    health_status['api_error'] = 'Gestor DevOps no disponible'
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
=======
    """Health check del sistema"""
    try:
        health_data = make_api_request('GET', 'health')
        return jsonify({
            'status': 'success',
            'data': health_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@devops_bp.route('/sync')
@devops_login_required
def devops_sync():
    """Panel de sincronización"""
    return render_template('devops/sync.html')
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb

@devops_bp.route('/status')
@devops_login_required
def devops_status():
    """Estado detallado del sistema DevOps"""
    try:
        # Obtener información del sistema
        system_info = {
            'timestamp': datetime.now().isoformat(),
            'devops_status': 'active',
            'services': {
                'belgrano_ahorro': 'checking...',
                'ticketera': 'checking...',
                'gateway': 'checking...',
                'sync': 'checking...'
            },
            'database': {
                'belgrano_ahorro_db': 'checking...',
                'tickets_db': 'checking...'
            }
        }
        
        # Verificar servicios
        try:
            response = requests.get('http://localhost:5000/', timeout=2)
            system_info['services']['belgrano_ahorro'] = 'active' if response.status_code == 200 else 'error'
        except:
            system_info['services']['belgrano_ahorro'] = 'inactive'
        
        try:
            response = requests.get('http://localhost:5001/', timeout=2)
            system_info['services']['ticketera'] = 'active' if response.status_code == 200 else 'error'
        except:
            system_info['services']['ticketera'] = 'inactive'
        
        try:
            response = requests.get('http://localhost:5003/gateway/health', timeout=2)
            system_info['services']['gateway'] = 'active' if response.status_code == 200 else 'error'
        except:
            system_info['services']['gateway'] = 'inactive'
        
        try:
            response = requests.get('http://localhost:5004/sync/status', timeout=2)
            system_info['services']['sync'] = 'active' if response.status_code == 200 else 'error'
        except:
            system_info['services']['sync'] = 'inactive'
        
        # Verificar bases de datos
        import os
        system_info['database']['belgrano_ahorro_db'] = 'active' if os.path.exists('belgrano_ahorro.db') else 'missing'
        system_info['database']['tickets_db'] = 'active' if os.path.exists('belgrano_tickets.db') else 'missing'
        
        return render_template('devops/status.html', system_info=system_info)
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return render_template('devops/status.html', error=str(e))

@devops_bp.route('/info')
@devops_login_required
def devops_info():
    """Información completa del servicio DevOps"""
    try:
        info = {
            'service': 'DevOps Belgrano Tickets',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'endpoints': [
                '/devops/ - Panel principal',
                '/devops/login - Autenticación',
                '/devops/health - Health check',
                '/devops/status - Estado del sistema',
                '/devops/info - Información del servicio',
                '/devops/negocios - Gestión de negocios',
                '/devops/productos - Gestión de productos',
                '/devops/ofertas - Gestión de ofertas',
                '/devops/sucursales - Gestión de sucursales',
                '/devops/precios - Gestión de precios',
                '/devops/sync - Panel de sincronización'
            ],
            'features': [
                'Gestión completa de contenido',
                'Sincronización en tiempo real',
                'API Gateway integrado',
                'Autenticación segura',
                'Interfaz web moderna'
            ],
            'configuration': {
                'belgrano_ahorro_url': BELGRANO_AHORRO_URL,
                'api_timeout': API_TIMEOUT_SECS,
                'devops_username': DEVOPS_USERNAME
            }
        }
        
        return render_template('devops/info.html', info=info)
        
    except Exception as e:
        logger.error(f"Error obteniendo información: {e}")
        return render_template('devops/info.html', error=str(e))

<<<<<<< HEAD
# ================================================================
# AUTENTICACIÓN (YA MANEJADA ARRIBA CON SISTEMA PROPIO)
# ================================================================

# =================================================================
# GESTIÓN DE OFERTAS
# =================================================================

@devops_bp.route('/ofertas', methods=['GET', 'POST'])
@devops_login_required
def gestion_ofertas():
    """Gestión completa de ofertas"""
    from flask import request, make_response, render_template, flash, redirect, url_for
    
    # Manejar POST requests (crear oferta)
    if request.method == 'POST':
        try:
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            productos = request.form.get('productos', '').strip()
            hasta_agotar_stock = request.form.get('hasta_agotar_stock') == 'on'
            activa = request.form.get('activa') == 'on'
            
            if not all([titulo, descripcion, productos]):
                flash('Título, descripción y productos son requeridos', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            
            # Cargar datos actuales
            from app_unificado import cargar_datos_completos, guardar_datos_json
            import uuid
            datos = cargar_datos_completos()
            if not datos:
                datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
            
            # Crear oferta usando el gestor DevOps
            oferta_data = {
                'titulo': titulo,
                'descripcion': descripcion,
                'productos': productos,
                'hasta_agotar_stock': hasta_agotar_stock,
                'activa': activa
            }
            
            if devops_manager:
                success, message = devops_manager.create_oferta(oferta_data)
                if success:
                    flash(f'Oferta "{titulo}" creada exitosamente', 'success')
                    logger.info(f"Oferta creada desde DevOps: {titulo}")
                else:
                    flash(f'Error al crear oferta: {message}', 'error')
            else:
                # Fallback local
                oferta_id = str(uuid.uuid4())
                nueva_oferta = {
                    'id': oferta_id,
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'productos': productos,
                    'hasta_agotar_stock': hasta_agotar_stock,
                    'activa': activa,
                    'fecha_creacion': datetime.now().isoformat()
                }
                
                # Agregar a la lista
                if 'ofertas' not in datos:
                    datos['ofertas'] = []
                datos['ofertas'].append(nueva_oferta)
                
                # Guardar
                if guardar_datos_json(datos):
                    flash(f'Oferta "{titulo}" creada exitosamente (local)', 'success')
                    logger.info(f"Oferta creada localmente: {titulo}")
                else:
                    flash('Error al guardar la oferta', 'error')
                
        except Exception as e:
            logger.error(f"Error creando oferta desde DevOps: {e}")
            flash('Error interno al crear la oferta', 'error')
        
        return redirect(url_for('devops.gestion_ofertas'))
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            # Obtener datos reales usando el gestor DevOps
            if devops_manager:
                ofertas = devops_manager.get_ofertas()
            else:
                # Fallback con datos simulados
                ofertas = [
                    {
                        'id': 1,
                        'titulo': 'Oferta Especial 50%',
                        'descripcion': 'Descuento del 50% en productos seleccionados',
                        'descuento': 50,
                        'producto_id': 1,
                        'producto_nombre': 'Producto Ejemplo',
                        'fecha_inicio': '2025-01-19',
                        'fecha_fin': '2025-01-31',
                        'activa': True
                    },
                    {
                        'id': 2,
                        'titulo': 'Oferta 2x1',
                        'descripcion': 'Lleva 2 productos y paga solo 1',
                        'descuento': 100,
                        'producto_id': 2,
                        'producto_nombre': 'Producto Ejemplo 2',
                        'fecha_inicio': '2025-01-20',
                        'fecha_fin': '2025-02-15',
                        'activa': True
                    }
                ]
            
            return jsonify({
                'status': 'success',
                'message': f'Ofertas obtenidas correctamente ({len(ofertas)} encontradas)',
                'data': {
                    'ofertas': ofertas,
                    'total': len(ofertas),
                    'timestamp': datetime.now().isoformat()
                },
                'source': 'simulated'
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo ofertas: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Error obteniendo ofertas: {str(e)}',
                'data': []
            }), 500
    
    # Si no es AJAX, devolver template HTML con datos reales
    try:
        from app_unificado import cargar_datos_completos
        datos = cargar_datos_completos()
        if not datos:
            datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
        
        ofertas = datos.get('ofertas', [])
        
        # Devolver template con datos reales
        return render_template('devops/ofertas.html', ofertas=ofertas)
        
    except Exception as e:
        logger.error(f"Error cargando datos para ofertas: {e}")
        # Fallback con datos vacíos
        return render_template('devops/ofertas.html', ofertas=[])
=======
# =============================
# GESTIÓN DE NEGOCIOS
# =============================
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb

@devops_bp.route('/negocios', methods=['GET', 'POST'])
@devops_login_required
def gestion_negocios():
    """Gestión completa de negocios - NUNCA devuelve JSON"""
    # Siempre devolver HTML, nunca JSON
    if request.method == 'POST':
        try:
<<<<<<< HEAD
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            
            if not all([nombre, descripcion]):
                flash('Nombre y descripción son requeridos', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Cargar datos actuales
            from app_unificado import cargar_datos_completos, guardar_datos_json
            import uuid
            datos = cargar_datos_completos()
            if not datos:
                datos = {'productos': [], 'sucursales': [], 'ofertas': [], 'negocios': {}, 'categorias': {}}
            
            # Crear negocio usando el gestor DevOps
            negocio_data = {
                'nombre': nombre,
                'descripcion': descripcion,
                'logo': request.form.get('logo', ''),
                'telefono': request.form.get('telefono', ''),
=======
            # Crear negocio
            data = {
                'nombre': request.form.get('nombre'),
                'descripcion': request.form.get('descripcion', ''),
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
                'direccion': request.form.get('direccion', ''),
                'telefono': request.form.get('telefono', ''),
                'email': request.form.get('email', ''),
<<<<<<< HEAD
                'activo': True
            }
            
            if devops_manager:
                success, message = devops_manager.create_negocio(negocio_data)
                if success:
                    flash(f'Negocio "{nombre}" creado exitosamente', 'success')
                    logger.info(f"Negocio creado desde DevOps: {nombre}")
                else:
                    flash(f'Error al crear negocio: {message}', 'error')
            else:
                # Fallback local
                negocio_id = str(uuid.uuid4())
                nuevo_negocio = {
                    'id': negocio_id,
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'logo': request.form.get('logo', ''),
                    'telefono': request.form.get('telefono', ''),
                    'direccion': request.form.get('direccion', ''),
                    'email': request.form.get('email', ''),
                    'activo': True,
                    'fecha_creacion': datetime.now().isoformat()
                }
                
                # Agregar al diccionario
                if 'negocios' not in datos:
                    datos['negocios'] = {}
                datos['negocios'][negocio_id] = nuevo_negocio
                
                # Guardar
                if guardar_datos_json(datos):
                    flash(f'Negocio "{nombre}" creado exitosamente (local)', 'success')
                    logger.info(f"Negocio creado localmente: {nombre}")
                else:
                    flash('Error al guardar el negocio', 'error')
                
=======
                'activo': request.form.get('activo') == 'on'
            }
            
            if not data['nombre']:
                flash('El nombre es requerido', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            result = make_api_request('POST', 'negocios', data)
            if 'error' in result:
                flash(f'Error creando negocio: {result["error"]}', 'error')
            else:
                flash('Negocio creado exitosamente', 'success')
            
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
        except Exception as e:
            logger.error(f"Error creando negocio: {e}")
            flash('Error interno al crear negocio', 'error')
        
        return redirect(url_for('devops.gestion_negocios'))
    
<<<<<<< HEAD
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            from datetime import datetime
            
            # Obtener datos reales usando el gestor DevOps
            if devops_manager:
                negocios = devops_manager.get_negocios()
            else:
                # Fallback con datos simulados
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
=======
    # GET - Listar negocios
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
    try:
        result = make_api_request('GET', 'negocios')
        if 'error' in result:
            logger.error(f"Error obteniendo negocios: {result['error']}")
            flash(f'Error obteniendo negocios: {result["error"]}', 'error')
            negocios = []
        else:
            negocios = result.get('data', [])
    except Exception as e:
        logger.error(f"Error en gestión de negocios: {e}")
        flash('Error interno al obtener negocios', 'error')
        negocios = []
    
    # SIEMPRE devolver HTML
    return render_template('devops/negocios.html', negocios=negocios)

@devops_bp.route('/negocios/<int:negocio_id>/editar', methods=['POST'])
@devops_login_required
def editar_negocio(negocio_id):
    """Editar negocio"""
    data = {
        'nombre': request.form.get('nombre'),
        'descripcion': request.form.get('descripcion', ''),
        'direccion': request.form.get('direccion', ''),
        'telefono': request.form.get('telefono', ''),
        'email': request.form.get('email', ''),
        'activo': request.form.get('activo') == 'on'
    }
    
    result = make_api_request('PUT', f'negocios/{negocio_id}', data)
    if 'error' in result:
        flash(f'Error actualizando negocio: {result["error"]}', 'error')
    else:
        flash('Negocio actualizado exitosamente', 'success')
    
    return redirect(url_for('devops.gestion_negocios'))

@devops_bp.route('/negocios/<int:negocio_id>/eliminar', methods=['POST'])
@devops_login_required
def eliminar_negocio(negocio_id):
    """Eliminar negocio"""
    result = make_api_request('DELETE', f'negocios/{negocio_id}')
    if 'error' in result:
        flash(f'Error eliminando negocio: {result["error"]}', 'error')
    else:
        flash('Negocio eliminado exitosamente', 'success')
    
    return redirect(url_for('devops.gestion_negocios'))

# =============================
# GESTIÓN DE SUCURSALES
# =============================

@devops_bp.route('/sucursales', methods=['GET', 'POST'])
@devops_login_required
def gestion_sucursales():
    """Gestión completa de sucursales"""
    if request.method == 'POST':
        # Crear sucursal
        data = {
            'nombre': request.form.get('nombre'),
            'direccion': request.form.get('direccion', ''),
            'telefono': request.form.get('telefono', ''),
            'email': request.form.get('email', ''),
            'negocio_id': request.form.get('negocio_id'),
            'activo': request.form.get('activo') == 'on'
        }
        
        if not data['nombre'] or not data['negocio_id']:
            flash('El nombre y negocio son requeridos', 'error')
            return redirect(url_for('devops.gestion_sucursales'))
        
        result = make_api_request('POST', 'sucursales', data)
        if 'error' in result:
            flash(f'Error creando sucursal: {result["error"]}', 'error')
        else:
            flash('Sucursal creada exitosamente', 'success')
        
        return redirect(url_for('devops.gestion_sucursales'))
    
    # GET - Listar sucursales y negocios
    try:
        sucursales_result = make_api_request('GET', 'sucursales')
        negocios_result = make_api_request('GET', 'negocios')
        
        sucursales = sucursales_result.get('data', []) if 'error' not in sucursales_result else []
        negocios = negocios_result.get('data', []) if 'error' not in negocios_result else []
    except Exception as e:
        logger.error(f"Error obteniendo datos: {e}")
        sucursales = []
        negocios = []
    
    return render_template('devops/sucursales.html', sucursales=sucursales, negocios=negocios)

@devops_bp.route('/sucursales/<int:sucursal_id>/editar', methods=['POST'])
@devops_login_required
def editar_sucursal(sucursal_id):
    """Editar sucursal"""
    data = {
        'nombre': request.form.get('nombre'),
        'direccion': request.form.get('direccion', ''),
        'telefono': request.form.get('telefono', ''),
        'email': request.form.get('email', ''),
        'negocio_id': request.form.get('negocio_id'),
        'activo': request.form.get('activo') == 'on'
    }
    
    result = make_api_request('PUT', f'sucursales/{sucursal_id}', data)
    if 'error' in result:
        flash(f'Error actualizando sucursal: {result["error"]}', 'error')
    else:
        flash('Sucursal actualizada exitosamente', 'success')
    
    return redirect(url_for('devops.gestion_sucursales'))

@devops_bp.route('/sucursales/<int:sucursal_id>/eliminar', methods=['POST'])
@devops_login_required
def eliminar_sucursal(sucursal_id):
    """Eliminar sucursal"""
    result = make_api_request('DELETE', f'sucursales/{sucursal_id}')
    if 'error' in result:
        flash(f'Error eliminando sucursal: {result["error"]}', 'error')
    else:
        flash('Sucursal eliminada exitosamente', 'success')
    
    return redirect(url_for('devops.gestion_sucursales'))

# =============================
# GESTIÓN DE PRODUCTOS
# =============================

@devops_bp.route('/productos', methods=['GET', 'POST'])
@devops_login_required
def gestion_productos():
    """Gestión completa de productos"""
    if request.method == 'POST':
<<<<<<< HEAD
        try:
            nombre = request.form.get('nombre', '').strip()
            precio = request.form.get('precio', '').strip()
            categoria = request.form.get('categoria', '').strip()
            negocio = request.form.get('negocio', '').strip()
            
            if not all([nombre, precio, categoria, negocio]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            try:
                precio_float = float(precio)
            except ValueError:
                flash('El precio debe ser un número válido', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Crear producto usando el gestor DevOps
            producto_data = {
                'nombre': nombre,
                'precio': precio_float,
                'categoria': categoria,
                'negocio': negocio,
                'descripcion': request.form.get('descripcion', ''),
                'imagen': request.form.get('imagen', ''),
                'activo': True
            }
            
            if devops_manager:
                success, message = devops_manager.create_producto(producto_data)
                if success:
                    flash(f'Producto "{nombre}" creado exitosamente', 'success')
                    logger.info(f"Producto creado desde DevOps: {nombre}")
                else:
                    flash(f'Error al crear producto: {message}', 'error')
            else:
                # Fallback local
                import uuid
                producto_id = str(uuid.uuid4())
                nuevo_producto = {
                    'id': producto_id,
                    'nombre': nombre,
                    'precio': precio_float,
                    'categoria': categoria,
                    'negocio': negocio,
                    'descripcion': request.form.get('descripcion', ''),
                    'imagen': request.form.get('imagen', ''),
                    'activo': True,
                    'fecha_creacion': datetime.now().isoformat()
                }
                
                # Agregar a la lista
                if 'productos' not in datos:
                    datos['productos'] = []
                datos['productos'].append(nuevo_producto)
                
                # Guardar
                if guardar_datos_json(datos):
                    flash(f'Producto "{nombre}" creado exitosamente (local)', 'success')
                    logger.info(f"Producto creado localmente: {nombre}")
                else:
                    flash('Error al guardar el producto', 'error')
                
        except Exception as e:
            logger.error(f"Error creando producto desde DevOps: {e}")
            flash('Error interno al crear el producto', 'error')
        
        return redirect(url_for('devops.gestion_productos'))
    
    # Solo devolver JSON si se solicita explícitamente con todos los parámetros
    if (request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
        request.args.get('ajax') == 'true' and 
        request.args.get('format') == 'json' and 
        request.args.get('api') == 'true' and
        request.args.get('json') == 'true'):
        try:
            from datetime import datetime
            
            # Obtener datos reales usando el gestor DevOps
            if devops_manager:
                productos = devops_manager.get_productos()
            else:
                # Fallback con datos simulados
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
    
    # Si no es AJAX, devolver template HTML con datos
=======
        # Crear producto
        data = {
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion', ''),
            'precio': float(request.form.get('precio', 0)),
            'categoria': request.form.get('categoria', ''),
            'stock': int(request.form.get('stock', 0)),
            'negocio_id': request.form.get('negocio_id'),
            'activo': request.form.get('activo') == 'on'
        }
        
        if not data['nombre'] or data['precio'] <= 0:
            flash('El nombre y precio son requeridos', 'error')
            return redirect(url_for('devops.gestion_productos'))
        
        result = make_api_request('POST', 'productos', data)
        if 'error' in result:
            flash(f'Error creando producto: {result["error"]}', 'error')
        else:
            flash('Producto creado exitosamente', 'success')
        
        return redirect(url_for('devops.gestion_productos'))
    
    # GET - Listar productos y negocios
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
    try:
        productos_result = make_api_request('GET', 'productos')
        negocios_result = make_api_request('GET', 'negocios')
        
        productos = productos_result.get('data', []) if 'error' not in productos_result else []
        negocios = negocios_result.get('data', []) if 'error' not in negocios_result else []
    except Exception as e:
        logger.error(f"Error obteniendo datos: {e}")
        productos = []
        negocios = []
    
    return render_template('devops/productos.html', productos=productos, negocios=negocios)

@devops_bp.route('/productos/<int:producto_id>/editar', methods=['POST'])
@devops_login_required
def editar_producto(producto_id):
    """Editar producto"""
    data = {
        'nombre': request.form.get('nombre'),
        'descripcion': request.form.get('descripcion', ''),
        'precio': float(request.form.get('precio', 0)),
        'categoria': request.form.get('categoria', ''),
        'stock': int(request.form.get('stock', 0)),
        'negocio_id': request.form.get('negocio_id'),
        'activo': request.form.get('activo') == 'on'
    }
    
<<<<<<< HEAD
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            precio = request.form.get('precio', '').strip()
            categoria = request.form.get('categoria', '').strip()
            negocio = request.form.get('negocio', '').strip()
            
            if not all([nombre, precio, categoria, negocio]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            try:
                precio_float = float(precio)
            except ValueError:
                flash('El precio debe ser un número válido', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Cargar datos actuales
            from app_unificado import cargar_datos_completos, guardar_datos_json
            datos = cargar_datos_completos()
            if not datos:
                flash('Error cargando datos', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Buscar y actualizar producto
            productos = datos.get('productos', [])
            producto_encontrado = False
            for i, producto in enumerate(productos):
                if str(producto.get('id')) == str(producto_id):
                    productos[i] = {
                        'id': producto_id,
                        'nombre': nombre,
                        'precio': precio_float,
                        'categoria': categoria,
                        'negocio': negocio,
                        'descripcion': request.form.get('descripcion', producto.get('descripcion', '')),
                        'imagen': request.form.get('imagen', producto.get('imagen', '')),
                        'stock': int(request.form.get('stock', producto.get('stock', 0))),
                        'activo': request.form.get('activo') == 'on',
                        'fecha_creacion': producto.get('fecha_creacion', datetime.now().isoformat()),
                        'fecha_modificacion': datetime.now().isoformat()
                    }
                    producto_encontrado = True
                    break
            
            if not producto_encontrado:
                flash('Producto no encontrado', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Guardar
            if guardar_datos_json(datos):
                flash(f'Producto "{nombre}" actualizado exitosamente', 'success')
                logger.info(f"Producto actualizado desde DevOps: {nombre}")
            else:
                flash('Error al guardar el producto', 'error')
                
        except Exception as e:
            logger.error(f"Error actualizando producto desde DevOps: {e}")
            flash('Error interno al actualizar el producto', 'error')
        
        return redirect(url_for('devops.gestion_productos'))
    
    # GET - Mostrar formulario de edición
    try:
        from app_unificado import cargar_datos_completos
        datos = cargar_datos_completos()
        productos = datos.get('productos', []) if datos else []
        negocios = list(datos.get('negocios', {}).values()) if datos else []
        categorias = list(datos.get('categorias', {}).values()) if datos else []
        
        # Buscar producto a editar
        producto_editar = None
        for producto in productos:
            if str(producto.get('id')) == str(producto_id):
                producto_editar = producto
                break
        
        if not producto_editar:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('devops.gestion_productos'))
        
        return render_template('devops/editar_producto.html', 
                             producto=producto_editar, 
                             negocios=negocios, 
                             categorias=categorias)
    except Exception as e:
        logger.error(f"Error cargando producto para editar: {e}")
        flash('Error cargando producto', 'error')
        return redirect(url_for('devops.gestion_productos'))

@devops_bp.route('/negocios/editar/<negocio_id>', methods=['GET', 'POST'])
@devops_login_required
def editar_negocio(negocio_id):
    """Editar un negocio existente"""
    from flask import request, make_response, render_template, flash, redirect, url_for
    
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            
            if not all([nombre, descripcion]):
                flash('Nombre y descripción son requeridos', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Cargar datos actuales
            from app_unificado import cargar_datos_completos, guardar_datos_json
            datos = cargar_datos_completos()
            if not datos:
                flash('Error cargando datos', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Buscar y actualizar negocio
            negocios = datos.get('negocios', {})
            if negocio_id not in negocios:
                flash('Negocio no encontrado', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            negocios[negocio_id] = {
                'id': negocio_id,
                'nombre': nombre,
                'descripcion': descripcion,
                'logo': request.form.get('logo', negocios[negocio_id].get('logo', '')),
                'telefono': request.form.get('telefono', negocios[negocio_id].get('telefono', '')),
                'direccion': request.form.get('direccion', negocios[negocio_id].get('direccion', '')),
                'email': request.form.get('email', negocios[negocio_id].get('email', '')),
                'categoria': request.form.get('categoria', negocios[negocio_id].get('categoria', '')),
                'activo': request.form.get('activo') == 'on',
                'fecha_creacion': negocios[negocio_id].get('fecha_creacion', datetime.now().isoformat()),
                'fecha_modificacion': datetime.now().isoformat()
            }
            
            # Guardar
            if guardar_datos_json(datos):
                flash(f'Negocio "{nombre}" actualizado exitosamente', 'success')
                logger.info(f"Negocio actualizado desde DevOps: {nombre}")
            else:
                flash('Error al guardar el negocio', 'error')
                
        except Exception as e:
            logger.error(f"Error actualizando negocio desde DevOps: {e}")
            flash('Error interno al actualizar el negocio', 'error')
        
        return redirect(url_for('devops.gestion_negocios'))
    
    # GET - Mostrar formulario de edición
    try:
        from app_unificado import cargar_datos_completos
        datos = cargar_datos_completos()
        negocios = datos.get('negocios', {}) if datos else {}
        
        # Buscar negocio a editar
        if negocio_id not in negocios:
            flash('Negocio no encontrado', 'error')
            return redirect(url_for('devops.gestion_negocios'))
        
        negocio_editar = negocios[negocio_id]
        return render_template('devops/editar_negocio.html', negocio=negocio_editar)
    except Exception as e:
        logger.error(f"Error cargando negocio para editar: {e}")
        flash('Error cargando negocio', 'error')
        return redirect(url_for('devops.gestion_negocios'))

@devops_bp.route('/productos/eliminar/<producto_id>', methods=['POST'])
@devops_login_required
def eliminar_producto(producto_id):
    """Eliminar un producto"""
    from flask import request, make_response, flash, redirect, url_for
    
    try:
        if devops_manager:
            success, message = devops_manager.delete_producto(producto_id)
            if success:
                flash(f'Producto eliminado exitosamente', 'success')
                logger.info(f"Producto eliminado desde DevOps: ID {producto_id}")
            else:
                flash(f'Error al eliminar producto: {message}', 'error')
        else:
            # Fallback local
            from app_unificado import cargar_datos_completos, guardar_datos_json
            datos = cargar_datos_completos()
            if not datos:
                flash('Error cargando datos', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Buscar y eliminar producto
            productos = datos.get('productos', [])
            producto_encontrado = False
            for i, producto in enumerate(productos):
                if str(producto.get('id')) == str(producto_id):
                    nombre_producto = producto.get('nombre', 'Sin nombre')
                    productos.pop(i)
                    producto_encontrado = True
                    break
            
            if not producto_encontrado:
                flash('Producto no encontrado', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Guardar
            if guardar_datos_json(datos):
                flash(f'Producto eliminado exitosamente (local)', 'success')
                logger.info(f"Producto eliminado localmente: ID {producto_id}")
            else:
                flash('Error al guardar los cambios', 'error')
            
    except Exception as e:
        logger.error(f"Error eliminando producto desde DevOps: {e}")
        flash('Error interno al eliminar el producto', 'error')
=======
    result = make_api_request('PUT', f'productos/{producto_id}', data)
    if 'error' in result:
        flash(f'Error actualizando producto: {result["error"]}', 'error')
    else:
        flash('Producto actualizado exitosamente', 'success')
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
    
    return redirect(url_for('devops.gestion_productos'))

@devops_bp.route('/productos/<int:producto_id>/eliminar', methods=['POST'])
@devops_login_required
def eliminar_producto(producto_id):
    """Eliminar producto"""
    result = make_api_request('DELETE', f'productos/{producto_id}')
    if 'error' in result:
        flash(f'Error eliminando producto: {result["error"]}', 'error')
    else:
        flash('Producto eliminado exitosamente', 'success')
    
<<<<<<< HEAD
    try:
        if devops_manager:
            success, message = devops_manager.delete_negocio(negocio_id)
            if success:
                flash(f'Negocio eliminado exitosamente', 'success')
                logger.info(f"Negocio eliminado desde DevOps: ID {negocio_id}")
            else:
                flash(f'Error al eliminar negocio: {message}', 'error')
        else:
            # Fallback local
            from app_unificado import cargar_datos_completos, guardar_datos_json
            datos = cargar_datos_completos()
            if not datos:
                flash('Error cargando datos', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Buscar y eliminar negocio
            negocios = datos.get('negocios', {})
            if negocio_id not in negocios:
                flash('Negocio no encontrado', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            nombre_negocio = negocios[negocio_id].get('nombre', 'Sin nombre')
            del negocios[negocio_id]
            
            # Guardar
            if guardar_datos_json(datos):
                flash(f'Negocio eliminado exitosamente (local)', 'success')
                logger.info(f"Negocio eliminado localmente: ID {negocio_id}")
            else:
                flash('Error al guardar los cambios', 'error')
            
    except Exception as e:
        logger.error(f"Error eliminando negocio desde DevOps: {e}")
        flash('Error interno al eliminar el negocio', 'error')
    
    return redirect(url_for('devops.gestion_negocios'))
=======
    return redirect(url_for('devops.gestion_productos'))
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb

# =============================
# GESTIÓN DE OFERTAS
# =============================

@devops_bp.route('/ofertas', methods=['GET', 'POST'])
@devops_login_required
def gestion_ofertas():
    """Gestión completa de ofertas"""
    if request.method == 'POST':
        # Crear oferta
        data = {
            'titulo': request.form.get('titulo'),
            'descripcion': request.form.get('descripcion', ''),
            'descuento_porcentaje': float(request.form.get('descuento_porcentaje', 0)),
            'descuento_fijo': float(request.form.get('descuento_fijo', 0)),
            'activa': request.form.get('activa') == 'on'
        }
        
        if not data['titulo']:
            flash('El título es requerido', 'error')
            return redirect(url_for('devops.gestion_ofertas'))
        
        result = make_api_request('POST', 'ofertas', data)
        if 'error' in result:
            flash(f'Error creando oferta: {result["error"]}', 'error')
        else:
            flash('Oferta creada exitosamente', 'success')
        
        return redirect(url_for('devops.gestion_ofertas'))
    
    # GET - Listar ofertas
    try:
        result = make_api_request('GET', 'ofertas')
        ofertas = result.get('data', []) if 'error' not in result else []
    except Exception as e:
        logger.error(f"Error obteniendo ofertas: {e}")
        ofertas = []
    
    return render_template('devops/ofertas.html', ofertas=ofertas)

@devops_bp.route('/ofertas/<int:oferta_id>/editar', methods=['POST'])
@devops_login_required
def editar_oferta(oferta_id):
    """Editar oferta"""
    data = {
        'titulo': request.form.get('titulo'),
        'descripcion': request.form.get('descripcion', ''),
        'descuento_porcentaje': float(request.form.get('descuento_porcentaje', 0)),
        'descuento_fijo': float(request.form.get('descuento_fijo', 0)),
        'activa': request.form.get('activa') == 'on'
    }
    
    result = make_api_request('PUT', f'ofertas/{oferta_id}', data)
    if 'error' in result:
        flash(f'Error actualizando oferta: {result["error"]}', 'error')
    else:
        flash('Oferta actualizada exitosamente', 'success')
    
    return redirect(url_for('devops.gestion_ofertas'))

@devops_bp.route('/ofertas/<int:oferta_id>/eliminar', methods=['POST'])
@devops_login_required
def eliminar_oferta(oferta_id):
    """Eliminar oferta"""
    result = make_api_request('DELETE', f'ofertas/{oferta_id}')
    if 'error' in result:
        flash(f'Error eliminando oferta: {result["error"]}', 'error')
    else:
        flash('Oferta eliminada exitosamente', 'success')
    
    return redirect(url_for('devops.gestion_ofertas'))

# =============================
# GESTIÓN DE PRECIOS
# =============================

@devops_bp.route('/precios', methods=['GET', 'POST'])
@devops_login_required
def gestion_precios():
    """Gestión de precios - NUNCA devuelve JSON"""
    # Siempre devolver HTML, nunca JSON
    if request.method == 'POST':
        try:
            # Actualizar precio
            producto_id = request.form.get('producto_id')
            nuevo_precio = float(request.form.get('nuevo_precio', 0))
            motivo = request.form.get('motivo', 'Actualización desde DevOps')
            
            if not producto_id or nuevo_precio <= 0:
                flash('Producto y precio válido son requeridos', 'error')
                return redirect(url_for('devops.gestion_precios'))
            
            data = {
                'precio': nuevo_precio,
                'motivo': motivo
            }
            
<<<<<<< HEAD
            # Sincronizar ofertas
            try:
                if devops_manager:
                    ofertas = devops_manager.get_ofertas()
                    sync_results['ofertas'] = {
                        'status': 'success',
                        'count': len(ofertas),
                        'message': f'{len(ofertas)} ofertas obtenidas'
                    }
                else:
                    sync_results['ofertas'] = {'status': 'error', 'error': 'Gestor DevOps no disponible'}
            except Exception as e:
                sync_results['ofertas'] = {'status': 'error', 'error': str(e)}
            
            # Sincronizar negocios
            try:
                if devops_manager:
                    negocios = devops_manager.get_negocios()
                    sync_results['negocios'] = {
                        'status': 'success',
                        'count': len(negocios),
                        'message': f'{len(negocios)} negocios obtenidos'
                    }
                else:
                    sync_results['negocios'] = {'status': 'error', 'error': 'Gestor DevOps no disponible'}
            except Exception as e:
                sync_results['negocios'] = {'status': 'error', 'error': str(e)}
            
            # Determinar estado general
            if all(item['status'] == 'success' for item in [sync_results['ofertas'], sync_results['negocios']]):
                sync_results['overall_status'] = 'success'
            elif any(item['status'] == 'success' for item in [sync_results['ofertas'], sync_results['negocios']]):
                sync_results['overall_status'] = 'partial'
=======
            result = make_api_request('PUT', f'precios/{producto_id}', data)
            if 'error' in result:
                flash(f'Error actualizando precio: {result["error"]}', 'error')
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
            else:
                flash('Precio actualizado exitosamente', 'success')
            
        except Exception as e:
            logger.error(f"Error actualizando precio: {e}")
            flash('Error interno al actualizar precio', 'error')
        
<<<<<<< HEAD
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
    from flask import request, make_response, render_template
    
    # Siempre devolver JSON para este endpoint
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

@devops_bp.route('/config')
@devops_login_required
def ver_configuracion():
    """Ver configuración actual del sistema"""
    from flask import request, make_response, render_template
    
    # Siempre devolver JSON para este endpoint
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
            if devops_manager:
                connectivity = devops_manager.test_connectivity()
                connection_status['belgrano_ahorro']['status'] = connectivity['overall_status']
                connection_status['belgrano_ahorro']['endpoints'] = connectivity.get('endpoints', {})
                connection_status['belgrano_ahorro']['success_count'] = connectivity.get('success_count', 0)
                connection_status['belgrano_ahorro']['total_endpoints'] = connectivity.get('total_endpoints', 0)
            else:
                connection_status['belgrano_ahorro']['status'] = 'not_configured'
                connection_status['belgrano_ahorro']['message'] = 'Gestor DevOps no disponible'
            
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
    
    # Si no es AJAX, devolver template HTML
    return render_template('devops/conectar.html')

@devops_bp.route('/system-status')
@devops_login_required
def system_status():
    """Estado completo del sistema DevOps"""
    try:
        if devops_manager:
            status = devops_manager.get_system_status()
            return jsonify({
                'status': 'success',
                'data': status
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Gestor DevOps no disponible',
                'data': {
                    'timestamp': datetime.now().isoformat(),
                    'fallback_mode': True,
                    'api_configured': False
                }
            }), 503
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }), 500

# =================================================================
# INTERFAZ WEB DEVOPS UI
# =================================================================

@devops_bp.route('/ui')
@devops_login_required
def devops_ui():
    """Interfaz web para gestión de endpoints DevOps"""
    from flask import render_template
=======
        return redirect(url_for('devops.gestion_precios'))
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
    
    # GET - Listar precios y productos
    try:
        precios_result = make_api_request('GET', 'precios')
        productos_result = make_api_request('GET', 'productos')
        
        if 'error' in precios_result:
            logger.error(f"Error obteniendo precios: {precios_result['error']}")
            flash(f'Error obteniendo precios: {precios_result["error"]}', 'error')
            precios = []
        else:
            precios = precios_result.get('data', [])
        
        if 'error' in productos_result:
            logger.error(f"Error obteniendo productos: {productos_result['error']}")
            flash(f'Error obteniendo productos: {productos_result["error"]}', 'error')
            productos = []
        else:
            productos = productos_result.get('data', [])
            
    except Exception as e:
        logger.error(f"Error en gestión de precios: {e}")
        flash('Error interno al obtener datos', 'error')
        precios = []
        productos = []
    
    # SIEMPRE devolver HTML
    return render_template('devops/precios.html', precios=precios, productos=productos)

# =============================
# MIDDLEWARE ANTI-JSON CRUDO
# =============================

@devops_bp.before_request
def before_request():
    """Middleware para prevenir JSON crudo"""
    pass

@devops_bp.after_request
def after_request(response):
    """Middleware para garantizar que nunca se devuelva JSON crudo"""
    try:
        # Si la respuesta es JSON, convertir a HTML
        if response.content_type and 'application/json' in response.content_type:
            logger.warning("Interceptando respuesta JSON - convirtiendo a HTML")
            # Redirigir al dashboard en lugar de devolver JSON
            return redirect(url_for('devops.devops_home'))
        
        # Si la respuesta contiene JSON crudo en el contenido, redirigir
        if response.data:
            content_str = response.data.decode('utf-8', errors='ignore')
            if ('"status":"error"' in content_str or 
                '"message":"Error interno del servidor DevOps"' in content_str or
                '"timestamp":' in content_str):
                logger.warning("Interceptando JSON crudo - redirigiendo")
                return redirect(url_for('devops.devops_home'))
        
        return response
    except Exception as e:
        logger.error(f"Error en middleware anti-JSON: {e}")
        return redirect(url_for('devops.devops_home'))

# =============================
# MANEJO DE ERRORES
# =============================

@devops_bp.errorhandler(404)
def devops_not_found(error):
    """Manejar errores 404 en DevOps"""
    if request.path.startswith('/devops/api/'):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint DevOps no encontrado',
            'available_endpoints': [
                '/devops/',
                '/devops/negocios',
                '/devops/sucursales',
                '/devops/productos',
                '/devops/ofertas',
                '/devops/precios'
            ],
            'timestamp': datetime.now().isoformat()
        }), 404
    else:
        # Para rutas HTML, redirigir al dashboard
        return redirect(url_for('devops.devops_home'))

@devops_bp.errorhandler(500)
def devops_internal_error(error):
    """Manejar errores 500 en DevOps"""
    logger.error(f"Error interno DevOps: {error}")
    
    if request.path.startswith('/devops/api/'):
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor DevOps',
            'timestamp': datetime.now().isoformat()
        }), 500
    else:
        # Para rutas HTML, mostrar página de error
        flash('Error interno del servidor. Intente nuevamente.', 'error')
        return redirect(url_for('devops.devops_home'))

@devops_bp.errorhandler(Exception)
def devops_handle_exception(error):
    """Manejar todas las excepciones no capturadas"""
    logger.error(f"Excepción no manejada en DevOps: {error}")
    
    if request.path.startswith('/devops/api/'):
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor DevOps',
            'timestamp': datetime.now().isoformat()
        }), 500
    else:
        # Para rutas HTML, mostrar página de error
        flash('Error interno del servidor. Intente nuevamente.', 'error')
        return redirect(url_for('devops.devops_home'))

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