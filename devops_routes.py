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

# =============================
# GESTIÓN DE NEGOCIOS
# =============================

@devops_bp.route('/negocios', methods=['GET', 'POST'])
@devops_login_required
def gestion_negocios():
    """Gestión completa de negocios - NUNCA devuelve JSON"""
    # Siempre devolver HTML, nunca JSON
    if request.method == 'POST':
        try:
            # Crear negocio
            data = {
                'nombre': request.form.get('nombre'),
                'descripcion': request.form.get('descripcion', ''),
                'direccion': request.form.get('direccion', ''),
                'telefono': request.form.get('telefono', ''),
                'email': request.form.get('email', ''),
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
            
        except Exception as e:
            logger.error(f"Error creando negocio: {e}")
            flash('Error interno al crear negocio', 'error')
        
        return redirect(url_for('devops.gestion_negocios'))
    
    # GET - Listar negocios
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
    
    result = make_api_request('PUT', f'productos/{producto_id}', data)
    if 'error' in result:
        flash(f'Error actualizando producto: {result["error"]}', 'error')
    else:
        flash('Producto actualizado exitosamente', 'success')
    
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
    
    return redirect(url_for('devops.gestion_productos'))

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
            
            result = make_api_request('PUT', f'precios/{producto_id}', data)
            if 'error' in result:
                flash(f'Error actualizando precio: {result["error"]}', 'error')
            else:
                flash('Precio actualizado exitosamente', 'success')
            
        except Exception as e:
            logger.error(f"Error actualizando precio: {e}")
            flash('Error interno al actualizar precio', 'error')
        
        return redirect(url_for('devops.gestion_precios'))
    
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