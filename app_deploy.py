#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación de Deploy - Sistema de Tickets para Belgrano Ahorro
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from functools import wraps
import hmac
import binascii
import hashlib

# Crear la instancia de Flask
app = Flask(__name__, template_folder='templates_tickets')
# Secret key y cookies configurables por entorno
app.secret_key = os.environ.get('SECRET_KEY', 'belgrano_tickets_secret_2025')
app.config.update(
    SESSION_COOKIE_SAMESITE=os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax'),
    SESSION_COOKIE_SECURE=os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true',
    REMEMBER_COOKIE_SECURE=os.environ.get('REMEMBER_COOKIE_SECURE', 'true').lower() == 'true',
)

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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

def crear_base_datos():
    """Crear base de datos de tickets"""
    try:
        conn = sqlite3.connect('belgrano_tickets.db')
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
        conn = sqlite3.connect('belgrano_tickets.db')
        cursor = conn.cursor()
        
        # Verificar si ya existen usuarios
        cursor.execute('SELECT COUNT(*) FROM usuarios')
        count = cursor.fetchone()[0]
        
        # En producción, siempre asegurar que existan los usuarios básicos
        force_init = os.environ.get('FORCE_USER_INIT', 'false').lower() == 'true'
        
        if count == 0 or force_init:
            print(f"🔄 Inicializando usuarios (count: {count}, force: {force_init})")
            
            # Credenciales admin por entorno (con defaults)
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@belgranoahorro.com')
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_plain_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_password = generate_password_hash(admin_plain_password)
            
            # Verificar si admin ya existe
            cursor.execute('SELECT id FROM usuarios WHERE email = ?', (admin_email,))
            admin_exists = cursor.fetchone()
            
            if admin_exists:
                # Actualizar admin existente
                cursor.execute('''
                    UPDATE usuarios SET username = ?, password = ?, nombre = ?, rol = 'admin', activo = 1
                    WHERE email = ?
                ''', (admin_username, admin_password, 'Administrador', admin_email))
                print(f"✅ Admin actualizado: {admin_email}")
            else:
                # Crear admin nuevo
                cursor.execute('''
                    INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (admin_username, admin_email, admin_password, 'Administrador', 'admin', True))
                print(f"✅ Admin creado: {admin_email}")
            
            # Crear/actualizar usuarios flota
            flota_usuarios = [
                ('repartidor1', 'repartidor1@belgranoahorro.com', 'Repartidor 1'),
                ('repartidor2', 'repartidor2@belgranoahorro.com', 'Repartidor 2'),
                ('repartidor3', 'repartidor3@belgranoahorro.com', 'Repartidor 3'),
                ('repartidor4', 'repartidor4@belgranoahorro.com', 'Repartidor 4'),
                ('repartidor5', 'repartidor5@belgranoahorro.com', 'Repartidor 5')
            ]
            
            for username, email, nombre in flota_usuarios:
                flota_password = generate_password_hash('flota123')
                
                # Verificar si usuario flota ya existe
                cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
                flota_exists = cursor.fetchone()
                
                if flota_exists:
                    # Actualizar usuario flota existente
                    cursor.execute('''
                        UPDATE usuarios SET username = ?, password = ?, nombre = ?, rol = 'flota', activo = 1
                        WHERE email = ?
                    ''', (username, flota_password, nombre, email))
                    print(f"✅ Flota actualizado: {email}")
                else:
                    # Crear usuario flota nuevo
                    cursor.execute('''
                        INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (username, email, flota_password, nombre, 'flota', True))
                    print(f"✅ Flota creado: {email}")
            
            conn.commit()
            print("✅ Usuarios del sistema inicializados/actualizados")
        else:
            print(f"✅ Ya existen {count} usuarios en el sistema")
        
        # Verificar usuarios finales
        cursor.execute('SELECT email, rol, activo FROM usuarios')
        final_users = cursor.fetchall()
        print(f"📋 Usuarios finales en DB: {final_users}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error inicializando usuarios: {e}")
        return False
    
def resetear_admin_si_solicitado():
    """Resetear credenciales del admin si ADMIN_RESET=1 en entorno"""
    try:
        if os.environ.get('ADMIN_RESET', '0') != '1':
            return True
        conn = sqlite3.connect('belgrano_tickets.db')
        cursor = conn.cursor()
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@belgranoahorro.com')
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_plain_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_password = generate_password_hash(admin_plain_password)
        cursor.execute('SELECT id FROM usuarios WHERE email = ?', (admin_email,))
        row = cursor.fetchone()
        if row:
            cursor.execute('''
                UPDATE usuarios SET username = ?, password = ?, nombre = ?, rol = 'admin', activo = 1
                WHERE id = ?
            ''', (admin_username, admin_password, 'Administrador', int(row[0])))
        else:
            cursor.execute('''
                INSERT INTO usuarios (username, email, password, nombre, rol, activo)
                VALUES (?, ?, ?, ?, 'admin', 1)
            ''', (admin_username, admin_email, admin_password, 'Administrador'))
        conn.commit()
        conn.close()
        print('✅ Admin reseteado por ADMIN_RESET=1')
        return True
    except Exception as e:
        print(f"Error reseteando admin: {e}")
        return False

def guardar_ticket(ticket_data):
    """Guardar ticket en la base de datos"""
    try:
        conn = sqlite3.connect('belgrano_tickets.db')
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

