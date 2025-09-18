#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación de Tickets - Sistema independiente para gestión de pedidos
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from functools import wraps

# Crear la instancia de Flask
app = Flask(__name__, template_folder='templates_tickets')
app.secret_key = 'belgrano_tickets_secret_2025'

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Registrar blueprint de DevOps (importación robusta)
try:
    # Intento directo si el cwd es la raíz del proyecto
    from devops_routes import devops_bp
    app.register_blueprint(devops_bp)
    print("✅ Blueprint de DevOps registrado en app_tickets (directo)")
except Exception as e:
    try:
        import sys
        project_root = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(project_root)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from devops_routes import devops_bp as devops_bp_root
        app.register_blueprint(devops_bp_root)
        print("✅ Blueprint de DevOps registrado en app_tickets (sys.path raíz)")
    except Exception as e2:
        print(f"⚠️ No se pudo registrar DevOps en app_tickets: {e2}")

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
# BASE DE DATOS
# =================================================================

# Usar ruta ABSOLUTA y configurable por entorno para la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('TICKETS_DB_PATH') or os.path.join(BASE_DIR, 'belgrano_tickets.db')

def crear_base_datos():
    """Crear base de datos de tickets"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabla usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(50),
                telefono VARCHAR(20),
                rol VARCHAR(20) DEFAULT 'cliente',
                activo BOOLEAN DEFAULT 1,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla tickets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido VARCHAR(50) UNIQUE NOT NULL,
                cliente VARCHAR(100) NOT NULL,
                productos TEXT NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                direccion TEXT,
                telefono VARCHAR(20),
                email VARCHAR(100),
                metodo_pago VARCHAR(50),
                notas TEXT,
                estado VARCHAR(20) DEFAULT 'pendiente',
                prioridad VARCHAR(20) DEFAULT 'normal',
                repartidor VARCHAR(50),
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creando base de datos: {e}")
        return False

def inicializar_usuarios():
    """Inicializar usuarios del sistema"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si ya existen usuarios
        cursor.execute('SELECT COUNT(*) FROM usuarios')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Crear usuario admin
            admin_password = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@belgranoahorro.com', admin_password, 'Administrador', 'admin', True))
            
            # Crear usuarios flota
            flota_usuarios = [
                ('repartidor1', 'repartidor1@belgranoahorro.com', 'Repartidor 1'),
                ('repartidor2', 'repartidor2@belgranoahorro.com', 'Repartidor 2'),
                ('repartidor3', 'repartidor3@belgranoahorro.com', 'Repartidor 3'),
                ('repartidor4', 'repartidor4@belgranoahorro.com', 'Repartidor 4'),
                ('repartidor5', 'repartidor5@belgranoahorro.com', 'Repartidor 5')
            ]
            
            for username, email, nombre in flota_usuarios:
                flota_password = generate_password_hash('flota123')
                cursor.execute('''
                    INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, email, flota_password, nombre, 'flota', True))
            
            conn.commit()
            print("✅ Usuarios del sistema inicializados")
        else:
            print(f"✅ Ya existen {count} usuarios en el sistema")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error inicializando usuarios: {e}")
        return False

def asegurar_usuarios_core():
    """Asegurar que existan/estén activos Admin y Flota base.
    Idempotente: crea si no existen, actualiza password si falta, activa si está inactivo.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cambios = 0

        # Admin
        cursor.execute('SELECT id, activo FROM usuarios WHERE email = ?', ('admin@belgranoahorro.com',))
        row = cursor.fetchone()
        if row is None:
            admin_password = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@belgranoahorro.com', admin_password, 'Administrador', 'admin', True))
            cambios += 1
        else:
            user_id, activo = row
            if not activo:
                cursor.execute('UPDATE usuarios SET activo = 1 WHERE id = ?', (user_id,))
                cambios += 1

        # Flota principal
        cursor.execute('SELECT id, activo FROM usuarios WHERE email = ?', ('repartidor1@belgranoahorro.com',))
        row = cursor.fetchone()
        if row is None:
            flota_password = generate_password_hash('flota123')
            cursor.execute('''
                INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('repartidor1', 'repartidor1@belgranoahorro.com', flota_password, 'Repartidor 1', 'flota', True))
            cambios += 1
        else:
            user_id, activo = row
            if not activo:
                cursor.execute('UPDATE usuarios SET activo = 1 WHERE id = ?', (user_id,))
                cambios += 1

        conn.commit()
        conn.close()
        if cambios:
            print(f"✅ Usuarios core asegurados/actualizados: {cambios}")
        else:
            print("✅ Usuarios core ya presentes y activos")
        return True
    except Exception as e:
        print(f"❌ Error asegurando usuarios core: {e}")
        return False

