# Rutas DevOps (migradas a paquete devops)
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
import os
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use package-local templates/static so frontend queda nucleado en devops/
# Usar rutas absolutas para templates y static
_current_dir = os.path.dirname(os.path.abspath(__file__))
_template_dir = os.path.join(_current_dir, 'templates')
_static_dir = os.path.join(_current_dir, 'static') if os.path.exists(os.path.join(_current_dir, 'static')) else None

devops_bp = Blueprint(
    'devops', __name__, url_prefix='/devops',
    template_folder=_template_dir if os.path.exists(_template_dir) else 'templates',
    static_folder=_static_dir if _static_dir else None,
    static_url_path='/devops/static' if _static_dir else None
)

# Importar managers - se inicializan cuando se importa el módulo
# Las variables de entorno DEBEN estar cargadas antes de importar este módulo
# (app.py carga las variables antes de importar routes)
try:
    # Intentar import relativo (cuando se usa como paquete)
    from .manager_unified import (
        devops_manager_unified,
        devops_ticketera_manager,
        devops_sync_manager
    )
    # Acceder a los managers para forzar inicialización lazy
    # Esto asegura que las variables de entorno estén cargadas
    devops_manager = devops_manager_unified
    logger.info("✅ Gestor DevOps unificado importado (paquete devops)")
except ImportError:
    try:
        # Intentar import absoluto (si estamos en el directorio devops)
        from manager_unified import (
            devops_manager_unified,
            devops_ticketera_manager,
            devops_sync_manager
        )
        devops_manager = devops_manager_unified
        logger.info("✅ Gestor DevOps unificado importado (directorio)")
    except ImportError as e:
        logger.error(f"❌ No se pudo importar manager_unified: {e}")
        devops_manager = None
        devops_ticketera_manager = None
        devops_sync_manager = None
except Exception as e:
    logger.error(f"❌ Error inesperado importando manager_unified: {e}")
    devops_manager = None
    devops_ticketera_manager = None
    devops_sync_manager = None

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
        # Usar variables de entorno para credenciales (más seguro)
        expected_username = os.getenv('DEVOPS_USERNAME', 'devops')
        expected_password = os.getenv('DEVOPS_PASSWORD', 'devops_password')
        
        if username == expected_username and password == expected_password:
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
        # Verificar si el manager existe y está configurado
        # Acceder al manager para forzar inicialización lazy
        manager = devops_manager if devops_manager else None
        if not manager or not manager.is_configured():
            error_msg = (
                'Error: API de Belgrano Ahorro no configurada. '
                'Configure las variables de entorno BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY. '
                'Verifique la documentación en devops/env/env.example'
            )
            flash(error_msg, 'error')
            logger.warning("⚠️ Dashboard accedido sin configuración de API")
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

