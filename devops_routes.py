# =================================================================
# RUTAS DEVOPS CORREGIDAS - SOLO DATOS REALES DE BELGRANO AHORRO
# =================================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint DevOps
devops_bp = Blueprint('devops', __name__, url_prefix='/devops')

# Importar gestor DevOps unificado
try:
    from devops_belgrano_manager_unified import devops_manager_unified as devops_manager
    logger.info("✅ Gestor DevOps unificado inicializado")
except Exception as e:
    # Intento adicional: agregar raíz del proyecto al sys.path y reintentar
    try:
        import sys, os
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from devops_belgrano_manager_unified import devops_manager_unified as devops_manager  # type: ignore
        logger.info("✅ Gestor DevOps unificado inicializado tras ajustar sys.path")
    except Exception as e2:
        logger.error(f"❌ No se pudo importar devops_belgrano_manager_unified: {e2}")
        devops_manager = None

# =================================================================
# MIDDLEWARE DE AUTENTICACIÓN
# =================================================================

def devops_login_required(f):
    """Decorador para requerir autenticación DevOps"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('devops_authenticated'):
            return redirect(url_for('devops.devops_login'))
        return f(*args, **kwargs)
    return decorated_function

@devops_bp.route('/login', methods=['GET', 'POST'])
def devops_login():
    """Login DevOps"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Credenciales simples (en producción usar hash)
        if username == 'devops' and password == 'devops_password':
            session['devops_authenticated'] = True
            flash('Login exitoso', 'success')
            return redirect(url_for('devops.dashboard'))
        else:
            flash('Credenciales inválidas', 'error')
    
    return render_template('devops/login.html')

@devops_bp.route('/logout')
def devops_logout():
    """Logout DevOps"""
    session.pop('devops_authenticated', None)
    flash('Sesión cerrada', 'info')
    return redirect(url_for('devops.devops_login'))

# =================================================================
# DASHBOARD PRINCIPAL
# =================================================================

@devops_bp.route('/')
@devops_bp.route('/dashboard')
@devops_login_required
def dashboard():
    """Dashboard principal DevOps"""
    try:
        if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
            flash('Servicio DevOps temporalmente no disponible. Configure las variables de entorno.', 'error')
            return render_template('devops/dashboard.html', 
                                 negocios=[], productos=[], ofertas=[], sucursales=[])
        
        # Obtener datos reales de API
        negocios = devops_manager.get_negocios()
        productos = devops_manager.get_productos()
        ofertas = devops_manager.get_ofertas()
        sucursales = devops_manager.get_sucursales()
        
        return render_template('devops/dashboard.html', 
                             negocios=negocios, productos=productos, 
                             ofertas=ofertas, sucursales=sucursales)
    except Exception as e:
        logger.error(f"Error cargando dashboard: {e}")
        flash('Error interno al cargar dashboard.', 'error')
        return render_template('devops/dashboard.html', 
                             negocios=[], productos=[], ofertas=[], sucursales=[])

# =================================================================
# GESTIÓN DE NEGOCIOS
# =================================================================