def guardar_ticket(ticket_data):
    """Guardar ticket en la base de datos"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (
                numero_pedido, cliente, productos, total, direccion, telefono,
                email, metodo_pago, notas, estado, prioridad, repartidor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket_data['numero_pedido'],
            ticket_data['cliente'],
            json.dumps(ticket_data['productos']),
            ticket_data['total'],
            ticket_data.get('direccion', ''),
            ticket_data.get('telefono', ''),
            ticket_data.get('email', ''),
            ticket_data.get('metodo_pago', ''),
            ticket_data.get('notas', ''),
            'pendiente',
            'normal',
            'Repartidor1'  # Asignación simple
        ))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticket_id
    except Exception as e:
        print(f"Error guardando ticket: {e}")
        return None

def obtener_todos_los_tickets():
    """Obtener todos los tickets"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, numero_pedido, cliente, productos, total, direccion,
                   telefono, email, metodo_pago, notas, estado, prioridad,
                   repartidor, fecha_creacion, fecha_actualizacion
            FROM tickets
            ORDER BY fecha_creacion DESC
        ''')
        
        tickets = []
        for row in cursor.fetchall():
            tickets.append({
                'id': row[0],
                'numero_pedido': row[1],
                'cliente': row[2],
                'productos': json.loads(row[3]) if row[3] else [],
                'total': row[4],
                'direccion': row[5],
                'telefono': row[6],
                'email': row[7],
                'metodo_pago': row[8],
                'notas': row[9],
                'estado': row[10],
                'prioridad': row[11],
                'repartidor': row[12],
                'fecha_creacion': row[13],
                'fecha_actualizacion': row[14]
            })
        
        conn.close()
        return tickets
    except Exception as e:
        print(f"Error obteniendo tickets: {e}")
        return []

def obtener_usuario_por_email(email):
    """Obtener usuario por email"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, password, nombre, apellido, telefono, rol, activo
            FROM usuarios
            WHERE email = ?
        ''', (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'password': row[3],
                'nombre': row[4],
                'apellido': row[5],
                'telefono': row[6],
                'rol': row[7],
                'activo': bool(row[8])
            }
        return None
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None

