# Rutas DevOps (migradas a paquete devops)
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
import os
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use package-local templates/static so frontend queda nucleado en devops/
devops_bp = Blueprint(
    'devops', __name__, url_prefix='/devops',
    template_folder='templates', static_folder='static', static_url_path='/devops/static'
)

try:
    from .manager_unified import devops_manager_unified as devops_manager
    logger.info("✅ Gestor DevOps unificado inicializado (paquete devops)")
except Exception as e:
    logger.error(f"❌ No se pudo importar manager_unified: {e}")
    devops_manager = None

# ================================
# Helpers de conectividad externa
# ================================
def _ahorro_base_url() -> str:
    return os.getenv('BELGRANO_AHORRO_URL', '').rstrip('/')

def _ahorro_headers() -> dict:
    api_key = os.getenv('BELGRANO_AHORRO_API_KEY', '')
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        headers["X-API-Key"] = api_key
    return headers

def _ticketera_base_url() -> str:
    # Prioridad: DEVOPS_API_URL (si ticketera expone REST), luego TICKETS_API_URL/TICKETERA_URL
    return (
        os.getenv('TICKETS_API_URL')
        or os.getenv('TICKETERA_URL')
        or os.getenv('DEVOPS_API_URL')
        or ''
    ).rstrip('/')

def _ticketera_headers() -> dict:
    api_key = (
        os.getenv('TICKETS_API_KEY')
        or os.getenv('TICKETERA_API_KEY')
        or os.getenv('DEVOPS_API_KEY')
        or ''
    )
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers

def devops_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('devops_authenticated'):
            return redirect(url_for('devops.devops_login'))
        return f(*args, **kwargs)
    return decorated_function

@devops_bp.route('/login', methods=['GET', 'POST'])
def devops_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'devops' and password == 'devops_password':
            session['devops_authenticated'] = True
            flash('Login exitoso', 'success')
            return redirect(url_for('devops.dashboard'))
        else:
            flash('Credenciales inválidas', 'error')
    return render_template('devops/login.html')

@devops_bp.route('/logout')
def devops_logout():
    session.pop('devops_authenticated', None)
    flash('Sesión cerrada', 'info')
    return redirect(url_for('devops.devops_login'))

@devops_bp.route('/')
@devops_bp.route('/dashboard')
@devops_login_required
def dashboard():
    try:
        if not devops_manager:
            flash('Error: API de Belgrano Ahorro no configurada. Configure BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY.', 'error')
            return render_template('devops/dashboard.html', negocios=[], productos=[], ofertas=[], sucursales=[])
        negocios = devops_manager.get_negocios()
        productos = devops_manager.get_productos()
        ofertas = devops_manager.get_ofertas()
        sucursales = devops_manager.get_sucursales()
        return render_template('devops/dashboard.html', negocios=negocios, productos=productos, ofertas=ofertas, sucursales=sucursales)
    except Exception as e:
        logger.error(f"Error cargando dashboard: {e}")
        flash('Error interno al cargar dashboard.', 'error')
        return render_template('devops/dashboard.html', negocios=[], productos=[], ofertas=[], sucursales=[])

