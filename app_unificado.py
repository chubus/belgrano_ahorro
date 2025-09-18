#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Unificada: Belgrano Ahorro + Belgrano Tickets
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_socketio import SocketIO
from functools import wraps
import uuid
import secrets

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la instancia de Flask
app = Flask(__name__, template_folder="templates", static_folder="static")

# Cargar configuración centralizada
try:
    from belgrano_tickets.config import get_config
    AppConfigClass = get_config()
    app.config.from_object(AppConfigClass)
    # Asegurar SECRET_KEY configurado
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(32).hex()
    logger.info(f"Config cargada: env={app.config.get('FLASK_ENV')}")
except Exception as e:
    logger.warning(f"No se pudo cargar configuración centralizada: {e}")
    # Fallback mínimo
    app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32).hex())

# Importar base de datos
try:
    import db as database
    print("✅ Módulo db importado correctamente")
except Exception as e:
    print(f"❌ Error importando db: {e}")
    raise

# Configurar Flask-Login y SocketIO
login_manager = LoginManager(app)

# Configurar SocketIO solo si no estamos en producción o si es necesario
try:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    SOCKETIO_AVAILABLE = True
except Exception as e:
    print(f"⚠️ SocketIO no disponible: {e}")
    socketio = None
    SOCKETIO_AVAILABLE = False

# =================================================================
# MODELOS
# =================================================================

class User(UserMixin):
    def __init__(self, id, username, email, password, nombre, role='cliente', activo=True):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.nombre = nombre
        self.role = role
        self.activo = activo

# =================================================================
# FUNCIONES AUXILIARES
# =================================================================

def cargar_productos():
    try:
        with open('productos.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('productos', [])
    except Exception as e:
        print(f"Error cargando productos: {e}")
        return []

def obtener_producto_por_id(producto_id):
    productos = cargar_productos()
    for producto in productos:
        if str(producto['id']) == str(producto_id):
            return producto
    return None

def generar_numero_pedido():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = secrets.token_hex(3).upper()
    return f"PED-{timestamp}-{random_suffix}"

def usuario_logueado():
    return 'usuario_id' in session

def obtener_usuario_actual():
    if usuario_logueado():
        return database.obtener_usuario_por_id(session['usuario_id'])
    return None

# =================================================================
# INICIALIZACIÓN DE USUARIOS
# =================================================================

def inicializar_usuarios_sistema():
    try:
        usuarios_existentes = database.contar_usuarios()
        
        if usuarios_existentes == 0:
            print("🔧 Inicializando usuarios del sistema...")
            
            # Crear usuario admin
            admin_data = {
                'username': 'admin',
                'email': 'admin@belgranoahorro.com',
                'password': generate_password_hash('admin123'),
                'nombre': 'Administrador Principal',
                'apellido': '',
                'telefono': '',
                'rol': 'admin',
                'activo': True
            }
            database.crear_usuario(**admin_data)
            print("✅ Usuario admin creado: admin@belgranoahorro.com / admin123")
            
            # Crear usuarios flota
            flota_usuarios = [
                ('repartidor1', 'repartidor1@belgranoahorro.com', 'Repartidor 1'),
                ('repartidor2', 'repartidor2@belgranoahorro.com', 'Repartidor 2'),
                ('repartidor3', 'repartidor3@belgranoahorro.com', 'Repartidor 3'),
                ('repartidor4', 'repartidor4@belgranoahorro.com', 'Repartidor 4'),
                ('repartidor5', 'repartidor5@belgranoahorro.com', 'Repartidor 5')
            ]
            
            for username, email, nombre in flota_usuarios:
                flota_data = {
                    'username': username,
                    'email': email,
                    'password': generate_password_hash('flota123'),
                    'nombre': nombre,
                    'apellido': '',
                    'telefono': '',
                    'rol': 'flota',
                    'activo': True
                }
                database.crear_usuario(**flota_data)
                print(f"✅ Usuario flota creado: {email} / flota123")
            
            print("🎉 Usuarios del sistema inicializados")
        else:
            print(f"✅ Ya existen {usuarios_existentes} usuarios en el sistema")
            
    except Exception as e:
        print(f"❌ Error inicializando usuarios del sistema: {e}")

# =================================================================
# FLASK-LOGIN
# =================================================================

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = database.obtener_usuario_por_id(int(user_id))
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                nombre=user_data['nombre'],
                role=user_data.get('rol', 'cliente'),
                activo=user_data.get('activo', True)
            )
    except Exception as e:
        print(f"Error cargando usuario: {e}")
    return None

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =================================================================
# RUTAS PRINCIPALES - BELGRANO AHORRO
# =================================================================

