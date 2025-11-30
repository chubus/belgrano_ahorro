# Rutas DevOps (migradas a paquete devops)
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
import os
import sys
import requests
import logging
from datetime import datetime
from werkzeug.utils import secure_filename

# Asegurar que el directorio actual esté en el path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importación absoluta para evitar problemas de importación relativa
try:
    from devops.image_utils import save_uploaded_file, delete_old_image, get_image_url, validate_image
except ImportError:
    # Si falla, intentar con importación relativa
    from image_utils import save_uploaded_file, delete_old_image, get_image_url, validate_image

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
devops_manager = None
devops_ticketera_manager = None
devops_sync_manager = None

# Intentar múltiples métodos de importación
import sys
import os

# Asegurar que el directorio padre esté en sys.path para imports absolutos
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    # Método 1: Import relativo (cuando se usa como paquete devops)
    from .manager_unified import (
        devops_manager_unified,
        devops_ticketera_manager,
        devops_sync_manager
    )
    devops_manager = devops_manager_unified
    logger.info("✅ Gestor DevOps unificado importado (import relativo)")
except ImportError as e1:
    try:
        # Método 2: Import absoluto desde devops.manager_unified
        from devops.manager_unified import (
            devops_manager_unified,
            devops_ticketera_manager,
            devops_sync_manager
        )
        devops_manager = devops_manager_unified
        logger.info("✅ Gestor DevOps unificado importado (import absoluto devops.manager_unified)")
    except ImportError as e2:
        try:
            # Método 3: Import directo desde el directorio actual
            # Asegurar que el directorio actual esté en sys.path
            if _current_dir not in sys.path:
                sys.path.insert(0, _current_dir)
            from manager_unified import (
                devops_manager_unified,
                devops_ticketera_manager,
                devops_sync_manager
            )
            devops_manager = devops_manager_unified
            logger.info("✅ Gestor DevOps unificado importado (import directo)")
        except ImportError as e3:
            logger.error(f"❌ No se pudo importar manager_unified")
            logger.error(f"   Intentado import relativo: {e1}")
            logger.error(f"   Intentado import absoluto: {e2}")
            logger.error(f"   Intentado import directo: {e3}")
            logger.error(f"   sys.path: {sys.path[:5]}")
            logger.error(f"   Directorio actual: {_current_dir}")
            logger.error(f"   Directorio padre: {_parent_dir}")