@devops_bp.route('/negocios', methods=['GET', 'POST'])
@devops_login_required
def gestion_negocios():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            if not all([nombre, descripcion]):
                flash('Nombre y descripción son requeridos', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            if not devops_manager:
                flash('Error: API no configurada. Verifique BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            negocio_data = {
                'nombre': nombre,
                'descripcion': descripcion,
                'logo': request.form.get('logo', ''),
                'telefono': request.form.get('telefono', ''),
                'direccion': request.form.get('direccion', ''),
                'email': request.form.get('email', ''),
                'activo': True
            }
            success, message = devops_manager.create_item('negocios', negocio_data)
            if success:
                flash(f'Negocio "{nombre}" creado exitosamente', 'success')
                logger.info(f"Negocio creado y sincronizado: {nombre}")
            else:
                flash(f'Error al crear negocio: {message}', 'error')
                logger.error(f"Error al crear negocio en API: {message}")
        except Exception as e:
            logger.error(f"Error creando negocio: {e}")
            flash(f'Error interno al crear el negocio: {str(e)}', 'error')
        return redirect(url_for('devops.gestion_negocios'))
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return render_template('devops/negocios.html', negocios=[], config_ok=False)
        negocios = devops_manager.get_negocios()
        return render_template('devops/negocios.html', negocios=negocios, config_ok=True)
    except Exception as e:
        logger.error(f"Error cargando negocios: {e}")
        flash('Error interno al cargar negocios.', 'error')
        return render_template('devops/negocios.html', negocios=[], config_ok=False)

@devops_bp.route('/productos', methods=['GET', 'POST'])
@devops_login_required
def gestion_productos():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            precio = request.form.get('precio', '').strip()
            negocio_id = request.form.get('negocio_id', '').strip()
            if not all([nombre, descripcion, precio, negocio_id]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('devops.gestion_productos'))
            try:
                precio_float = float(precio)
            except ValueError:
                flash('El precio debe ser un número válido', 'error')
                return redirect(url_for('devops.gestion_productos'))
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_productos'))
            producto_data = {
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio_float,
                'negocio_id': int(negocio_id),
                'categoria_id': request.form.get('categoria_id', 1),
                'activo': True
            }
            success, message = devops_manager.create_item('productos', producto_data)
            if success:
                flash(f'Producto "{nombre}" creado exitosamente', 'success')
                logger.info(f"Producto creado y sincronizado: {nombre}")
            else:
                flash(f'Error al crear producto: {message}', 'error')
                logger.error(f"Error al crear producto en API: {message}")
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            flash('Error interno al crear el producto', 'error')
        return redirect(url_for('devops.gestion_productos'))
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return render_template('devops/productos.html', productos=[], negocios=[])
        productos = devops_manager.get_productos()
        negocios = devops_manager.get_negocios()
        return render_template('devops/productos.html', productos=productos, negocios=negocios)
    except Exception as e:
        logger.error(f"Error cargando productos: {e}")
        flash('Error interno al cargar productos.', 'error')
        return render_template('devops/productos.html', productos=[], negocios=[])

@devops_bp.route('/ofertas', methods=['GET', 'POST'])
@devops_login_required
def gestion_ofertas():
    if request.method == 'POST':
        try:
            titulo = request.form.get('titulo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            descuento = request.form.get('descuento', '').strip()
            producto_id = request.form.get('producto_id', '').strip()
            if not all([titulo, descripcion, descuento, producto_id]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            try:
                descuento_float = float(descuento)
            except ValueError:
                flash('El descuento debe ser un número válido', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            oferta_data = {
                'titulo': titulo,
                'descripcion': descripcion,
                'descuento': descuento_float,
                'producto_id': int(producto_id),
                'fecha_inicio': request.form.get('fecha_inicio', datetime.now().strftime('%Y-%m-%d')),
                'fecha_fin': request.form.get('fecha_fin', ''),
                'activa': True
            }
            success, message = devops_manager.create_item('ofertas', oferta_data)
            if success:
                flash(f'Oferta "{titulo}" creada exitosamente', 'success')
                logger.info(f"Oferta creada y sincronizada: {titulo}")
            else:
                flash(f'Error al crear oferta: {message}', 'error')
                logger.error(f"Error al crear oferta en API: {message}")
        except Exception as e:
            logger.error(f"Error creando oferta: {e}")
            flash('Error interno al crear la oferta', 'error')
        return redirect(url_for('devops.gestion_ofertas'))
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return render_template('devops/ofertas.html', ofertas=[])
        ofertas = devops_manager.get_ofertas()
        return render_template('devops/ofertas.html', ofertas=ofertas)
    except Exception as e:
        logger.error(f"Error cargando ofertas: {e}")
        flash('Error interno al cargar ofertas.', 'error')
        return render_template('devops/ofertas.html', ofertas=[])

@devops_bp.route('/precios', methods=['GET', 'POST'])
@devops_login_required
def gestion_precios():
    if request.method == 'POST':
        try:
            producto_id = request.form.get('producto_id', '').strip()
            nuevo_precio = request.form.get('nuevo_precio', '').strip()
            motivo = request.form.get('motivo', '').strip()
            if not all([producto_id, nuevo_precio]):
                flash('Producto y nuevo precio son requeridos', 'error')
                return redirect(url_for('devops.gestion_precios'))
            try:
                precio_float = float(nuevo_precio)
            except ValueError:
                flash('El precio debe ser un número válido', 'error')
                return redirect(url_for('devops.gestion_precios'))
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_precios'))
            precio_data = {
                'producto_id': int(producto_id),
                'nuevo_precio': precio_float,
                'motivo': motivo or 'Actualización desde DevOps'
            }
            success, message = devops_manager.update_item('precios', producto_id, precio_data)
            if success:
                flash('Precio actualizado exitosamente', 'success')
                logger.info(f"Precio actualizado: Producto {producto_id}")
            else:
                flash(f'Error al actualizar precio: {message}', 'error')
                logger.error(f"Error al actualizar precio en API: {message}")
        except Exception as e:
            logger.error(f"Error actualizando precio: {e}")
            flash('Error interno al actualizar el precio', 'error')
        return redirect(url_for('devops.gestion_precios'))
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return render_template('devops/precios.html', precios=[], productos=[])
        precios = devops_manager.get_items('precios')
        productos = devops_manager.get_productos()
        return render_template('devops/precios.html', precios=precios, productos=productos)
    except Exception as e:
        logger.error(f"Error cargando precios: {e}")
        flash('Error interno al cargar precios.', 'error')
        return render_template('devops/precios.html', precios=[], productos=[])

@devops_bp.route('/conectar-belgrano')
@devops_login_required
def conectar_belgrano():
    try:
        if not devops_manager:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'status': 'error', 'message': 'Gestor DevOps no disponible', 'data': {}}), 503
            else:
                flash('Gestor DevOps no disponible', 'error')
                return render_template('devops/status.html', status='error', message='Gestor DevOps no disponible', connectivity={})
        connectivity = devops_manager.test_connectivity()
        if connectivity['overall_status'] == 'success':
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'status': 'success', 'message': 'Conexión exitosa con Belgrano Ahorro', 'data': connectivity})
            else:
                flash('Conexión exitosa con Belgrano Ahorro', 'success')
                return render_template('devops/status.html', status='success', message='Conexión exitosa con Belgrano Ahorro', connectivity=connectivity)
        elif connectivity['overall_status'] == 'partial':
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'status': 'warning', 'message': 'Conexión parcial con Belgrano Ahorro', 'data': connectivity})
            else:
                flash('Conexión parcial con Belgrano Ahorro', 'warning')
                return render_template('devops/status.html', status='warning', message='Conexión parcial con Belgrano Ahorro', connectivity=connectivity)
        else:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'status': 'error', 'message': 'No se pudo conectar con Belgrano Ahorro', 'data': connectivity}), 503
            else:
                flash('No se pudo conectar con Belgrano Ahorro', 'error')
                return render_template('devops/status.html', status='error', message='No se pudo conectar con Belgrano Ahorro', connectivity=connectivity)
    except Exception as e:
        logger.error(f"Error verificando conexión con Belgrano Ahorro: {e}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}', 'data': {}}), 500
        else:
            flash(f'Error interno: {str(e)}', 'error')
            return render_template('devops/status.html', status='error', message=f'Error interno: {str(e)}', connectivity={})

@devops_bp.route('/info')
@devops_login_required
def devops_info():
    try:
        if not devops_manager:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'status': 'error', 'message': 'Gestor DevOps no disponible', 'data': {'timestamp': datetime.now().isoformat(), 'fallback_mode': True, 'api_configured': False}}), 503
            else:
                flash('Gestor DevOps no disponible', 'error')
                return render_template('devops/info.html', status='error', message='Gestor DevOps no disponible', system_status={'timestamp': datetime.now().isoformat(), 'fallback_mode': True, 'api_configured': False})
        system_status = devops_manager.get_system_status()
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'status': 'success', 'message': 'Información del sistema DevOps', 'data': system_status})
        else:
            flash('Información del sistema cargada correctamente', 'success')
            return render_template('devops/info.html', status='success', message='Información del sistema DevOps', system_status=system_status)
    except Exception as e:
        logger.error(f"Error obteniendo información del sistema: {e}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}', 'data': {}}), 500
        else:
            flash(f'Error interno: {str(e)}', 'error')
            return render_template('devops/info.html', status='error', message=f'Error interno: {str(e)}', system_status={})

# =================================================================
# Endpoints de conectividad y proxies a APIs externas
# =================================================================

@devops_bp.route('/api/integrations/health')
@devops_login_required
def integrations_health():
    """Verifica salud de Belgrano Ahorro y Ticketera."""
    results = {
        'ahorro': {'ok': False, 'status': None, 'error': None},
        'ticketera': {'ok': False, 'status': None, 'error': None},
    }
    # Belgrano Ahorro
    try:
        base = _ahorro_base_url()
        if base:
            resp = requests.get(f"{base}/api/health", headers=_ahorro_headers(), timeout=10)
            results['ahorro']['ok'] = 200 <= resp.status_code < 300
            results['ahorro']['status'] = resp.json() if resp.headers.get('content-type','').startswith('application/json') else resp.text
        else:
            results['ahorro']['error'] = 'BELGRANO_AHORRO_URL no configurada'
    except Exception as e:
        results['ahorro']['error'] = str(e)

    # Ticketera
    try:
        base_t = _ticketera_base_url()
        if base_t:
            # Intentar health estándar
            for path in ('/api/health', '/health', '/status'):
                try:
                    resp = requests.get(f"{base_t}{path}", headers=_ticketera_headers(), timeout=10)
                    if 200 <= resp.status_code < 300:
                        results['ticketera']['ok'] = True
                        results['ticketera']['status'] = resp.json() if resp.headers.get('content-type','').startswith('application/json') else resp.text
                        break
                except Exception:
                    continue
            if not results['ticketera']['ok'] and not results['ticketera']['status']:
                results['ticketera']['error'] = 'No respondió health en rutas conocidas'
        else:
            results['ticketera']['error'] = 'TICKETS_API_URL/TICKETERA_URL/DEVOPS_API_URL no configurada'
    except Exception as e:
        results['ticketera']['error'] = str(e)

    overall = 'success' if results['ahorro']['ok'] and results['ticketera']['ok'] else (
        'partial' if results['ahorro']['ok'] or results['ticketera']['ok'] else 'error'
    )
    return jsonify({'status': overall, 'results': results})


def _proxy_request(base_url: str, subpath: str, headers: dict):
    method = request.method.upper()
    url = f"{base_url}/{subpath.lstrip('/')}"
    kwargs = {
        'headers': headers,
        'timeout': 30,
    }
    if method in ('POST', 'PUT', 'PATCH'):
        kwargs['json'] = request.get_json(silent=True) or {}
    if method == 'GET':
        kwargs['params'] = request.args
    resp = requests.request(method, url, **kwargs)
    content_type = resp.headers.get('content-type','')
    body = None
    try:
        body = resp.json() if content_type.startswith('application/json') else resp.text
    except Exception:
        body = resp.text
    return jsonify(body) if isinstance(body, (dict, list)) else (body, resp.status_code, {'Content-Type': content_type})


@devops_bp.route('/api/ahorro/<path:subpath>', methods=['GET','POST','PUT','PATCH','DELETE'])
@devops_login_required
def proxy_belgrano_ahorro(subpath: str):
    base = _ahorro_base_url()
    if not base:
        return jsonify({'status':'error','message':'BELGRANO_AHORRO_URL no configurada'}), 500
    return _proxy_request(base, subpath, _ahorro_headers())


@devops_bp.route('/api/ticketera/<path:subpath>', methods=['GET','POST','PUT','PATCH','DELETE'])
@devops_login_required
def proxy_ticketera(subpath: str):
    base = _ticketera_base_url()
    if not base:
        return jsonify({'status':'error','message':'TICKETS_API_URL/TICKETERA_URL/DEVOPS_API_URL no configurada'}), 500
    return _proxy_request(base, subpath, _ticketera_headers())

# =================================================================
# API REST JSON propia de DevOps (CRUD básico)
# =================================================================

def _json_response(ok: bool, data=None, message: str = 'ok', status_code: int = 200):
    body = {'status': 'success' if ok else 'error', 'message': message}
    if data is not None:
        body['data'] = data
    return jsonify(body), status_code


@devops_bp.route('/api/negocios', methods=['GET', 'POST'])
@devops_login_required
def api_negocios():
    if request.method == 'GET':
        try:
            items = devops_manager.get_negocios() if devops_manager else []
            return _json_response(True, items)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    # POST
    payload = request.get_json(silent=True) or {}
    try:
        ok, msg = devops_manager.create_item('negocios', payload) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 201 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/negocios/<int:item_id>', methods=['PUT', 'DELETE'])
@devops_login_required
def api_negocio_detail(item_id: int):
    if request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        try:
            ok, msg = devops_manager.update_item('negocios', item_id, payload) if devops_manager else (False, 'manager no disponible')
            return _json_response(ok, None, msg, 200 if ok else 400)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    # DELETE
    try:
        ok, msg = devops_manager.delete_item('negocios', item_id) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 200 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/productos', methods=['GET', 'POST'])
@devops_login_required
def api_productos():
    if request.method == 'GET':
        try:
            items = devops_manager.get_productos() if devops_manager else []
            return _json_response(True, items)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    payload = request.get_json(silent=True) or {}
    try:
        ok, msg = devops_manager.create_item('productos', payload) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 201 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/productos/<int:item_id>', methods=['PUT', 'DELETE'])
@devops_login_required
def api_producto_detail(item_id: int):
    if request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        try:
            ok, msg = devops_manager.update_item('productos', item_id, payload) if devops_manager else (False, 'manager no disponible')
            return _json_response(ok, None, msg, 200 if ok else 400)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    try:
        ok, msg = devops_manager.delete_item('productos', item_id) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 200 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/ofertas', methods=['GET', 'POST'])
@devops_login_required
def api_ofertas():
    if request.method == 'GET':
        try:
            items = devops_manager.get_ofertas() if devops_manager else []
            return _json_response(True, items)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    payload = request.get_json(silent=True) or {}
    try:
        ok, msg = devops_manager.create_item('ofertas', payload) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 201 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/ofertas/<int:item_id>', methods=['PUT', 'DELETE'])
@devops_login_required
def api_oferta_detail(item_id: int):
    if request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        try:
            ok, msg = devops_manager.update_item('ofertas', item_id, payload) if devops_manager else (False, 'manager no disponible')
            return _json_response(ok, None, msg, 200 if ok else 400)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    try:
        ok, msg = devops_manager.delete_item('ofertas', item_id) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 200 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/sucursales', methods=['GET', 'POST'])
@devops_login_required
def api_sucursales():
    if request.method == 'GET':
        try:
            items = devops_manager.get_items('sucursales') if devops_manager else []
            return _json_response(True, items)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    payload = request.get_json(silent=True) or {}
    try:
        ok, msg = devops_manager.create_item('sucursales', payload) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 201 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/sucursales/<string:item_id>', methods=['PUT', 'DELETE'])
@devops_login_required
def api_sucursal_detail(item_id: str):
    if request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        try:
            ok, msg = devops_manager.update_item('sucursales', item_id, payload) if devops_manager else (False, 'manager no disponible')
            return _json_response(ok, None, msg, 200 if ok else 400)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    try:
        ok, msg = devops_manager.delete_item('sucursales', item_id) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 200 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)