@app.route('/')
def index():
    productos = cargar_productos()
    productos_destacados = productos[:8]
    
    # Agrupar productos por negocio
    productos_por_negocio = {}
    for producto in productos:
        negocio = producto.get('negocio', 'belgrano_ahorro')
        if negocio not in productos_por_negocio:
            productos_por_negocio[negocio] = []
        productos_por_negocio[negocio].append(producto)
    
    # Cargar categorías y negocios desde productos.json
    categorias = {}
    negocios = {}
    try:
        with open('productos.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            categorias = data.get('categorias', {})
            negocios = data.get('negocios', {})
    except Exception as e:
        logger.error(f"Error cargando categorías y negocios: {e}")
        categorias = {}
        negocios = {}
    
    # Log para verificar en Render
    logger.info(f"Endpoint / accedido - Productos cargados: {len(productos)}")
    logger.info(f"Productos destacados: {len(productos_destacados)}")
    logger.info(f"Primeros 3 productos destacados: {[p.get('nombre', 'Sin nombre') for p in productos_destacados[:3]]}")
    logger.info(f"Productos por negocio: {list(productos_por_negocio.keys())}")
    logger.info(f"Categorías cargadas: {len(categorias)}")
    logger.info(f"Negocios cargados: {len(negocios)}")
    
    return render_template('index.html', productos=productos_destacados, productos_por_negocio=productos_por_negocio, categorias=categorias, negocios=negocios)

@app.route('/productos')
def productos():
    productos_lista = cargar_productos()
    busqueda = request.args.get('busqueda', '')
    
    if busqueda:
        busqueda = busqueda.lower()
        productos_lista = [p for p in productos_lista if busqueda in p.get('nombre', '').lower()]
    
    return render_template('productos.html', productos=productos_lista, busqueda=busqueda)

@app.route('/carrito')
def carrito():
    if not session.get('carrito'):
        session['carrito'] = {}
    
    carrito_items = []
    total = 0
    
    for producto_id, cantidad in session['carrito'].items():
        producto = obtener_producto_por_id(producto_id)
        if producto:
            subtotal = producto['precio'] * cantidad
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('carrito.html', carrito_items=carrito_items, total=total)

@app.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    if not session.get('carrito'):
        session['carrito'] = {}
    
    cantidad = int(request.form.get('cantidad', 1))
    
    if str(producto_id) in session['carrito']:
        session['carrito'][str(producto_id)] += cantidad
    else:
        session['carrito'][str(producto_id)] = cantidad
    
    session.modified = True
    flash('Producto agregado al carrito', 'success')
    return redirect(url_for('carrito'))

@app.route('/checkout')
def checkout():
    if not usuario_logueado():
        flash('Debes iniciar sesión para realizar una compra', 'warning')
        return redirect(url_for('login'))
    
    if not session.get('carrito'):
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito'))
    
    carrito_items = []
    total = 0
    
    for producto_id, cantidad in session['carrito'].items():
        producto = obtener_producto_por_id(producto_id)
        if producto:
            subtotal = producto['precio'] * cantidad
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('checkout.html', carrito_items=carrito_items, total=total)

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    if not usuario_logueado():
        flash('Debes iniciar sesión para realizar una compra', 'warning')
        return redirect(url_for('login'))
    
    if not session.get('carrito'):
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito'))
    
    metodo_pago = request.form.get('metodo_pago')
    direccion = request.form.get('direccion')
    notas = request.form.get('notas')
    
    if not direccion:
        flash('Por favor ingresa una dirección de entrega', 'danger')
        return redirect(url_for('checkout'))
    
    numero_pedido = generar_numero_pedido()
    usuario = obtener_usuario_actual()
    
    carrito_items = []
    total = 0
    
    for producto_id, cantidad in session['carrito'].items():
        producto = obtener_producto_por_id(producto_id)
        if producto:
            subtotal = producto['precio'] * cantidad
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    # Guardar pedido
    pedido_id = database.guardar_pedido(
        usuario_id=usuario['id'],
        numero_pedido=numero_pedido,
        total=total,
        metodo_pago=metodo_pago,
        direccion_entrega=direccion,
        notas=notas
    )
    
    if pedido_id:
        # Guardar items del pedido
        items_db = []
        for item in carrito_items:
            items_db.append({
                'producto_id': item['producto']['id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['producto']['precio'],
                'subtotal': item['subtotal']
            })
        
        database.guardar_items_pedido(pedido_id, items_db)
        
        # Enviar pedido a la API de tickets
        enviar_pedido_a_tickets(numero_pedido, usuario, carrito_items, total, 
                               metodo_pago, direccion, notas)
    
    session.pop('carrito', None)
    
    if pedido_id:
        flash(f'¡Pedido confirmado! Número: {numero_pedido}', 'success')
        return redirect(url_for('confirmacion_pedido', numero_pedido=numero_pedido))
    else:
        flash('Error al procesar el pedido. Intenta nuevamente.', 'danger')
        return redirect(url_for('checkout'))

def enviar_pedido_a_tickets(numero_pedido, usuario, carrito_items, total, 
                           metodo_pago, direccion, notas):
    """Enviar pedido a la API de tickets externa"""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        # Config de ticketera desde app.config
        api_url = (
            app.config.get('TICKETS_API_URL')
            or os.environ.get('TICKETS_API_URL')
            or os.environ.get('TICKETERA_URL')
        )
        api_key = (
            app.config.get('TICKETS_API_KEY')
            or os.environ.get('TICKETS_API_KEY')
            or os.environ.get('TICKETERA_API_KEY')
        )
        api_user = (
            app.config.get('TICKETS_API_USERNAME')
            or os.environ.get('TICKETS_API_USERNAME')
            or os.environ.get('TICKETERA_USER')
        )
        api_pass = (
            app.config.get('TICKETS_API_PASSWORD')
            or os.environ.get('TICKETS_API_PASSWORD')
            or os.environ.get('TICKETERA_PASSWORD')
        )
        
        # Preparar datos del cliente
        nombre_completo = usuario.get('nombre', 'Cliente')
        if usuario.get('apellido'):
            nombre_completo = f"{usuario['nombre']} {usuario['apellido']}"
        
        # Preparar lista de productos
        productos = []
        for item in carrito_items:
            productos.append(item['producto']['nombre'])
        
        # Datos para enviar a la API
        ticket_data = {
            "cliente": nombre_completo,
            "productos": productos,
            "total": total,
            "numero_pedido": numero_pedido,
            "direccion": direccion,
            "telefono": usuario.get('telefono', ''),
            "email": usuario['email'],
            "metodo_pago": metodo_pago,
            "notas": notas or 'Sin indicaciones especiales'
        }
        
        # Validar URL configurada
        if not api_url:
            logger.warning("No se configuró TICKETS_API_URL/TICKETERA_URL; se omite envío a ticketera")
            return

        headers = {'Content-Type': 'application/json'}
        auth = None
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        elif api_user and api_pass:
            auth = HTTPBasicAuth(api_user, api_pass)
        
        # Enviar request POST
        response = requests.post(
            api_url,
            json=ticket_data,
            headers=headers,
            auth=auth,
            timeout=app.config.get('API_TIMEOUT_SECS', 10)
        )
        
        if response.status_code == 201:
            print(f"✅ Pedido enviado exitosamente a tickets: {numero_pedido}")
            print(f"   Cliente: {nombre_completo}")
            print(f"   Total: ${total}")
            print(f"   Productos: {len(productos)} items")
        else:
            print(f"⚠️ Error enviando pedido a tickets: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error de conexión enviando pedido a tickets: {e}")
    except Exception as e:
        print(f"⚠️ Error inesperado enviando pedido a tickets: {e}")

@app.route('/confirmacion/<numero_pedido>')
def confirmacion_pedido(numero_pedido):
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver esta página', 'warning')
        return redirect(url_for('login'))
    
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    hora_actual = datetime.now().strftime("%H:%M")
    
    return render_template("confirmacion.html", 
                         numero_pedido=numero_pedido,
                         fecha=fecha_actual,
                         hora=hora_actual)

# =================================================================
# RUTAS DE AUTENTICACIÓN
# =================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email and password:
            usuario = database.verificar_usuario(email, password)
            if usuario:
                session['usuario_id'] = usuario['id']
                flash(f'¡Bienvenido, {usuario["nombre"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Email o contraseña incorrectos', 'danger')
        else:
            flash('Por favor completa todos los campos', 'warning')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        telefono = request.form.get('telefono')
        
        if not all([username, email, password, confirm_password, nombre]):
            flash('Por favor completa todos los campos obligatorios', 'warning')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'danger')
            return render_template('register.html')
        
        if database.verificar_email_existe(email):
            flash('El email ya está registrado', 'danger')
            return render_template('register.html')
        
        try:
            database.crear_usuario(
                username=username,
                email=email,
                password=password,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                rol='cliente'
            )
            flash('¡Registro exitoso! Ya puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error en el registro: {e}', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

# =================================================================
# RUTAS DE LA TICKETERA
# =================================================================

@app.route('/ticketera')
def ticketera_home():
    if not current_user.is_authenticated:
        return redirect(url_for('ticketera_login'))
    
    if current_user.role == 'admin':
        return redirect(url_for('ticketera_admin'))
    elif current_user.role == 'flota':
        return redirect(url_for('ticketera_flota'))
    else:
        return redirect(url_for('index'))

@app.route('/ticketera/login', methods=['GET', 'POST'])
def ticketera_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Por favor complete todos los campos', 'warning')
            return render_template('ticketera/login.html')
        
        usuario = database.obtener_usuario_por_email(email)
        
        if usuario:
            if not usuario.get('activo', True):
                flash('Usuario inactivo. Contacte al administrador.', 'danger')
                return render_template('ticketera/login.html')
            
            # Verificar password usando werkzeug
            from werkzeug.security import check_password_hash
            if check_password_hash(usuario['password'], password):
                user = User(
                    id=usuario['id'],
                    username=usuario['username'],
                    email=usuario['email'],
                    password=usuario['password'],
                    nombre=usuario['nombre'],
                    role=usuario.get('rol', 'cliente'),
                    activo=usuario.get('activo', True)
                )
                
                login_user(user)
                flash(f'Bienvenido, {usuario["nombre"]}!', 'success')
                return redirect(url_for('ticketera_home'))
            else:
                flash('Email o contraseña incorrectos', 'danger')
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('ticketera/login.html')

@app.route('/ticketera/admin')
@login_required
@role_required('admin')
def ticketera_admin():
    tickets = database.obtener_todos_los_tickets()
    return render_template('ticketera/admin_panel.html', tickets=tickets)

@app.route('/ticketera/flota')
@login_required
@role_required('flota')
def ticketera_flota():
    repartidor = f"Repartidor{current_user.id % 5 + 1}"
    tickets = database.obtener_tickets_por_repartidor(repartidor)
    return render_template('ticketera/flota_panel.html', tickets=tickets, repartidor=repartidor)

@app.route('/ticketera/gestion_flota')
@login_required
@role_required('admin')
def ticketera_gestion_flota():
    """Panel de gestión de flota para admin"""
    # Obtener todos los usuarios con rol flota
    try:
        usuarios_flota = database.obtener_usuarios_por_rol('flota')
    except Exception:
        usuarios_flota = []
    
    # Repartidores lógicos (para asignación actual)
    repartidores = ['Repartidor1', 'Repartidor2', 'Repartidor3', 'Repartidor4', 'Repartidor5']
    
    # Obtener estadísticas por repartidor
    stats_repartidores = {}
    for rep in repartidores:
        try:
            tickets_rep = database.obtener_tickets_por_repartidor(rep)
        except Exception:
            tickets_rep = []
        stats_repartidores[rep] = {
            'total': len(tickets_rep),
            'pendientes': len([t for t in tickets_rep if t.get('estado') == 'pendiente']),
            'en_camino': len([t for t in tickets_rep if t.get('estado') in ('en_camino', 'en-camino', 'en_proceso')]),
            'entregados': len([t for t in tickets_rep if t.get('estado') in ('entregado', 'completado')])
        }
    
    # Tickets con repartidor asignado
    try:
        tickets_asignados = database.obtener_tickets_asignados()
    except Exception:
        # Fallback: filtrar manualmente si no existe helper
        try:
            todos = database.obtener_todos_los_tickets()
            tickets_asignados = [t for t in todos if t.get('repartidor')]
        except Exception:
            tickets_asignados = []
    
    return render_template(
        'ticketera/gestion_flota.html',
        repartidores=repartidores,
        usuarios_flota=usuarios_flota,
        tickets_asignados=tickets_asignados,
        stats_repartidores=stats_repartidores
    )

@app.route('/ticketera/registro')
@login_required
@role_required('admin')
def ticketera_registro():
    """Panel de registro de tickets (historial)"""
    tickets_registro = database.obtener_tickets_registro()
    return render_template('ticketera/registro_tickets.html', tickets_registro=tickets_registro)

# =================================================================
# RUTAS DE API
# =================================================================

@app.route('/api/tickets/<int:ticket_id>/actualizar-estado', methods=['POST'])
@login_required
@role_required('admin')
def api_actualizar_estado_ticket(ticket_id):
    """Actualizar estado de un ticket"""
    try:
        data = request.get_json()
        estado = data.get('estado')
        estado_envio = data.get('estado_envio')
        repartidor = data.get('repartidor')
        prioridad = data.get('prioridad')
        
        success = database.actualizar_estado_ticket(
            ticket_id, estado, estado_envio, repartidor, prioridad
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Estado actualizado correctamente'})
        else:
            return jsonify({'success': False, 'error': 'Error actualizando estado'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>/preparar', methods=['POST'])
@login_required
@role_required('admin')
def api_preparar_ticket(ticket_id):
    """Preparar un ticket (asignar repartidor y prioridad)"""
    try:
        data = request.get_json()
        repartidor = data.get('repartidor')
        prioridad = data.get('prioridad', 'normal')
        
        success = database.actualizar_estado_ticket(
            ticket_id, 
            estado='en-preparacion',
            estado_envio='en-preparacion',
            repartidor=repartidor,
            prioridad=prioridad
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Ticket preparado correctamente'})
        else:
            return jsonify({'success': False, 'error': 'Error preparando ticket'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>/mover-registro', methods=['POST'])
@login_required
@role_required('admin')
def api_mover_a_registro(ticket_id):
    """Mover un ticket al registro"""
    try:
        success = database.mover_ticket_a_registro(ticket_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Ticket movido al registro correctamente'})
        else:
            return jsonify({'success': False, 'error': 'Error moviendo ticket al registro'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    try:
        # Verificar conexión básica a la base de datos
        try:
            usuarios = database.obtener_todos_los_usuarios()
            total_usuarios = len(usuarios) if usuarios else 0
        except Exception:
            total_usuarios = 0
            
        try:
            tickets = database.obtener_todos_los_tickets()
            total_tickets = len(tickets) if tickets else 0
        except Exception:
            total_tickets = 0
        
        return jsonify({
            'status': 'healthy',
            'service': 'Belgrano Ahorro Unificado',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'total_usuarios': total_usuarios,
            'total_tickets': total_tickets,
            'version': '2.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/healthz')
def healthz():
    """Health check endpoint para Render"""
    return "ok", 200

@app.route('/debug/credenciales')
def debug_credenciales():
    try:
        # Deshabilitar en producción
        if app.config.get('FLASK_ENV') == 'production':
            return jsonify({'status': 'forbidden'}), 403
        usuarios = database.obtener_todos_los_usuarios()
        credenciales = []
        
        for usuario in usuarios:
            credenciales.append({
                'id': usuario['id'],
                'username': usuario['username'],
                'email': usuario['email'],
                'nombre': usuario['nombre'],
                'rol': usuario.get('rol', 'cliente'),
                'activo': usuario.get('activo', True),
                'password_hash': usuario['password'][:50] + '...' if usuario['password'] else 'None'
            })
        
        return jsonify({
            'status': 'success',
            'total_usuarios': len(usuarios),
            'usuarios': credenciales,
            # No exponer credenciales por defecto en producción
            'credenciales_demo': (
                {
                    'admin': {'email': 'admin@belgranoahorro.com', 'password': 'admin123'},
                    'flota': {'email': 'repartidor1@belgranoahorro.com', 'password': 'flota123'}
                } if app.config.get('FLASK_ENV') != 'production' else {}
            )
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/debug/crear-usuarios')
def debug_crear_usuarios():
    """Endpoint temporal para crear usuarios si no existen"""
    try:
        if app.config.get('FLASK_ENV') == 'production':
            return jsonify({'status': 'forbidden'}), 403
            
        # Forzar creación de usuarios
        inicializar_usuarios_sistema()
        
        usuarios = database.obtener_todos_los_usuarios()
        return jsonify({
            'status': 'success',
            'message': 'Usuarios inicializados',
            'total_usuarios': len(usuarios),
            'credenciales': {
                'admin': 'admin@belgranoahorro.com / admin123',
                'flota': 'repartidor1@belgranoahorro.com / flota123'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# =================================================================
# INICIALIZACIÓN
# =================================================================

def inicializar_aplicacion():
    """Inicializar la aplicación y crear tablas necesarias"""
    print("🚀 Iniciando Belgrano Ahorro Unificado...")
    
    # Crear tablas si no existen
    try:
        database.crear_tabla_tickets()
        print("✅ Tabla de tickets verificada/creada")
    except Exception as e:
        print(f"⚠️ Error con tabla de tickets: {e}")
    
    # Inicializar usuarios del sistema
    try:
        inicializar_usuarios_sistema()
        print("✅ Usuarios del sistema inicializados")
    except Exception as e:
        print(f"⚠️ Error inicializando usuarios: {e}")
        print("   Puedes usar /debug/crear-usuarios para forzar la creación")
    
    print("✅ Aplicación inicializada correctamente")
    print("📱 URLs disponibles:")
    print("   • Belgrano Ahorro: http://localhost:5000")
    print("   • Ticketera: http://localhost:5000/ticketera")
    print("   • Debug usuarios: http://localhost:5000/debug/credenciales")
    print("   • Crear usuarios: http://localhost:5000/debug/crear-usuarios")
    print()
    print("🔐 Credenciales Ticketera:")
    print("   • Admin: admin@belgranoahorro.com / admin123")
    print("   • Flota: repartidor1@belgranoahorro.com / flota123")

if __name__ == "__main__":
    inicializar_aplicacion()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Servidor iniciado en puerto {port}")
    
    # Usar SocketIO si está disponible, sino usar Flask normal
    if SOCKETIO_AVAILABLE and socketio:
        socketio.run(app, debug=debug, host='0.0.0.0', port=port)
    else:
        app.run(debug=debug, host='0.0.0.0', port=port)