except Exception as e:
    logger.error(f"❌ Error inesperado importando manager_unified: {e}")
    import traceback
    logger.error(traceback.format_exc())

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
        expected_password = os.getenv('DEVOPS_PASSWORD', 'DevOps2025!Secure')
        
        # Log para debugging (sin exponer la contraseña completa)
        logger.info(f"🔐 Intento de login - Usuario recibido: '{username}'")
        logger.info(f"🔐 Usuario esperado: '{expected_username}'")
        logger.info(f"🔐 Contraseña recibida tiene {len(password) if password else 0} caracteres")
        logger.info(f"🔐 Contraseña esperada tiene {len(expected_password)} caracteres")
        logger.info(f"🔐 Primeros 3 chars de contraseña recibida: '{password[:3] if password else ''}'")
        logger.info(f"🔐 Primeros 3 chars de contraseña esperada: '{expected_password[:3]}'")
        logger.info(f"🔐 Últimos 3 chars de contraseña recibida: '{password[-3:] if password else ''}'")
        logger.info(f"🔐 Últimos 3 chars de contraseña esperada: '{expected_password[-3:]}'")
        logger.info(f"🔐 Usuario coincide: {username == expected_username}")
        logger.info(f"🔐 Contraseña coincide: {password == expected_password}")
        logger.info(f"🔐 Contraseña esperada repr: {repr(expected_password)}")
        
        if username == expected_username and password == expected_password:
            session['devops_authenticated'] = True
            flash('Login exitoso', 'success')
            logger.info(f"✅ Login exitoso para usuario: {username}")
            return redirect(url_for('devops.dashboard'))
        else:
            flash('Credenciales inválidas', 'error')
            logger.warning(f"❌ Login fallido para usuario: {username}")
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
        # Verificar variables de entorno directamente primero
        belgrano_url = os.getenv('BELGRANO_AHORRO_URL', '').strip().rstrip('/')
        belgrano_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', '').strip()
        
        # Valores por defecto seguros
        DEFAULT_URL = 'https://belgranoahorro-aliq.onrender.com'
        DEFAULT_API_KEY = 'belgrano_ahorro_api_key_2025'
        
        # Si no hay URL, usar valor por defecto
        if not belgrano_url:
            belgrano_url = DEFAULT_URL
            os.environ['BELGRANO_AHORRO_URL'] = belgrano_url
            logger.info(f"✅ Usando URL por defecto: {belgrano_url}")
        else:
            logger.info(f"✅ Usando URL configurada: {belgrano_url}")
        
        # Si no hay API key, usar valor por defecto
        if not belgrano_api_key:
            belgrano_api_key = DEFAULT_API_KEY
            os.environ['BELGRANO_AHORRO_API_KEY'] = belgrano_api_key
            logger.info("✅ Usando API key por defecto")
        else:
            logger.info(f"✅ Usando API key configurada ({len(belgrano_api_key)} caracteres)")
        
        # Asegurar que los valores están establecidos (después de aplicar defaults)
        belgrano_url = belgrano_url or DEFAULT_URL
        belgrano_api_key = belgrano_api_key or DEFAULT_API_KEY
        
        # Establecer en entorno si no estaban
        if not os.getenv('BELGRANO_AHORRO_URL'):
            os.environ['BELGRANO_AHORRO_URL'] = belgrano_url
        if not os.getenv('BELGRANO_AHORRO_API_KEY'):
            os.environ['BELGRANO_AHORRO_API_KEY'] = belgrano_api_key
        
        # Log informativo (no error, ya que tenemos valores por defecto)
        using_defaults = (
            belgrano_url == DEFAULT_URL or 
            belgrano_api_key == DEFAULT_API_KEY
        )
        if using_defaults:
            logger.info("ℹ️ Usando valores por defecto para API. Para producción, configure BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY en variables de entorno.")
        
        # Verificar si el manager existe y está configurado
        # Intentar acceder al manager para forzar inicialización lazy
        manager = None
        manager_error = None
        try:
            if devops_manager is None:
                manager_error = "devops_manager es None - verificar logs de importación"
                logger.error("❌ devops_manager es None")
            else:
                # Si es un LazyManager, acceder para forzar inicialización
                if hasattr(devops_manager, '_ensure_instance'):
                    try:
                        manager = devops_manager._ensure_instance()
                        logger.info("✅ Manager inicializado correctamente")
                    except Exception as e:
                        manager_error = f"Error inicializando manager: {str(e)}"
                        logger.error(f"❌ {manager_error}")
                        import traceback
                        logger.error(traceback.format_exc())
                else:
                    manager = devops_manager
                    logger.info("✅ Manager obtenido directamente")
        except Exception as e:
            manager_error = f"Error accediendo al manager: {str(e)}"
            logger.error(f"❌ {manager_error}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Verificar también el manager
        if not manager:
            error_msg = (
                'Error: El manager de DevOps no pudo inicializarse. '
                f'{manager_error if manager_error else "Verifique los logs del servidor para más detalles."}'
            )
            flash(error_msg, 'error')
            logger.error(f"❌ Manager no disponible - {manager_error}")
            return render_template('devops/dashboard.html', negocios=[], productos=[], ofertas=[], sucursales=[])
        
        # Verificar si el manager está configurado
        try:
            if hasattr(manager, 'is_configured'):
                if not manager.is_configured():
                    error_msg = (
                        'Error: API de Belgrano Ahorro no configurada correctamente. '
                        f'URL: {"✅" if belgrano_url else "❌"}, '
                        f'API_KEY: {"✅" if belgrano_api_key else "❌"}. '
                        'Verifique las variables de entorno.'
                    )
                    flash(error_msg, 'error')
                    logger.warning(f"⚠️ Manager no configurado - URL: {belgrano_url}, API_KEY: {'CONFIGURADA' if belgrano_api_key else 'NO CONFIGURADA'}")
                    return render_template('devops/dashboard.html', negocios=[], productos=[], ofertas=[], sucursales=[])
            else:
                logger.warning("⚠️ Manager no tiene método is_configured()")
        except Exception as e:
            logger.error(f"❌ Error verificando configuración del manager: {e}")
            import traceback
            logger.error(traceback.format_exc())
        try:
            negocios = devops_manager.get_negocios() or []
            productos = devops_manager.get_productos() or []
            ofertas = devops_manager.get_ofertas() or []
            sucursales = devops_manager.get_sucursales() or []
        except Exception as fetch_error:
            logger.error(f"[DEVOPS] ❌ Error obteniendo datos de la API: {fetch_error}")
            import traceback
            logger.error(traceback.format_exc())
            negocios = productos = ofertas = sucursales = []
            flash('La API de Belgrano Ahorro no respondió. Mostrando panel sin datos.', 'warning')
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
            # CORRECCIÓN: Asegurar que activo sea boolean (no integer)
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            # Obtener activo del formulario y convertirlo a boolean
            activo_raw = request.form.get('activo', 'true')
            activo = _to_boolean(activo_raw, default=True)
            
            # Procesar imagen si existe
            image_url = None
            if 'logo_file' in request.files:
                file = request.files['logo_file']
                if file and file.filename:
                    try:
                        from image_utils import image_to_base64
                    except ImportError:
                        try:
                            from devops.image_utils import image_to_base64
                        except ImportError:
                            from .image_utils import image_to_base64
                    
                    base64_data, error = image_to_base64(file)
                    if error:
                        flash(f'Advertencia: {error}. El negocio se creará sin imagen.', 'warning')
                        logger.warning(f"Error procesando imagen para negocio: {error}")
                    else:
                        image_url = base64_data
                        logger.info(f"✅ Imagen procesada para negocio: {len(base64_data)} caracteres")
            
            negocio_data = {
                'nombre': nombre,
                'descripcion': descripcion,
                'logo': request.form.get('logo', ''),
                'image_url': image_url or request.form.get('image_url', ''),  # Base64 o URL
                'telefono': request.form.get('telefono', ''),
                'direccion': request.form.get('direccion', ''),
                'email': request.form.get('email', ''),
                'activo': activo  # Asegurar que sea boolean (True/False), no integer
            }
            success, message = devops_manager.create_item('negocios', negocio_data)
            if success:
                flash(f'Negocio "{nombre}" creado exitosamente', 'success')
                logger.info(f"Negocio creado y sincronizado: {nombre} (con imagen: {bool(image_url)})")
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
            
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            
            # Procesar nueva imagen si existe
            image_url = None
            if 'logo_file' in request.files:
                file = request.files['logo_file']
                if file and file.filename:
                    try:
                        from image_utils import save_uploaded_file
                    except ImportError:
                        try:
                            from devops.image_utils import save_uploaded_file
                        except ImportError:
                            from .image_utils import save_uploaded_file
                    
                    # Usar save_uploaded_file en lugar de image_to_base64
                    saved_url, error = save_uploaded_file(file, 'business', negocio_id)
                    if error:
                        flash(f'Advertencia: {error}. Se mantendrá la imagen actual.', 'warning')
                        logger.warning(f"Error procesando nueva imagen para negocio {negocio_id}: {error}")
                    else:
                        image_url = saved_url
                        logger.info(f"✅ Nueva imagen subida a Cloudinary para negocio {negocio_id}: {saved_url}")
            
            # Si no hay nueva imagen, mantener la actual
            if not image_url:
                image_url = request.form.get('image_url_actual', '')
            
            # Obtener datos del formulario
            activo_raw = request.form.get('activo', 'false')
            negocio_data = {
                'nombre': request.form.get('nombre', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'direccion': request.form.get('direccion', '').strip(),
                'telefono': request.form.get('telefono', '').strip(),
                'email': request.form.get('email', '').strip(),
                'image_url': image_url,  # Nueva o actual
                'activo': _to_boolean(activo_raw, default=True)  # CORRECCIÓN: Usar _to_boolean() en lugar de == 'on'
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

def _normalizar_producto(producto):
    """
    Normalizar tipos de datos de un producto.
    Convierte campos numéricos de string a sus tipos correctos.
    """
    if not isinstance(producto, dict):
        return producto
    
    producto_normalizado = producto.copy()
    
    # Normalizar campos numéricos
    campos_numericos = ['id', 'precio', 'stock', 'negocio_id', 'categoria_id']
    for campo in campos_numericos:
        if campo in producto_normalizado and producto_normalizado[campo] is not None:
            try:
                if campo == 'precio':
                    producto_normalizado[campo] = float(producto_normalizado[campo])
                else:
                    producto_normalizado[campo] = int(producto_normalizado[campo])
            except (ValueError, TypeError):
                # Si no se puede convertir, mantener el valor original o usar default
                if campo == 'precio':
                    producto_normalizado[campo] = 0.0
                elif campo == 'stock':
                    producto_normalizado[campo] = 0
                else:
                    producto_normalizado[campo] = None
    
    # Normalizar campos booleanos
    campos_booleanos = ['activo', 'destacado']
    for campo in campos_booleanos:
        if campo in producto_normalizado:
            valor = producto_normalizado[campo]
            if isinstance(valor, bool):
                continue
            elif isinstance(valor, str):
                producto_normalizado[campo] = valor.lower() in ('true', '1', 'yes', 'on', 'si', 'sí')
            elif isinstance(valor, int):
                producto_normalizado[campo] = bool(valor)
            else:
                producto_normalizado[campo] = True if campo == 'activo' else False
    
    return producto_normalizado

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
            
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            activo_raw = request.form.get('activo', 'true')
            destacado_raw = request.form.get('destacado', 'false')
            
            # Procesar imagen del producto si existe
            image_url = None
            imagen_filename = ''
            if 'imagen_file' in request.files:
                file = request.files['imagen_file']
                if file and file.filename:
                    try:
                        from image_utils import save_uploaded_file
                    except ImportError:
                        try:
                            from devops.image_utils import save_uploaded_file
                        except ImportError:
                            from .image_utils import save_uploaded_file
                    
                    # Guardar archivo y obtener URL pública
                    # Usamos ID 0 porque es creación
                    saved_url, error = save_uploaded_file(file, 'product', 0)
                    
                    if error:
                        flash(f'Advertencia: {error}. El producto se creará sin imagen.', 'warning')
                        logger.warning(f"Error procesando imagen para producto: {error}")
                    else:
                        image_url = saved_url
                        imagen_filename = file.filename
                        logger.info(f"✅ Imagen guardada para producto: {saved_url}")
            
            producto_data = {
                'nombre': nombre,
                'descripcion': descripcion,  # Se mapea a 'store' en la API
                'precio': precio_float,
                'negocio_id': int(negocio_id),
                'categoria': categoria,  # Enviar categoria (string) en lugar de categoria_id
                'stock': int(request.form.get('stock', 0)),
                'imagen': imagen_filename or request.form.get('imagen', ''),  # Nombre del archivo
                'image_url': image_url or request.form.get('image_url', ''),  # Base64 o URL
                'activo': _to_boolean(activo_raw, default=True),  # CORRECCIÓN: Usar _to_boolean() para consistencia
                'destacado': _to_boolean(destacado_raw, default=False)  # CORRECCIÓN: Agregar conversión para destacado
            }
            success, message = devops_manager.create_item('productos', producto_data)
            if success:
                flash(f'Producto "{nombre}" creado exitosamente', 'success')
                logger.info(f"Producto creado y sincronizado: {nombre} (con imagen: {bool(image_url)})")
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
        productos_raw = devops_manager.get_productos()
        negocios = devops_manager.get_negocios()
        
        # Normalizar tipos de datos de productos
        if isinstance(productos_raw, list):
            productos = [_normalizar_producto(p) for p in productos_raw]
        else:
            productos = []
        
        return render_template('devops/productos.html', productos=productos, negocios=negocios)
    except Exception as e:
        logger.error(f"Error cargando productos: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            
            # Procesar nueva imagen si existe
            image_url = None
            imagen_filename = ''
            if 'imagen_file' in request.files:
                file = request.files['imagen_file']
                if file and file.filename:
                    try:
                        from image_utils import save_uploaded_file
                    except ImportError:
                        try:
                            from devops.image_utils import save_uploaded_file
                        except ImportError:
                            from .image_utils import save_uploaded_file
                    
                    # Guardar archivo y obtener URL pública
                    saved_url, error = save_uploaded_file(file, 'product', producto_id)
                    
                    if error:
                        flash(f'Advertencia: {error}. Se mantendrá la imagen actual.', 'warning')
                        logger.warning(f"Error procesando nueva imagen para producto {producto_id}: {error}")
                    else:
                        image_url = saved_url
                        imagen_filename = file.filename
                        logger.info(f"✅ Nueva imagen guardada para producto {producto_id}: {saved_url}")
            
            # Si no hay nueva imagen, mantener la actual
            if not image_url:
                image_url = request.form.get('image_url_actual', '')
                imagen_filename = request.form.get('imagen_actual', '')
            
            activo_raw = request.form.get('activo', 'false')
            destacado_raw = request.form.get('destacado', 'false')
            producto_data = {
                'nombre': request.form.get('nombre', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'precio': request.form.get('precio', '').strip(),
                'categoria': request.form.get('categoria', '').strip(),
                'stock': request.form.get('stock', '0').strip(),
                'negocio_id': request.form.get('negocio_id', '').strip(),
                'imagen': imagen_filename,  # Nombre del archivo (nuevo o actual)
                'image_url': image_url,  # Base64 o URL (nuevo o actual)
                'activo': _to_boolean(activo_raw, default=True),  # CORRECCIÓN: Usar _to_boolean() en lugar de == 'on'
                'destacado': _to_boolean(destacado_raw, default=False)  # CORRECCIÓN: Agregar conversión para destacado
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
            
            # Validar título
            if not titulo:
                flash('El título es requerido', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            
            if not devops_manager:
                flash('Error: API no configurada.', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            activa_raw = request.form.get('activo', 'true')
            
            # Procesar descuentos
            descuento_porcentaje = float(request.form.get('descuento_porcentaje', 0))
            descuento_fijo = float(request.form.get('descuento_fijo', 0))
            
            # Procesar imagen de la oferta si existe
            image_url = None
            imagen_filename = ''
            if 'imagen_file' in request.files:
                file = request.files['imagen_file']
                if file and file.filename:
                    try:
                        from image_utils import save_uploaded_file
                    except ImportError:
                        try:
                            from devops.image_utils import save_uploaded_file
                        except ImportError:
                            from .image_utils import save_uploaded_file
                    
                    # Guardar archivo y obtener URL pública
                    # Usamos 'product' porque ofertas no tiene carpeta propia en image_utils, o podemos agregarla
                    # image_utils valida business, branch, product. Usemos 'product' por ahora o agreguemos 'offer'
                    # Pero save_uploaded_file valida entity_type.
                    # Vamos a usar 'product' ya que las ofertas suelen ser de productos.
                    saved_url, error = save_uploaded_file(file, 'product', 0)
                    
                    if error:
                        flash(f'Advertencia: {error}. La oferta se creará sin imagen.', 'warning')
                        logger.warning(f"Error procesando imagen para oferta: {error}")
                    else:
                        image_url = saved_url
                        imagen_filename = file.filename
                        logger.info(f"✅ Imagen guardada para oferta: {saved_url}")
            
            oferta_data = {
                'titulo': titulo,
                'descripcion': descripcion,
                'descuento_porcentaje': descuento_porcentaje,
                'descuento_fijo': descuento_fijo,
                'imagen': imagen_filename or request.form.get('imagen', ''),  # Nombre del archivo
                'image_url': image_url or request.form.get('image_url', ''),  # Base64 o URL
                'activa': _to_boolean(activa_raw, default=True)
            }
            success, message = devops_manager.create_item('ofertas', oferta_data)
            if success:
                flash(f'Oferta "{titulo}" creada exitosamente', 'success')
                logger.info(f"Oferta creada y sincronizada: {titulo} (con imagen: {bool(image_url)})")
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
            
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            
            # Procesar nueva imagen si existe
            image_url = None
            imagen_filename = ''
            if 'imagen_file' in request.files:
                file = request.files['imagen_file']
                if file and file.filename:
                    try:
                        from image_utils import save_uploaded_file
                    except ImportError:
                        try:
                            from devops.image_utils import save_uploaded_file
                        except ImportError:
                            from .image_utils import save_uploaded_file
                    
                    # Guardar archivo y obtener URL pública
                    saved_url, error = save_uploaded_file(file, 'product', oferta_id)
                    
                    if error:
                        flash(f'Advertencia: {error}. Se mantendrá la imagen actual.', 'warning')
                        logger.warning(f"Error procesando nueva imagen para oferta {oferta_id}: {error}")
                    else:
                        image_url = saved_url
                        imagen_filename = file.filename
                        logger.info(f"✅ Nueva imagen guardada para oferta {oferta_id}: {saved_url}")
            
            # Si no hay nueva imagen, mantener la actual
            if not image_url:
                image_url = request.form.get('image_url_actual', '')
                imagen_filename = request.form.get('imagen_actual', '')
            
            activa_raw = request.form.get('activo', 'false')
            # Obtener datos del formulario
            oferta_data = {
                'titulo': request.form.get('titulo', '').strip(),
                'descripcion': request.form.get('descripcion', '').strip(),
                'descuento_porcentaje': request.form.get('descuento_porcentaje', '').strip(),
                'descuento_fijo': request.form.get('descuento_fijo', '').strip(),
                'imagen': imagen_filename,  # Nombre del archivo (nuevo o actual)
                'image_url': image_url,  # Base64 o URL (nuevo o actual)
                'activa': _to_boolean(activa_raw, default=True)  # CORRECCIÓN: Usar _to_boolean() en lugar de == 'on'
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
            try:
                from devops.api_helpers import cached_request
            except ImportError:
                try:
                    from .api_helpers import cached_request
                except ImportError:
                    from api_helpers import cached_request
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
                    try:
                        from devops.api_helpers import cached_request
                    except ImportError:
                        try:
                            from .api_helpers import cached_request
                        except ImportError:
                            from api_helpers import cached_request
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
    
    # CORRECCIÓN: Asegurar que activo sea boolean (no integer)
    # Helper para convertir a boolean
    def _to_boolean(value, default=True):
        """Convertir valor a boolean de forma segura"""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return True if value != 0 else False
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                return True
            if value_lower in ('false', '0', 'no', 'off'):
                return False
        return default
    
    # Convertir activo a boolean si está presente
    if 'activo' in payload:
        payload['activo'] = _to_boolean(payload['activo'], default=True)
    else:
        payload['activo'] = True  # Default a True si no se especifica
    
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
            items_raw = devops_manager.get_productos()
            if isinstance(items_raw, dict) and 'data' in items_raw:
                items_raw = items_raw['data']
            
            # Normalizar tipos de datos de productos
            if isinstance(items_raw, list):
                items = [_normalizar_producto(p) for p in items_raw]
            else:
                items = []
            
            return _json_response(True, items if items else [], 'Productos obtenidos exitosamente')
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return _json_response(False, None, f'Error al obtener productos: {str(e)}', 500)
    
    if not devops_manager:
        return _json_response(False, None, 'Manager no disponible', 503)
    
    payload = request.get_json(silent=True) or {}
    if not payload or 'nombre' not in payload or 'precio' not in payload:
        return _json_response(False, None, 'Los campos "nombre" y "precio" son requeridos', 400)
    
    # CORRECCIÓN: Asegurar que activo y destacado sean boolean (no integer)
    # Helper para convertir a boolean
    def _to_boolean(value, default=True):
        """Convertir valor a boolean de forma segura"""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return True if value != 0 else False
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                return True
            if value_lower in ('false', '0', 'no', 'off'):
                return False
        return default
    
    # Convertir activo y destacado a boolean si están presentes
    if 'activo' in payload:
        payload['activo'] = _to_boolean(payload['activo'], default=True)
    else:
        payload['activo'] = True  # Default a True si no se especifica
    
    if 'destacado' in payload:
        payload['destacado'] = _to_boolean(payload['destacado'], default=False)
    else:
        payload['destacado'] = False  # Default a False si no se especifica
    
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
                producto_raw = data['data'] if isinstance(data, dict) and 'data' in data else data
                # Normalizar tipos de datos del producto
                producto = _normalizar_producto(producto_raw) if isinstance(producto_raw, dict) else producto_raw
                return _json_response(True, producto, 'Producto obtenido exitosamente')
            else:
                error_msg = data.get('error', str(data)) if isinstance(data, dict) else str(data)
                return _json_response(False, None, error_msg, 404)
        except Exception as e:
            logger.error(f"Error obteniendo producto {item_id}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
    
    # CORRECCIÓN: Asegurar que activa/activo sea boolean (no integer)
    # Helper para convertir a boolean
    def _to_boolean(value, default=True):
        """Convertir valor a boolean de forma segura"""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return True if value != 0 else False
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                return True
            if value_lower in ('false', '0', 'no', 'off'):
                return False
        return default
    
    # Convertir activa/activo a boolean si está presente
    if 'activa' in payload:
        payload['activa'] = _to_boolean(payload['activa'], default=True)
    elif 'activo' in payload:
        payload['activo'] = _to_boolean(payload['activo'], default=True)
        # Normalizar a 'activa' para ofertas
        payload['activa'] = payload.pop('activo')
    else:
        payload['activa'] = True  # Default a True si no se especifica
    
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
    
    # CORRECCIÓN: Asegurar que activo sea boolean (no integer)
    # Helper para convertir a boolean
    def _to_boolean(value, default=True):
        """Convertir valor a boolean de forma segura"""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return True if value != 0 else False
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                return True
            if value_lower in ('false', '0', 'no', 'off'):
                return False
        return default
    
    # Convertir activo a boolean si está presente
    if 'activo' in payload:
        payload['activo'] = _to_boolean(payload['activo'], default=True)
    else:
        payload['activo'] = True  # Default a True si no se especifica
    
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
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            activo_raw = request.form.get('activo', 'true')
            sucursal_data = {
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'negocio_id': negocio_id,
                'activo': _to_boolean(activo_raw, default=True)  # CORRECCIÓN: Usar _to_boolean() para consistencia
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
            
            # Helper para convertir a boolean
            def _to_boolean(value, default=True):
                """Convertir valor a boolean de forma segura"""
                if value is None:
                    return default
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return True if value != 0 else False
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ('true', '1', 'yes', 'on', 'si', 'sí'):
                        return True
                    if value_lower in ('false', '0', 'no', 'off'):
                        return False
                return default
            
            activo_raw = request.form.get('activo', 'false')
            # Obtener datos del formulario
            sucursal_data = {
                'nombre': request.form.get('nombre', '').strip(),
                'direccion': request.form.get('direccion', '').strip(),
                'telefono': request.form.get('telefono', '').strip(),
                'email': request.form.get('email', '').strip(),
                'negocio_id': request.form.get('negocio_id', '').strip(),
                'activo': _to_boolean(activo_raw, default=True)  # CORRECCIÓN: Usar _to_boolean() en lugar de == 'on'
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

# =================================================================
# Endpoint para carga de imágenes
# =================================================================

@devops_bp.route('/api/upload-image', methods=['POST'])
@devops_login_required
def upload_image():
    """
    Endpoint para cargar imágenes para negocios, sucursales o productos.
    
    Parámetros (multipart/form-data):
    - file: Archivo de imagen a subir (obligatorio)
    - entity_type: Tipo de entidad (business, branch, product) (obligatorio)
    - entity_id: ID de la entidad (obligatorio)
    
    Retorna:
    - 200 OK: { success: true, image_url: "ruta/a/la/imagen" }
    - 400 Bad Request: { error: "mensaje de error" }
    - 500 Error interno del servidor
    """
    try:
        # Validar que se haya enviado un archivo
        if 'file' not in request.files:
            return jsonify({"error": "No se ha proporcionado ningún archivo"}), 400
            
        file = request.files['file']
        
        # Validar que el archivo tenga un nombre
        if file.filename == '':
            return jsonify({"error": "No se ha seleccionado ningún archivo"}), 400
            
        # Validar tipo de entidad
        entity_type = request.form.get('entity_type')
        if not entity_type or entity_type not in ['business', 'branch', 'product']:
            return jsonify({
                "error": "Tipo de entidad no válido. Debe ser 'business', 'branch' o 'product'"
            }), 400
            
        # Validar ID de entidad
        entity_id = request.form.get('entity_id')
        if not entity_id:
            return jsonify({"error": "Se requiere el ID de la entidad"}), 400
            
        # Validar que el ID sea un número entero
        try:
            entity_id = int(entity_id)
        except ValueError:
            return jsonify({"error": "El ID de la entidad debe ser un número entero"}), 400
        
        # Guardar la imagen
        filepath, error = save_uploaded_file(file, entity_type, entity_id)
        if error:
            return jsonify({"error": error}), 400
            
        # Construir la URL pública de la imagen
        image_url = f"/devops/media/{filepath}"
        
        # Actualizar la URL de la imagen en la entidad correspondiente
        try:
            if entity_type == 'business':
                success, message = devops_manager.actualizar_negocio(entity_id, {'image_url': image_url})
            elif entity_type == 'branch':
                success, message = devops_manager.actualizar_sucursal(entity_id, {'image_url': image_url})
            else:  # product
                success, message = devops_manager.actualizar_producto(entity_id, {'image_url': image_url})
                
            if not success:
                # Si falla la actualización, eliminar la imagen subida
                delete_old_image(filepath)
                return jsonify({"error": f"Error al actualizar la entidad: {message}"}), 500
                
        except Exception as e:
            # Si hay un error, eliminar la imagen subida
            delete_old_image(filepath)
            logger.error(f"Error al actualizar la entidad: {str(e)}")
            return jsonify({"error": f"Error al actualizar la entidad: {str(e)}"}), 500
            
        # Devolver la URL de la imagen
        return jsonify({
            "success": True,
            "image_url": image_url,
            "message": "Imagen cargada correctamente"
        })
        
    except Exception as e:
        logger.error(f"Error en upload_image: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

# =================================================================
# Ruta para servir archivos estáticos (imágenes)
# =================================================================

@devops_bp.route('/media/<path:filename>')
def serve_media(filename):
    """
    Sirve archivos estáticos desde el directorio de uploads.
    
    Parámetros:
    - filename: Ruta relativa del archivo dentro del directorio de uploads
    
    Ejemplo: /media/business/uuid.jpg
    """
    try:
        # Validar que el archivo esté dentro del directorio de uploads
        safe_path = os.path.join('uploads', filename)
        # Normalizar rutas para prevenir path traversal
        safe_path = os.path.normpath(safe_path)
        uploads_dir = os.path.normpath('uploads')
        
        if not safe_path.startswith(uploads_dir):
            return "Acceso denegado", 403
            
        # Verificar que el archivo exista
        if not os.path.isfile(safe_path):
            return "Archivo no encontrado", 404
        
        # Obtener directorio y nombre del archivo usando rutas absolutas
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_dir, safe_path)
        directory = os.path.dirname(full_path)
        file_name = os.path.basename(full_path)
        
        # Servir el archivo usando send_from_directory
        return send_from_directory(directory, file_name)
        
    except Exception as e:
        logger.error(f"Error al servir archivo {filename}: {str(e)}")
        return "Error al servir el archivo", 500