@devops_bp.route('/negocios', methods=['GET', 'POST'])
@devops_login_required
def gestion_negocios():
    """Gestión completa de negocios - SOLO DATOS REALES"""
    
    # Manejar POST requests (crear negocio)
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            
            if not all([nombre, descripcion]):
                flash('Nombre y descripción son requeridos', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Verificar que el gestor esté disponible
            if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
                flash('Error: API no configurada. Verifique las variables de entorno BELGRANO_AHORRO_URL y BELGRANO_AHORRO_API_KEY', 'error')
                return redirect(url_for('devops.gestion_negocios'))
            
            # Crear negocio usando el gestor DevOps
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
                logger.info(f"Negocio creado desde DevOps: {nombre}")
            else:
                flash(f'Error al crear negocio: {message}', 'error')
                logger.error(f"Error al crear negocio en API: {message}")
                
        except Exception as e:
            logger.error(f"Error creando negocio desde DevOps: {e}")
            flash(f'Error interno al crear el negocio: {str(e)}', 'error')
        
        return redirect(url_for('devops.gestion_negocios'))
    
    # GET request - mostrar negocios
    try:
        if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
            flash('Servicio DevOps temporalmente no disponible. Configure las variables de entorno.', 'error')
            return render_template('devops/negocios.html', negocios=[], config_ok=False)
        
        negocios = devops_manager.get_negocios()
        config_ok = True
        return render_template('devops/negocios.html', negocios=negocios, config_ok=config_ok)
    except Exception as e:
        logger.error(f"Error cargando negocios: {e}")
        flash('Error interno al cargar negocios.', 'error')
        return render_template('devops/negocios.html', negocios=[], config_ok=False)

# =================================================================
# GESTIÓN DE PRODUCTOS
# =================================================================

@devops_bp.route('/productos', methods=['GET', 'POST'])
@devops_login_required
def gestion_productos():
    """Gestión completa de productos - SOLO DATOS REALES"""
    
    # Manejar POST requests (crear producto)
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
            
            # Verificar que el gestor esté disponible
            if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
                flash('Error: API no configurada. Verifique las variables de entorno.', 'error')
                return redirect(url_for('devops.gestion_productos'))
            
            # Crear producto usando el gestor DevOps
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
                logger.info(f"Producto creado desde DevOps: {nombre}")
            else:
                flash(f'Error al crear producto: {message}', 'error')
                logger.error(f"Error al crear producto en API: {message}")
                
        except Exception as e:
            logger.error(f"Error creando producto desde DevOps: {e}")
            flash('Error interno al crear el producto', 'error')
        
        return redirect(url_for('devops.gestion_productos'))
    
    # GET request - mostrar productos
    try:
        if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
            flash('Servicio DevOps temporalmente no disponible. Configure las variables de entorno.', 'error')
            return render_template('devops/productos.html', productos=[], negocios=[])
        
        productos = devops_manager.get_productos()
        negocios = devops_manager.get_negocios()
        return render_template('devops/productos.html', productos=productos, negocios=negocios)
    except Exception as e:
        logger.error(f"Error cargando productos: {e}")
        flash('Error interno al cargar productos.', 'error')
        return render_template('devops/productos.html', productos=[], negocios=[])

# =================================================================
# GESTIÓN DE OFERTAS
# =================================================================

@devops_bp.route('/ofertas', methods=['GET', 'POST'])
@devops_login_required
def gestion_ofertas():
    """Gestión completa de ofertas - SOLO DATOS REALES"""
    
    # Manejar POST requests (crear oferta)
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
            
            # Verificar que el gestor esté disponible
            if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
                flash('Error: API no configurada. Verifique las variables de entorno.', 'error')
                return redirect(url_for('devops.gestion_ofertas'))
            
            # Crear oferta usando el gestor DevOps
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
                logger.info(f"Oferta creada desde DevOps: {titulo}")
            else:
                flash(f'Error al crear oferta: {message}', 'error')
                logger.error(f"Error al crear oferta en API: {message}")
                
        except Exception as e:
            logger.error(f"Error creando oferta desde DevOps: {e}")
            flash('Error interno al crear la oferta', 'error')
        
        return redirect(url_for('devops.gestion_ofertas'))
    
    # GET request - mostrar ofertas
    try:
        if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
            flash('Servicio DevOps temporalmente no disponible. Configure las variables de entorno.', 'error')
            return render_template('devops/ofertas.html', ofertas=[])
        
        ofertas = devops_manager.get_ofertas()
        return render_template('devops/ofertas.html', ofertas=ofertas)
    except Exception as e:
        logger.error(f"Error cargando ofertas: {e}")
        flash('Error interno al cargar ofertas.', 'error')
        return render_template('devops/ofertas.html', ofertas=[])

# =================================================================
# GESTIÓN DE PRECIOS
# =================================================================

@devops_bp.route('/precios', methods=['GET', 'POST'])
@devops_login_required
def gestion_precios():
    """Gestión completa de precios - SOLO DATOS REALES"""
    
    # Manejar POST requests (actualizar precio)
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
            
            # Verificar que el gestor esté disponible
            if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
                flash('Error: API no configurada. Verifique las variables de entorno.', 'error')
                return redirect(url_for('devops.gestion_precios'))
            
            # Actualizar precio usando el gestor DevOps
            precio_data = {
                'producto_id': int(producto_id),
                'nuevo_precio': precio_float,
                'motivo': motivo or 'Actualización desde DevOps'
            }
            
            success, message = devops_manager.update_item('precios', producto_id, precio_data)
            if success:
                flash(f'Precio actualizado exitosamente', 'success')
                logger.info(f"Precio actualizado desde DevOps: Producto {producto_id}")
            else:
                flash(f'Error al actualizar precio: {message}', 'error')
                logger.error(f"Error al actualizar precio en API: {message}")
                
        except Exception as e:
            logger.error(f"Error actualizando precio desde DevOps: {e}")
            flash('Error interno al actualizar el precio', 'error')
        
        return redirect(url_for('devops.gestion_precios'))
    
    # GET request - mostrar precios
    try:
        if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
            flash('Servicio DevOps temporalmente no disponible. Configure las variables de entorno.', 'error')
            return render_template('devops/precios.html', precios=[], productos=[])
        
        precios = devops_manager.get_items('precios')
        productos = devops_manager.get_productos()
        return render_template('devops/precios.html', precios=precios, productos=productos)
    except Exception as e:
        logger.error(f"Error cargando precios: {e}")
        flash('Error interno al cargar precios.', 'error')
        return render_template('devops/precios.html', precios=[], productos=[])

# =================================================================
# CONECTIVIDAD CON BELGRANO AHORRO
# =================================================================

@devops_bp.route('/conectar-belgrano')
@devops_login_required
def conectar_belgrano():
    """Verificar y establecer conexión con Belgrano Ahorro"""
    try:
        if not devops_manager:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'error',
                    'message': 'Gestor DevOps no disponible',
                    'data': {}
                }), 503
            else:
                flash('Gestor DevOps no disponible', 'error')
                return render_template('devops/status.html', 
                                     status='error', 
                                     message='Gestor DevOps no disponible',
                                     connectivity={})
        
        # Probar conectividad
        connectivity = devops_manager.test_connectivity()
        
        if connectivity['overall_status'] == 'success':
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'success',
                    'message': 'Conexión exitosa con Belgrano Ahorro',
                    'data': connectivity
                })
            else:
                flash('Conexión exitosa con Belgrano Ahorro', 'success')
                return render_template('devops/status.html', 
                                     status='success', 
                                     message='Conexión exitosa con Belgrano Ahorro',
                                     connectivity=connectivity)
        elif connectivity['overall_status'] == 'partial':
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'warning',
                    'message': 'Conexión parcial con Belgrano Ahorro',
                    'data': connectivity
                })
            else:
                flash('Conexión parcial con Belgrano Ahorro', 'warning')
                return render_template('devops/status.html', 
                                     status='warning', 
                                     message='Conexión parcial con Belgrano Ahorro',
                                     connectivity=connectivity)
        else:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'error',
                    'message': 'No se pudo conectar con Belgrano Ahorro',
                    'data': connectivity
                }), 503
            else:
                flash('No se pudo conectar con Belgrano Ahorro', 'error')
                return render_template('devops/status.html', 
                                     status='error', 
                                     message='No se pudo conectar con Belgrano Ahorro',
                                     connectivity=connectivity)
            
    except Exception as e:
        logger.error(f"Error verificando conexión con Belgrano Ahorro: {e}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'error',
                'message': f'Error interno: {str(e)}',
                'data': {}
            }), 500
        else:
            flash(f'Error interno: {str(e)}', 'error')
            return render_template('devops/status.html', 
                                 status='error', 
                                 message=f'Error interno: {str(e)}',
                                 connectivity={})