@devops_bp.route('/api/precios', methods=['GET', 'POST', 'PUT'])
@devops_login_required
def api_precios():
    if request.method == 'GET':
        try:
            items = devops_manager.get_items('precios') if devops_manager else []
            return _json_response(True, items)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    payload = request.get_json(silent=True) or {}
    # Para precios, usamos update_item con 'precios' y producto_id en payload
    producto_id = payload.get('producto_id')
    if not producto_id:
        return _json_response(False, None, 'producto_id requerido', 400)
    try:
        ok, msg = devops_manager.update_item('precios', producto_id, payload) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 200 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/sucursales', methods=['GET', 'POST'])
@devops_login_required
def gestion_sucursales():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            direccion = request.form.get('direccion', '').strip()
            telefono = request.form.get('telefono', '').strip()
            negocio_id = request.form.get('negocio_id', '').strip()
            if not all([nombre, direccion, negocio_id]):
                flash('Nombre, dirección y negocio son requeridos', 'error')
                return redirect(url_for('devops.gestion_sucursales'))
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_sucursales'))
            sucursal_data = {
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'negocio_id': negocio_id,
                'activo': True
            }
            success, message = devops_manager.create_sucursal(sucursal_data)
            if success:
                flash('Sucursal creada exitosamente', 'success')
                logger.info(f"Sucursal creada: {nombre}")
            else:
                flash(f'Error al crear sucursal: {message}', 'error')
                logger.error(f"Error creando sucursal en API: {message}")
        except Exception as e:
            logger.error(f"Error creando sucursal: {e}")
            flash('Error interno al crear la sucursal', 'error')
        return redirect(url_for('devops.gestion_sucursales'))
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return render_template('devops/sucursales.html', sucursales=[], negocios=[])
        sucursales = devops_manager.get_sucursales()
        negocios = devops_manager.get_negocios()
        return render_template('devops/sucursales.html', sucursales=sucursales, negocios=negocios)
    except Exception as e:
        logger.error(f"Error cargando sucursales: {e}")
        flash('Error interno al cargar sucursales.', 'error')
        return render_template('devops/sucursales.html', sucursales=[], negocios=[])