def contar_tickets():
    """Contar total de tickets"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tickets')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    except Exception as e:
        print(f"Error contando tickets: {e}")
        return 0

# =================================================================
# FLASK-LOGIN
# =================================================================

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, password, nombre, rol, activo
            FROM usuarios
            WHERE id = ?
        ''', (int(user_id),))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password=row[3],
                nombre=row[4],
                role=row[5],
                activo=bool(row[6])
            )
    except Exception as e:
        print(f"Error cargando usuario: {e}")
    return None

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return jsonify({'error': 'Acceso denegado'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =================================================================
# RUTAS DE LA API
# =================================================================

@app.route('/api/tickets', methods=['POST'])
def api_crear_ticket():
    """Endpoint público para recibir tickets desde Belgrano Ahorro"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        required_fields = ['cliente', 'productos', 'total']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Validar tipos de datos
        if not isinstance(data['cliente'], str):
            return jsonify({'error': 'cliente debe ser string'}), 400
        
        if not isinstance(data['productos'], list):
            return jsonify({'error': 'productos debe ser lista'}), 400
        
        if not isinstance(data['total'], (int, float)):
            return jsonify({'error': 'total debe ser número'}), 400
        
        # Generar número de pedido si no viene
        if 'numero_pedido' not in data:
            import secrets
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_suffix = secrets.token_hex(3).upper()
            data['numero_pedido'] = f"TICK-{timestamp}-{random_suffix}"
        
        # Guardar ticket
        ticket_id = guardar_ticket(data)
        
        if ticket_id:
            print(f"✅ Ticket recibido y guardado: {data['numero_pedido']}")
            print(f"   Cliente: {data['cliente']}")
            print(f"   Total: ${data['total']}")
            print(f"   Productos: {len(data['productos'])} items")
            
            return jsonify({'msg': 'ticket registrado', 'ticket_id': ticket_id}), 201
        else:
            return jsonify({'error': 'Error guardando ticket'}), 500
            
    except Exception as e:
        print(f"Error en API crear ticket: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/tickets', methods=['GET'])
@login_required
@role_required('admin')
def api_obtener_tickets():
    """Obtener todos los tickets (solo admin)"""
    try:
        tickets = obtener_todos_los_tickets()
        return jsonify({'tickets': tickets}), 200
    except Exception as e:
        return jsonify({'error': 'Error obteniendo tickets'}), 500

# =================================================================
# RUTAS WEB
# =================================================================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Log del intento de login
        print(f"Intento de login: {email}")
        
        if not email or not password:
            print(f"Login fallido - Campos vacíos: {email}")
            return render_template('login.html', error='Por favor complete todos los campos')
        
        try:
            usuario = obtener_usuario_por_email(email)
            
            if not usuario:
                print(f"Login fallido - Usuario no encontrado: {email}")
                return render_template('login.html', error='Usuario no encontrado o inactivo')
            
            if not usuario['activo']:
                print(f"Login fallido - Usuario inactivo: {email}")
                return render_template('login.html', error='Usuario no encontrado o inactivo')
            
            if not check_password_hash(usuario['password'], password):
                print(f"Login fallido - Contraseña incorrecta: {email}")
                return render_template('login.html', error='Email o contraseña incorrectos')
            
            # Login exitoso
            user = User(
                id=usuario['id'],
                username=usuario['username'],
                email=usuario['email'],
                password=usuario['password'],
                nombre=usuario['nombre'],
                role=usuario['rol'],
                activo=usuario['activo']
            )
            
            login_user(user)
            print(f"Login exitoso: {email} ({usuario['rol']})")
            return redirect(url_for('tickets'))
            
        except Exception as e:
            print(f"Error en login para {email}: {e}")
            return render_template('login.html', error='Error interno del servidor')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/tickets')
@login_required
def tickets():
    """Panel principal de tickets"""
    tickets_list = obtener_todos_los_tickets()
    return render_template('tickets.html', tickets=tickets_list)

@app.route('/health')
def health_check():
    """Health check para Render.com"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tickets')
        total_tickets = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM usuarios')
        total_usuarios = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'Belgrano Tickets',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'total_tickets': total_tickets,
            'total_usuarios': total_usuarios,
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# =================================================================
# INICIALIZACIÓN
# =================================================================

def inicializar_aplicacion():
    """Inicializar la aplicación"""
    print("🚀 Iniciando Belgrano Tickets...")
    
    # Crear base de datos
    if crear_base_datos():
        print("✅ Base de datos creada/verificada")
    else:
        print("❌ Error creando base de datos")
        return False
    
    # Inicializar usuarios
    if inicializar_usuarios():
        print("✅ Usuarios inicializados")
    else:
        print("❌ Error inicializando usuarios")
        return False
    
    print("✅ Aplicación inicializada correctamente")
    print("📱 URLs disponibles:")
    print("   • Login: http://localhost:5001")
    print("   • Tickets: http://localhost:5001/tickets")
    print("   • API: http://localhost:5001/api/tickets")
    print()
    print("🔐 Credenciales:")
    print("   • Admin: admin@belgranoahorro.com / admin123")
    print("   • Flota: repartidor1@belgranoahorro.com / flota123")
    
    return True

# Inicialización automática para deploy
def init_deploy():
    """Inicialización automática para deploy"""
    try:
        # Verificar si la base de datos existe
        if not os.path.exists(DB_PATH):
            print("Inicializando base de datos para deploy...")
            crear_base_datos()
            inicializar_usuarios()
            asegurar_usuarios_core()
            print("Inicializacion de deploy completada")
        else:
            # Verificar que los usuarios existan
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM usuarios')
            user_count = cursor.fetchone()[0]
            conn.close()
            
            if user_count == 0:
                print("Base de datos existe pero sin usuarios, inicializando...")
                inicializar_usuarios()
                asegurar_usuarios_core()
            else:
                print(f"Base de datos ya existe con {user_count} usuarios")
                asegurar_usuarios_core()
    except Exception as e:
        print(f"Error en inicializacion de deploy: {e}")

# Función de verificación automática de credenciales
def verificar_credenciales():
    """Verificar que las credenciales críticas existan"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar usuario admin
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE email = ? AND rol = ?', 
                      ('admin@belgranoahorro.com', 'admin'))
        admin_count = cursor.fetchone()[0]
        
        # Verificar usuarios flota
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE rol = ?', ('flota',))
        flota_count = cursor.fetchone()[0]
        
        conn.close()
        
        if admin_count == 0 or flota_count == 0:
            print("⚠️ Usuarios core incompletos, asegurando...")
            asegurar_usuarios_core()
        
        print(f"✅ Credenciales verificadas: admin={admin_count}, flota={flota_count}")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando credenciales: {e}")
        return False

# Ejecutar inicialización automática
init_deploy()

# Verificar credenciales después de la inicialización
verificar_credenciales()

if __name__ == "__main__":
    if inicializar_aplicacion():
        port = int(os.environ.get('PORT', 5001))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        print(f"🌐 Servidor iniciado en puerto {port}")
        app.run(debug=debug, host='0.0.0.0', port=port)
    else:
        print("❌ Error inicializando aplicación")