# =================================================================
# INFORMACIÓN DEL SISTEMA
# =================================================================

@devops_bp.route('/info')
@devops_login_required
def devops_info():
    """Información completa del sistema DevOps"""
    try:
        if not devops_manager:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'status': 'error',
                    'message': 'Gestor DevOps no disponible',
                    'data': {
                        'timestamp': datetime.now().isoformat(),
                        'fallback_mode': True,
                        'api_configured': False
                    }
                }), 503
            else:
                flash('Gestor DevOps no disponible', 'error')
                return render_template('devops/info.html', 
                                     status='error', 
                                     message='Gestor DevOps no disponible',
                                     system_status={
                                         'timestamp': datetime.now().isoformat(),
                                         'fallback_mode': True,
                                         'api_configured': False
                                     })
        
        system_status = devops_manager.get_system_status()
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'success',
                'message': 'Información del sistema DevOps',
                'data': system_status
            })
        else:
            flash('Información del sistema cargada correctamente', 'success')
            return render_template('devops/info.html', 
                                 status='success', 
                                 message='Información del sistema DevOps',
                                 system_status=system_status)
        
    except Exception as e:
        logger.error(f"Error obteniendo información del sistema: {e}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'status': 'error',
                'message': f'Error interno: {str(e)}',
                'data': {}
            }), 500
        else:
            flash(f'Error interno: {str(e)}', 'error')
            return render_template('devops/info.html', 
                                 status='error', 
                                 message=f'Error interno: {str(e)}',
                                 system_status={})