def verificar_password_compat(stored_hash: str, plain_password: str) -> bool:
    """Verifica password con compatibilidad para hashes 'scrypt:' heredados."""
    # Intento estándar con Werkzeug
    try:
        return check_password_hash(stored_hash, plain_password)
    except Exception:
        pass
    # Compatibilidad scrypt en formato: 'scrypt:N:r:p$salt_hex$digest_hex'
    try:
        if not stored_hash.startswith('scrypt:'):
            return False
        meta_rest = stored_hash.split(':', 1)[1]
        params_part, salt_hex, digest_hex = meta_rest.split('$')
        n_str, r_str, p_str = params_part.split(':')
        n = int(n_str)
        r = int(r_str)
        p = int(p_str)
        salt = binascii.unhexlify(salt_hex)
        expected = binascii.unhexlify(digest_hex)
        dk = hashlib.scrypt(
            plain_password.encode('utf-8'),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=len(expected)
        )
        return hmac.compare_digest(dk, expected)
    except Exception as e:
        print(f"Error verificando hash scrypt: {e}")
        return False

def migrar_hash_si_corresponde(user_id: int, stored_hash: str, plain_password: str) -> None:
    """Si el hash previo es 'scrypt:' y la verificación fue válida, re-hashear con el esquema actual."""
    try:
        if stored_hash.startswith('scrypt:'):
            nuevo_hash = generate_password_hash(plain_password)
            conn = sqlite3.connect('belgrano_tickets.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE usuarios SET password = ? WHERE id = ?', (nuevo_hash, int(user_id)))
            conn.commit()
            conn.close()
            print('🔄 Hash de contraseña migrado a formato actual para el usuario', user_id)
    except Exception as e:
        print(f"Error migrando hash: {e}")

def obtener_todos_los_tickets():
    """Obtener todos los tickets"""
    try:
        conn = sqlite3.connect('belgrano_tickets.db')
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
        conn = sqlite3.connect('belgrano_tickets.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, password, nombre, apellido, telefono, rol, activo
            FROM usuarios
            WHERE email = ?
        ''', (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            print(f"✅ Usuario encontrado: {email} (rol: {row[7]}, activo: {bool(row[8])})")
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
        else:
            print(f"❌ Usuario no encontrado: {email}")
            # Debug: mostrar todos los usuarios disponibles
            conn = sqlite3.connect('belgrano_tickets.db')
            cursor = conn.cursor()
            cursor.execute('SELECT email, rol, activo FROM usuarios')
            all_users = cursor.fetchall()
            conn.close()
            print(f"📋 Usuarios disponibles en DB: {all_users}")
        return None
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None

# =================================================================
# FLASK-LOGIN
# =================================================================

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = sqlite3.connect('belgrano_tickets.db')
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
        
        print(f"Intento de login: {email}")
        
        if not email or not password:
            return render_template('login.html', error='Por favor complete todos los campos')
        
        usuario = obtener_usuario_por_email(email)
        
        if usuario and usuario['activo']:
            print(f"Usuario encontrado y activo: {email}")
            if verificar_password_compat(usuario['password'], password):
                print(f"✅ Login exitoso para: {email}")
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
                try:
                    migrar_hash_si_corresponde(usuario['id'], usuario['password'], password)
                except Exception as e:
                    print(f"Error durante migración de hash: {e}")
                return redirect(url_for('tickets'))
            else:
                print(f"❌ Contraseña incorrecta para: {email}")
                return render_template('login.html', error='Email o contraseña incorrectos')
        else:
            if usuario:
                print(f"❌ Usuario inactivo: {email}")
                return render_template('login.html', error='Usuario inactivo')
            else:
                print(f"❌ Usuario no encontrado: {email}")
                return render_template('login.html', error='Usuario no encontrado o inactivo')
    
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
        conn = sqlite3.connect('belgrano_tickets.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tickets')
        total_tickets = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM usuarios')
        total_usuarios = cursor.fetchone()[0]
        
        # Obtener lista de usuarios para debug
        cursor.execute('SELECT email, rol, activo FROM usuarios')
        usuarios = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'Belgrano Tickets',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'total_tickets': total_tickets,
            'total_usuarios': total_usuarios,
            'usuarios': [{'email': u[0], 'rol': u[1], 'activo': bool(u[2])} for u in usuarios],
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/debug/users')
def debug_users():
    """Endpoint de debug para verificar usuarios"""
    try:
        conn = sqlite3.connect('belgrano_tickets.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, rol, activo FROM usuarios')
        usuarios = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'usuarios': [
                {
                    'id': u[0],
                    'username': u[1], 
                    'email': u[2],
                    'rol': u[3],
                    'activo': bool(u[4])
                } for u in usuarios
            ],
            'total': len(usuarios)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    # Resetear admin si se solicita por entorno
    try:
        if not resetear_admin_si_solicitado():
            print("❌ Error reseteando admin")
            return False
    except NameError:
        # Si la función no existe, continuar sin bloquear el deploy
        pass
    
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

# Inicializar la aplicación al importar el módulo
if __name__ == "__main__":
    if inicializar_aplicacion():
        port = int(os.environ.get('PORT', 5001))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        print(f"🌐 Servidor iniciado en puerto {port}")
        app.run(debug=debug, host='0.0.0.0', port=port)
    else:
        print("❌ Error inicializando aplicación")
else:
    # Inicializar cuando se importa como módulo (para Gunicorn)
    inicializar_aplicacion()