@devops_bp.route('/negocios/<int:negocio_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_negocio(negocio_id):
    """Editar un negocio - GET muestra formulario, POST procesa actualización"""
    if request.method == 'POST':
        try:
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Obtener datos del formulario
            negocio_data = {
                'nombre': request.form.get('nombre', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'direccion': request.form.get('direccion', '').strip(),
                'telefono': request.form.get('telefono', '').strip(),
                'email': request.form.get('email', '').strip(),
                'activo': request.form.get('activo') == 'on'
            }
            
            # Validar campos requeridos
            if not negocio_data['nombre'] or not negocio_data['descripcion']:
                flash('Nombre y descripción son requeridos', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Actualizar negocio usando el manager
            success, message = devops_manager.update_item('negocios', negocio_id, negocio_data)
            if success:
                flash(f'Negocio "{negocio_data["nombre"]}" actualizado exitosamente', 'success')
                logger.info(f"Negocio {negocio_id} actualizado: {negocio_data['nombre']}")
            else:
                flash(f'Error al actualizar negocio: {message}', 'error')
                logger.error(f"Error actualizando negocio {negocio_id}: {message}")
        except Exception as e:
            logger.error(f"Error actualizando negocio: {e}")
            flash(f'Error interno al actualizar el negocio: {str(e)}', 'error')
        return redirect(url_for('devops.gestion_negocios'))
    
    # GET - Redirigir a gestión (el template maneja el modal)
    flash('Usa el botón de editar en la tabla para modificar negocios', 'info')
    return redirect(url_for('devops.gestion_negocios'))

@devops_bp.route('/negocios/eliminar/<int:negocio_id>', methods=['POST', 'GET'])
@devops_login_required
def eliminar_negocio(negocio_id):
    """Eliminar un negocio - acepta POST (desde formulario) y GET (con confirmación)"""
    if request.method == 'GET':
        # Si accede por GET, redirigir a la página de negocios con mensaje
        flash('La eliminación debe realizarse desde el botón de eliminar en la tabla', 'warning')
        return redirect(url_for('devops.gestion_negocios'))
    
    # Método POST
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return redirect(url_for('devops.gestion_negocios'))
        success, message = devops_manager.delete_item('negocios', negocio_id)
        if success:
            flash(f'Negocio eliminado exitosamente', 'success')
            logger.info(f"Negocio {negocio_id} eliminado")
        else:
            flash(f'Error al eliminar negocio: {message}', 'error')
            logger.error(f"Error eliminando negocio: {message}")
    except Exception as e:
        logger.error(f"Error eliminando negocio: {e}")
        flash('Error interno al eliminar el negocio', 'error')
    return redirect(url_for('devops.gestion_negocios'))

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
            # Obtener categoría del formulario o usar valor por defecto
            categoria = request.form.get('categoria', '').strip()
            if not categoria:
                categoria = request.form.get('categoria_id', '1')  # Fallback a categoria_id si no hay categoria
            
            producto_data = {
                'nombre': nombre,
                'descripcion': descripcion,  # Se mapea a 'store' en la API
                'precio': precio_float,
                'negocio_id': int(negocio_id),
                'categoria': categoria,  # Enviar categoria (string) en lugar de categoria_id
                'stock': int(request.form.get('stock', 0)),
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

@devops_bp.route('/productos/<int:producto_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_producto(producto_id):
    """Editar un producto - GET muestra formulario, POST procesa actualización"""
    if request.method == 'POST':
        try:
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Obtener datos del formulario
            producto_data = {
                'nombre': request.form.get('nombre', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'precio': request.form.get('precio', '').strip(),
                'categoria': request.form.get('categoria', '').strip(),
                'stock': request.form.get('stock', '0').strip(),
                'negocio_id': request.form.get('negocio_id', '').strip(),
                'activo': request.form.get('activo') == 'on'
            }
            
            # Validar campos requeridos
            if not producto_data['nombre'] or not producto_data['precio']:
                flash('Nombre y precio son requeridos', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            try:
                producto_data['precio'] = float(producto_data['precio'])
            except ValueError:
                flash('El precio debe ser un número válido', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            if producto_data['negocio_id']:
                try:
                    producto_data['negocio_id'] = int(producto_data['negocio_id'])
                except ValueError:
                    producto_data['negocio_id'] = None
            else:
                producto_data['negocio_id'] = None
            
            if producto_data['stock']:
                try:
                    producto_data['stock'] = int(producto_data['stock'])
                except ValueError:
                    producto_data['stock'] = 0
            else:
                producto_data['stock'] = 0
            
            # Actualizar producto usando el manager
            success, message = devops_manager.update_item('productos', producto_id, producto_data)
            if success:
                flash(f'Producto "{producto_data["nombre"]}" actualizado exitosamente', 'success')
                logger.info(f"Producto {producto_id} actualizado: {producto_data['nombre']}")
            else:
                flash(f'Error al actualizar producto: {message}', 'error')
                logger.error(f"Error actualizando producto {producto_id}: {message}")
        except Exception as e:
            logger.error(f"Error actualizando producto: {e}")
            flash(f'Error interno al actualizar el producto: {str(e)}', 'error')
        return redirect(url_for('devops.gestion_productos'))
    
    # GET - Mostrar página de edición (redirigir a gestión con el modal abierto)
    # El template maneja el modal, así que redirigimos a la página de gestión
    flash('Usa el botón de editar en la tabla para modificar productos', 'info')
    return redirect(url_for('devops.gestion_productos'))

@devops_bp.route('/productos/eliminar/<int:producto_id>', methods=['POST', 'GET'])
@devops_login_required
def eliminar_producto(producto_id):
    """Eliminar un producto - acepta POST (desde formulario) y GET"""
    if request.method == 'GET':
        flash('La eliminación debe realizarse desde el botón de eliminar en la tabla', 'warning')
        return redirect(url_for('devops.gestion_productos'))
    
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return redirect(url_for('devops.gestion_productos'))
        success, message = devops_manager.delete_item('productos', producto_id)
        if success:
            flash(f'Producto eliminado exitosamente', 'success')
            logger.info(f"Producto {producto_id} eliminado")
        else:
            flash(f'Error al eliminar producto: {message}', 'error')
            logger.error(f"Error eliminando producto: {message}")
    except Exception as e:
        logger.error(f"Error eliminando producto: {e}")
        flash('Error interno al eliminar el producto', 'error')
    return redirect(url_for('devops.gestion_productos'))

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
            # Asegurar que fecha_fin tenga un valor válido
            fecha_inicio = request.form.get('fecha_inicio', '').strip()
            if not fecha_inicio:
                fecha_inicio = datetime.now().strftime('%Y-%m-%d')
            
            fecha_fin = request.form.get('fecha_fin', '').strip()
            if not fecha_fin:
                # Si no hay fecha_fin, usar 30 días desde hoy
                from datetime import timedelta
                fecha_fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            oferta_data = {
                'titulo': titulo,  # La API acepta tanto 'titulo' como 'nombre'
                'descripcion': descripcion,
                'descuento': descuento_float,
                'producto_id': int(producto_id),
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'activa': True  # La API acepta tanto 'activa' como 'activo'
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

@devops_bp.route('/ofertas/<int:oferta_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_oferta(oferta_id):
    """Editar una oferta - GET muestra formulario, POST procesa actualización"""
    if request.method == 'POST':
        try:
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            
            # Obtener datos del formulario
            oferta_data = {
                'titulo': request.form.get('titulo', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'descuento_porcentaje': request.form.get('descuento_porcentaje', '').strip(),
                'descuento_fijo': request.form.get('descuento_fijo', '').strip(),
                'activa': request.form.get('activo') == 'on'
            }
            
            # Validar campos requeridos
            if not oferta_data['titulo']:
                flash('El título es requerido', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            
            # Procesar descuentos
            if oferta_data['descuento_porcentaje']:
                try:
                    oferta_data['descuento'] = float(oferta_data['descuento_porcentaje'])
                except ValueError:
                    flash('El descuento porcentual debe ser un número válido', 'error')
                    return redirect(url_for('devops.gestion_ofertas'))
            elif oferta_data['descuento_fijo']:
                try:
                    oferta_data['descuento'] = float(oferta_data['descuento_fijo'])
                except ValueError:
                    flash('El descuento fijo debe ser un número válido', 'error')
                    return redirect(url_for('devops.gestion_ofertas'))
            else:
                flash('Debe especificar un descuento (porcentual o fijo)', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            
            # Limpiar campos no usados
            oferta_data.pop('descuento_porcentaje', None)
            oferta_data.pop('descuento_fijo', None)
            
            # Actualizar oferta usando el manager
            success, message = devops_manager.update_item('ofertas', oferta_id, oferta_data)
            if success:
                flash(f'Oferta "{oferta_data["titulo"]}" actualizada exitosamente', 'success')
                logger.info(f"Oferta {oferta_id} actualizada: {oferta_data['titulo']}")
            else:
                flash(f'Error al actualizar oferta: {message}', 'error')
                logger.error(f"Error actualizando oferta {oferta_id}: {message}")
        except Exception as e:
            logger.error(f"Error actualizando oferta: {e}")
            flash(f'Error interno al actualizar la oferta: {str(e)}', 'error')
        return redirect(url_for('devops.gestion_ofertas'))
    
    # GET - Redirigir a gestión (el template maneja el modal)
    flash('Usa el botón de editar en la tabla para modificar ofertas', 'info')
    return redirect(url_for('devops.gestion_ofertas'))

@devops_bp.route('/ofertas/eliminar/<int:oferta_id>', methods=['POST', 'GET'])
@devops_login_required
def eliminar_oferta(oferta_id):
    """Eliminar una oferta - acepta POST (desde formulario) y GET"""
    if request.method == 'GET':
        flash('La eliminación debe realizarse desde el botón de eliminar en la tabla', 'warning')
        return redirect(url_for('devops.gestion_ofertas'))
    
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return redirect(url_for('devops.gestion_ofertas'))
        success, message = devops_manager.delete_item('ofertas', oferta_id)
        if success:
            flash(f'Oferta eliminada exitosamente', 'success')
            logger.info(f"Oferta {oferta_id} eliminada")
        else:
            flash(f'Error al eliminar oferta: {message}', 'error')
            logger.error(f"Error eliminando oferta: {message}")
    except Exception as e:
        logger.error(f"Error eliminando oferta: {e}")
        flash('Error interno al eliminar la oferta', 'error')
    return redirect(url_for('devops.gestion_ofertas'))

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
        def _safe_system_status() -> dict:
            return {
                'timestamp': datetime.now().isoformat(),
                'fallback_mode': True,
                'api_url': os.getenv('BELGRANO_AHORRO_URL', ''),
                'api_configured': bool(os.getenv('BELGRANO_AHORRO_API_KEY')),
            }
        
        if not devops_manager:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'status': 'error', 'message': 'Gestor DevOps no disponible', 'data': _safe_system_status()}), 503
            else:
                flash('Gestor DevOps no disponible', 'error')
                return render_template('devops/info.html', status='error', message='Gestor DevOps no disponible', system_status=_safe_system_status())
        
        try:
            system_status = devops_manager.get_system_status()
            # Normalizar estructura mínima esperada
            if not isinstance(system_status, dict):
                system_status = _safe_system_status()
            system_status.setdefault('timestamp', datetime.now().isoformat())
            system_status.setdefault('api_url', os.getenv('BELGRANO_AHORRO_URL', ''))
            system_status.setdefault('api_configured', bool(os.getenv('BELGRANO_AHORRO_API_KEY')))
            system_status.setdefault('fallback_mode', False)
        except Exception as inner_e:
            logger.warning(f"get_system_status falló, usando fallback: {inner_e}")
            system_status = _safe_system_status()
        
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
            from devops.api_helpers import cached_request
            resp_data = cached_request(f"{base}/api/health", timeout=20, cache_ttl=60, headers=_ahorro_headers())
            # cached_request devuelve dict, simular response para compatibilidad
            class MockResponse:
                def __init__(self, data):
                    self.status_code = 200 if 'error' not in data else 500
                    self.data = data
                    self.headers = {'content-type': 'application/json'}
                def json(self):
                    return self.data if isinstance(self.data, dict) else {}
                @property
                def text(self):
                    return str(self.data)
            resp = MockResponse(resp_data)
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
                    from devops.api_helpers import cached_request
                    resp_data = cached_request(f"{base_t}{path}", timeout=20, cache_ttl=60, headers=_ticketera_headers())
                    # cached_request devuelve dict, simular response para compatibilidad
                    class MockResponse:
                        def __init__(self, data):
                            self.status_code = 200 if 'error' not in data else 500
                            self.data = data
                            self.headers = {'content-type': 'application/json'}
                        def json(self):
                            return self.data if isinstance(self.data, dict) else {}
                        @property
                        def text(self):
                            return str(self.data)
                    resp = MockResponse(resp_data)
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
    """Respuesta JSON consistente para todos los endpoints"""
    body = {'status': 'success' if ok else 'error', 'message': message}
    if data is not None:
        body['data'] = data
    return jsonify(body), status_code

def _parse_manager_response(result: tuple, default_message: str = 'ok') -> tuple:
    """Parsear respuesta del manager para extraer datos y mensajes correctamente"""
    if not result:
        return False, None, 'Manager no disponible'
    
    ok, response = result
    if ok:
        # Si es exitoso, puede venir 'ok' o datos
        if isinstance(response, dict):
            # Si response tiene 'status' y es 'success', es exitoso
            if response.get('status') == 'success':
                return True, response.get('data'), response.get('message', default_message)
            # Si response tiene 'data', extraerlo
            if 'data' in response:
                return True, response.get('data'), response.get('message', default_message)
            # Si response tiene 'message', usar ese
            if 'message' in response:
                return True, response.get('data'), response.get('message', default_message)
            # Si response es el objeto completo
            return True, response, default_message
        # Si response es 'ok' o string, es exitoso sin datos
        if response == 'ok' or (isinstance(response, str) and 'ok' in response.lower()):
            return True, None, default_message
        return True, response if response != 'ok' else None, default_message
    else:
        # Si falló, response puede ser un string o un dict con error
        if isinstance(response, dict):
            error_msg = response.get('error', response.get('message', str(response)))
            return False, None, error_msg
        return False, None, str(response) if response else 'Error desconocido'


@devops_bp.route('/api/negocios', methods=['GET', 'POST'])
@devops_login_required
def api_negocios():
    if request.method == 'GET':
        try:
            if not devops_manager:
                return _json_response(False, None, 'Manager no disponible', 503)
            items = devops_manager.get_negocios()
            # get_negocios puede devolver lista o dict con 'data'
            if isinstance(items, dict) and 'data' in items:
                items = items['data']
            return _json_response(True, items if items else [], 'Negocios obtenidos exitosamente')
        except Exception as e:
            logger.error(f"Error obteniendo negocios: {e}")
            return _json_response(False, None, f'Error al obtener negocios: {str(e)}', 500)
    
    # POST
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    payload = request.get_json(silent=True) or {}
    if not payload or 'nombre' not in payload:
        return _json_response(False, None, 'El campo "nombre" es requerido', 400)
    
    try:
        result = devops_manager.create_item('negocios', payload)
        ok, data, msg = _parse_manager_response(result, 'Negocio creado exitosamente')
        return _json_response(ok, data, msg, 201 if ok else 400)
    except Exception as e:
        logger.error(f"Error creando negocio: {e}")
        return _json_response(False, None, f'Error al crear negocio: {str(e)}', 500)


@devops_bp.route('/api/negocios/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@devops_login_required
def api_negocio_detail(item_id: int):
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    if request.method == 'GET':
        try:
            # Obtener negocio específico usando el endpoint de detalle
            ok, data = devops_manager._req('GET', f"/api/negocios/{item_id}")
            if ok:
                if isinstance(data, dict) and 'data' in data:
                    return _json_response(True, data['data'], 'Negocio obtenido exitosamente')
                return _json_response(True, data, 'Negocio obtenido exitosamente')
            else:
                error_msg = data.get('error', str(data)) if isinstance(data, dict) else str(data)
                return _json_response(False, None, error_msg, 404)
        except Exception as e:
            logger.error(f"Error obteniendo negocio {item_id}: {e}")
            return _json_response(False, None, f'Error al obtener negocio: {str(e)}', 500)
    
    if request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        if not payload:
            return _json_response(False, None, 'Datos requeridos para actualizar', 400)
        try:
            result = devops_manager.update_item('negocios', item_id, payload)
            ok, data, msg = _parse_manager_response(result, 'Negocio actualizado exitosamente')
            return _json_response(ok, data, msg, 200 if ok else 400)
        except Exception as e:
            logger.error(f"Error actualizando negocio {item_id}: {e}")
            return _json_response(False, None, f'Error al actualizar negocio: {str(e)}', 500)
    
    # DELETE
    try:
        result = devops_manager.delete_item('negocios', item_id)
        ok, data, msg = _parse_manager_response(result, 'Negocio eliminado exitosamente')
        return _json_response(ok, data, msg, 200 if ok else 400)
    except Exception as e:
        logger.error(f"Error eliminando negocio {item_id}: {e}")
        return _json_response(False, None, f'Error al eliminar negocio: {str(e)}', 500)


@devops_bp.route('/api/productos', methods=['GET', 'POST'])
@devops_login_required
def api_productos():
    if request.method == 'GET':
        try:
            if not devops_manager:
                return _json_response(False, None, 'Manager no disponible', 503)
            items = devops_manager.get_productos()
            if isinstance(items, dict) and 'data' in items:
                items = items['data']
            return _json_response(True, items if items else [], 'Productos obtenidos exitosamente')
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return _json_response(False, None, f'Error al obtener productos: {str(e)}', 500)
    
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    payload = request.get_json(silent=True) or {}
    if not payload or 'nombre' not in payload or 'precio' not in payload:
        return _json_response(False, None, 'Los campos "nombre" y "precio" son requeridos', 400)
    
    try:
        result = devops_manager.create_item('productos', payload)
        ok, data, msg = _parse_manager_response(result, 'Producto creado exitosamente')
        return _json_response(ok, data, msg, 201 if ok else 400)
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        return _json_response(False, None, f'Error al crear producto: {str(e)}', 500)


@devops_bp.route('/api/productos/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@devops_login_required
def api_producto_detail(item_id: int):
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    if request.method == 'GET':
        try:
            ok, data = devops_manager._req('GET', f"/api/productos/{item_id}")
            if ok:
                if isinstance(data, dict) and 'data' in data:
                    return _json_response(True, data['data'], 'Producto obtenido exitosamente')
                return _json_response(True, data, 'Producto obtenido exitosamente')
            else:
                error_msg = data.get('error', str(data)) if isinstance(data, dict) else str(data)
                return _json_response(False, None, error_msg, 404)
        except Exception as e:
            logger.error(f"Error obteniendo producto {item_id}: {e}")
            return _json_response(False, None, f'Error al obtener producto: {str(e)}', 500)
    
    if request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        if not payload:
            return _json_response(False, None, 'Datos requeridos para actualizar', 400)
        try:
            result = devops_manager.update_item('productos', item_id, payload)
            ok, data, msg = _parse_manager_response(result, 'Producto actualizado exitosamente')
            return _json_response(ok, data, msg, 200 if ok else 400)
        except Exception as e:
            logger.error(f"Error actualizando producto {item_id}: {e}")
            return _json_response(False, None, f'Error al actualizar producto: {str(e)}', 500)
    
    # DELETE
    try:
        result = devops_manager.delete_item('productos', item_id)
        ok, data, msg = _parse_manager_response(result, 'Producto eliminado exitosamente')
        return _json_response(ok, data, msg, 200 if ok else 400)
    except Exception as e:
        logger.error(f"Error eliminando producto {item_id}: {e}")
        return _json_response(False, None, f'Error al eliminar producto: {str(e)}', 500)


@devops_bp.route('/api/ofertas', methods=['GET', 'POST'])
@devops_login_required
def api_ofertas():
    if request.method == 'GET':
        try:
            if not devops_manager:
                return _json_response(False, None, 'Manager no disponible', 503)
            items = devops_manager.get_ofertas()
            if isinstance(items, dict) and 'data' in items:
                items = items['data']
            return _json_response(True, items if items else [], 'Ofertas obtenidas exitosamente')
        except Exception as e:
            logger.error(f"Error obteniendo ofertas: {e}")
            return _json_response(False, None, f'Error al obtener ofertas: {str(e)}', 500)
    
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    payload = request.get_json(silent=True) or {}
    if not payload or 'titulo' not in payload:
        return _json_response(False, None, 'El campo "titulo" es requerido', 400)
    
    try:
        result = devops_manager.create_item('ofertas', payload)
        ok, data, msg = _parse_manager_response(result, 'Oferta creada exitosamente')
        return _json_response(ok, data, msg, 201 if ok else 400)
    except Exception as e:
        logger.error(f"Error creando oferta: {e}")
        return _json_response(False, None, f'Error al crear oferta: {str(e)}', 500)


@devops_bp.route('/api/ofertas/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@devops_login_required
def api_oferta_detail(item_id: int):
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    if request.method == 'GET':
        try:
            ok, data = devops_manager._req('GET', f"/api/ofertas/{item_id}")
            if ok:
                if isinstance(data, dict) and 'data' in data:
                    return _json_response(True, data['data'], 'Oferta obtenida exitosamente')
                return _json_response(True, data, 'Oferta obtenida exitosamente')
            else:
                error_msg = data.get('error', str(data)) if isinstance(data, dict) else str(data)
                return _json_response(False, None, error_msg, 404)
        except Exception as e:
            logger.error(f"Error obteniendo oferta {item_id}: {e}")
            return _json_response(False, None, f'Error al obtener oferta: {str(e)}', 500)
    
    if request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        if not payload:
            return _json_response(False, None, 'Datos requeridos para actualizar', 400)
        try:
            result = devops_manager.update_item('ofertas', item_id, payload)
            ok, data, msg = _parse_manager_response(result, 'Oferta actualizada exitosamente')
            return _json_response(ok, data, msg, 200 if ok else 400)
        except Exception as e:
            logger.error(f"Error actualizando oferta {item_id}: {e}")
            return _json_response(False, None, f'Error al actualizar oferta: {str(e)}', 500)
    
    # DELETE
    try:
        result = devops_manager.delete_item('ofertas', item_id)
        ok, data, msg = _parse_manager_response(result, 'Oferta eliminada exitosamente')
        return _json_response(ok, data, msg, 200 if ok else 400)
    except Exception as e:
        logger.error(f"Error eliminando oferta {item_id}: {e}")
        return _json_response(False, None, f'Error al eliminar oferta: {str(e)}', 500)


@devops_bp.route('/api/sucursales', methods=['GET', 'POST'])
@devops_login_required
def api_sucursales():
    if request.method == 'GET':
        try:
            if not devops_manager:
                return _json_response(False, None, 'Manager no disponible', 503)
            items = devops_manager.get_sucursales()
            if isinstance(items, dict) and 'data' in items:
                items = items['data']
            return _json_response(True, items if items else [], 'Sucursales obtenidas exitosamente')
        except Exception as e:
            logger.error(f"Error obteniendo sucursales: {e}")
            return _json_response(False, None, f'Error al obtener sucursales: {str(e)}', 500)
    
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    payload = request.get_json(silent=True) or {}
    if not payload or 'nombre' not in payload:
        return _json_response(False, None, 'El campo "nombre" es requerido', 400)
    
    try:
        result = devops_manager.create_sucursal(payload)
        ok, data, msg = _parse_manager_response(result, 'Sucursal creada exitosamente')
        return _json_response(ok, data, msg, 201 if ok else 400)
    except Exception as e:
        logger.error(f"Error creando sucursal: {e}")
        return _json_response(False, None, f'Error al crear sucursal: {str(e)}', 500)


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
            producto_id = request.args.get('producto_id', type=int)
            if producto_id:
                items = devops_manager.get_precios(producto_id) if devops_manager else []
            else:
                items = devops_manager.get_precios() if devops_manager else []
            return _json_response(True, items)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    payload = request.get_json(silent=True) or {}
    # Para precios, usamos update_precio con producto_id
    producto_id = payload.get('producto_id')
    if not producto_id:
        return _json_response(False, None, 'producto_id requerido', 400)
    try:
        ok, msg = devops_manager.update_precio(producto_id, payload) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, None, msg, 200 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/categorias', methods=['GET'])
@devops_login_required
def api_categorias():
    """Obtener todas las categorías de Belgrano Ahorro"""
    try:
        if not devops_manager:
            return _json_response(False, None, 'Manager no disponible', 503)
        items = devops_manager.get_categorias()
        if isinstance(items, dict) and 'data' in items:
            items = items['data']
        return _json_response(True, items if items else [], 'Categorías obtenidas exitosamente')
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {e}")
        return _json_response(False, None, f'Error al obtener categorías: {str(e)}', 500)

@devops_bp.route('/api/categorias/<int:categoria_id>', methods=['GET'])
@devops_login_required
def api_categoria_detail(categoria_id: int):
    """Obtener una categoría específica"""
    try:
        ok, data = devops_manager.get_item_detail('categorias', categoria_id) if devops_manager else (False, 'manager no disponible')
        return _json_response(ok, data if ok else None, 'ok' if ok else str(data))
    except Exception as e:
        return _json_response(False, None, str(e), 500)

# =================================================================
# API REST para Ticketera
# =================================================================

@devops_bp.route('/api/ticketera/tickets', methods=['GET', 'POST'])
@devops_login_required
def api_ticketera_tickets():
    """Obtener o crear tickets en Ticketera"""
    if request.method == 'GET':
        try:
            if not devops_ticketera_manager:
                return _json_response(False, None, 'Ticketera manager no disponible', 503)
            tickets = devops_ticketera_manager.get_tickets()
            return _json_response(True, tickets)
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    # POST
    payload = request.get_json(silent=True) or {}
    try:
        if not devops_ticketera_manager:
            return _json_response(False, None, 'Ticketera manager no disponible', 503)
        ok, result = devops_ticketera_manager.create_ticket(payload)
        return _json_response(ok, result if ok else None, 'ok' if ok else str(result), 201 if ok else 400)
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/ticketera/tickets/<ticket_id>', methods=['GET', 'PUT', 'DELETE'])
@devops_login_required
def api_ticketera_ticket_detail(ticket_id):
    """Obtener, actualizar o eliminar un ticket específico"""
    if request.method == 'GET':
        try:
            if not devops_ticketera_manager:
                return _json_response(False, None, 'Ticketera manager no disponible', 503)
            ok, data = devops_ticketera_manager.get_ticket(ticket_id)
            return _json_response(ok, data if ok else None, 'ok' if ok else str(data))
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        try:
            if not devops_ticketera_manager:
                return _json_response(False, None, 'Ticketera manager no disponible', 503)
            ok, result = devops_ticketera_manager.update_ticket(ticket_id, payload)
            return _json_response(ok, result if ok else None, 'ok' if ok else str(result))
        except Exception as e:
            return _json_response(False, None, str(e), 500)
    # DELETE
    try:
        if not devops_ticketera_manager:
            return _json_response(False, None, 'Ticketera manager no disponible', 503)
        ok, result = devops_ticketera_manager.delete_ticket(ticket_id)
        return _json_response(ok, None, 'ok' if ok else str(result))
    except Exception as e:
        return _json_response(False, None, str(e), 500)

# =================================================================
# API de Sincronización
# =================================================================

@devops_bp.route('/api/sync/status', methods=['GET'])
@devops_login_required
def api_sync_status():
    """Obtener estado de sincronización entre sistemas"""
    try:
        if not devops_sync_manager:
            return _json_response(False, None, 'Sync manager no disponible', 503)
        status = devops_sync_manager.get_sync_status()
        return _json_response(True, status)
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/sync/negocios', methods=['POST'])
@devops_login_required
def api_sync_negocios():
    """Sincronizar negocios de Belgrano Ahorro a Ticketera"""
    try:
        if not devops_sync_manager:
            return _json_response(False, None, 'Sync manager no disponible', 503)
        results = devops_sync_manager.sync_negocios_to_ticketera()
        success = results['failed'] == 0
        return _json_response(success, results, 
                             f"Sincronizados {results['success']} negocios" if success else 
                             f"Sincronizados {results['success']}, fallaron {results['failed']}", 
                             200 if success else 207)  # 207 Multi-Status
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/sync/productos', methods=['POST'])
@devops_login_required
def api_sync_productos():
    """Sincronizar productos de Belgrano Ahorro a Ticketera"""
    try:
        if not devops_sync_manager:
            return _json_response(False, None, 'Sync manager no disponible', 503)
        results = devops_sync_manager.sync_productos_to_ticketera()
        success = results['failed'] == 0
        return _json_response(success, results,
                             f"Sincronizados {results['success']} productos" if success else
                             f"Sincronizados {results['success']}, fallaron {results['failed']}",
                             200 if success else 207)
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/sync/all', methods=['POST'])
@devops_login_required
def api_sync_all():
    """Sincronización completa de todos los datos (negocios + productos)"""
    try:
        if not devops_sync_manager:
            return _json_response(False, None, 'Sync manager no disponible', 503)
        results = devops_sync_manager.full_sync_all()
        success = results['overall_status'] == 'success'
        return _json_response(success, results,
                             'Sincronización completa exitosa' if success else 'Sincronización parcial',
                             200 if success else 207)
    except Exception as e:
        return _json_response(False, None, str(e), 500)

# =================================================================
# Endpoints adicionales de Belgrano Ahorro
# =================================================================

@devops_bp.route('/api/ahorro/negocios/<int:negocio_id>', methods=['GET'])
@devops_login_required
def api_ahorro_negocio_detail(negocio_id: int):
    """Obtener detalle de un negocio específico"""
    try:
        if not devops_manager:
            return _json_response(False, None, 'Manager no disponible', 503)
        ok, data = devops_manager.get_item_detail('negocios', negocio_id)
        return _json_response(ok, data if ok else None, 'ok' if ok else str(data))
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/ahorro/productos/<int:producto_id>', methods=['GET'])
@devops_login_required
def api_ahorro_producto_detail(producto_id: int):
    """Obtener detalle de un producto específico"""
    try:
        if not devops_manager:
            return _json_response(False, None, 'Manager no disponible', 503)
        ok, data = devops_manager.get_item_detail('productos', producto_id)
        return _json_response(ok, data if ok else None, 'ok' if ok else str(data))
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/ahorro/ofertas/<int:oferta_id>', methods=['GET'])
@devops_login_required
def api_ahorro_oferta_detail(oferta_id: int):
    """Obtener detalle de una oferta específica"""
    try:
        if not devops_manager:
            return _json_response(False, None, 'Manager no disponible', 503)
        ok, data = devops_manager.get_item_detail('ofertas', oferta_id)
        return _json_response(ok, data if ok else None, 'ok' if ok else str(data))
    except Exception as e:
        return _json_response(False, None, str(e), 500)

@devops_bp.route('/api/ahorro/sucursales/<sucursal_id>', methods=['GET'])
@devops_login_required
def api_ahorro_sucursal_detail(sucursal_id):
    """Obtener detalle de una sucursal específica"""
    try:
        if not devops_manager:
            return _json_response(False, None, 'Manager no disponible', 503)
        ok, data = devops_manager.get_item_detail('sucursales', sucursal_id)
        return _json_response(ok, data if ok else None, 'ok' if ok else str(data))
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

@devops_bp.route('/sucursales/<string:sucursal_id>/editar', methods=['GET', 'POST'])
@devops_login_required
def editar_sucursal(sucursal_id):
    """Editar una sucursal - GET muestra formulario, POST procesa actualización"""
    if request.method == 'POST':
        try:
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_sucursales'))
            
            # Obtener datos del formulario
            sucursal_data = {
                'nombre': request.form.get('nombre', '').strip(),
                'direccion': request.form.get('direccion', '').strip(),
                'telefono': request.form.get('telefono', '').strip(),
                'email': request.form.get('email', '').strip(),
                'negocio_id': request.form.get('negocio_id', '').strip(),
                'activo': request.form.get('activo') == 'on'
            }
            
            # Validar campos requeridos
            if not sucursal_data['nombre']:
                flash('El nombre es requerido', 'error')
                return redirect(url_for('devops.gestion_sucursales'))
            
            if sucursal_data['negocio_id']:
                try:
                    sucursal_data['negocio_id'] = int(sucursal_data['negocio_id'])
                except ValueError:
                    flash('El ID de negocio debe ser un número válido', 'error')
                    return redirect(url_for('devops.gestion_sucursales'))
            else:
                sucursal_data['negocio_id'] = None
            
            # Actualizar sucursal usando el manager
            success, message = devops_manager.update_item('sucursales', sucursal_id, sucursal_data)
            if success:
                flash(f'Sucursal "{sucursal_data["nombre"]}" actualizada exitosamente', 'success')
                logger.info(f"Sucursal {sucursal_id} actualizada: {sucursal_data['nombre']}")
            else:
                flash(f'Error al actualizar sucursal: {message}', 'error')
                logger.error(f"Error actualizando sucursal {sucursal_id}: {message}")
        except Exception as e:
            logger.error(f"Error actualizando sucursal: {e}")
            flash(f'Error interno al actualizar la sucursal: {str(e)}', 'error')
        return redirect(url_for('devops.gestion_sucursales'))
    
    # GET - Redirigir a gestión (el template maneja el modal)
    flash('Usa el botón de editar en la tabla para modificar sucursales', 'info')
    return redirect(url_for('devops.gestion_sucursales'))

@devops_bp.route('/sucursales/eliminar/<string:sucursal_id>', methods=['POST'])
@devops_login_required
def eliminar_sucursal(sucursal_id):
    try:
        if not devops_manager:
            flash('Error: API no configurada.', 'error')
            return redirect(url_for('devops.gestion_sucursales'))
        success, message = devops_manager.delete_item('sucursales', sucursal_id)
        if success:
            flash(f'Sucursal eliminada exitosamente', 'success')
            logger.info(f"Sucursal {sucursal_id} eliminada")
        else:
            flash(f'Error al eliminar sucursal: {message}', 'error')
            logger.error(f"Error eliminando sucursal: {message}")
    except Exception as e:
        logger.error(f"Error eliminando sucursal: {e}")
        flash('Error interno al eliminar la sucursal', 'error')
    return redirect(url_for('devops.gestion_sucursales'))

# Alias para compatibilidad con templates
@devops_bp.route('/home')
@devops_login_required
def devops_home():
    """Alias para dashboard - redirige a dashboard"""
    return redirect(url_for('devops.dashboard'))