# =================================================================
# GESTIÓN DE SUCURSALES
# =================================================================

@devops_bp.route('/sucursales', methods=['GET', 'POST'])
@devops_login_required
def gestion_sucursales():
    """Gestión completa de sucursales - SOLO DATOS REALES"""
    
    # Manejar POST requests (crear sucursal)
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip()
            direccion = request.form.get('direccion', '').strip()
            telefono = request.form.get('telefono', '').strip()
            negocio_id = request.form.get('negocio_id', '').strip()
            
            if not all([nombre, direccion, negocio_id]):
                flash('Nombre, dirección y negocio son requeridos', 'error')
                return redirect(url_for('devops.gestion_sucursales'))
            
            # Verificar que el gestor esté disponible
            if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
                flash('Error: API no configurada. Verifique las variables de entorno.', 'error')
                return redirect(url_for('devops.gestion_sucursales'))
            
            # Crear sucursal usando el gestor DevOps
            sucursal_data = {
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'negocio_id': negocio_id,
                'activo': True
            }
            
            success, message = devops_manager.create_sucursal(sucursal_data)
            if success:
                flash(f'Sucursal creada exitosamente', 'success')
                logger.info(f"Sucursal creada desde DevOps: {nombre}")
            else:
                flash(f'Error al crear sucursal: {message}', 'error')
                logger.error(f"Error creando sucursal desde DevOps: {message}")
                
        except Exception as e:
            logger.error(f"Error creando sucursal desde DevOps: {e}")
            flash('Error interno al crear la sucursal', 'error')
        
        return redirect(url_for('devops.gestion_sucursales'))
    
    # GET request - mostrar sucursales
    try:
        if not devops_manager or getattr(devops_manager, 'fallback_mode', False):
            flash('Servicio DevOps temporalmente no disponible. Configure las variables de entorno.', 'error')
            return render_template('devops/sucursales.html', sucursales=[], negocios=[])
        
        sucursales = devops_manager.get_sucursales()
        negocios = devops_manager.get_negocios()
        return render_template('devops/sucursales.html', sucursales=sucursales, negocios=negocios)
    except Exception as e:
        logger.error(f"Error cargando sucursales: {e}")
        flash('Error interno al cargar sucursales.', 'error')
        return render_template('devops/sucursales.html', sucursales=[], negocios=[])
