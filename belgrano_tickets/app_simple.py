import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Inicialización Flask y extensiones
app = Flask(__name__)
app.config['SECRET_KEY'] = 'belgrano_tickets_secret_2025'

# Configuración de base de datos - USAR RUTA ABSOLUTA
import os
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'belgrano_tickets.db')
print(f"🗄️ Ruta de base de datos: {db_path}")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar db desde models
from models import db, User, Ticket

# Inicializar db con la app
db.init_app(app)

def inicializar_base_datos():
    """Inicializar base de datos y usuarios por defecto"""
    try:
        print("🔧 Inicializando base de datos...")
        db.create_all()
        print("✅ Base de datos creada/verificada")
        
        # FORZAR CREACIÓN DE USUARIOS - ELIMINAR TODOS Y RECREAR
        print("🗑️ Eliminando usuarios existentes para recrear...")
        User.query.delete()
        db.session.commit()
        print("✅ Usuarios eliminados")
        
        # Crear admin SIEMPRE
        print("🔧 Creando usuario admin...")
        admin = User(
            username='admin',
            email='admin@belgranoahorro.com',
            password=generate_password_hash('admin123'),
            role='admin',
            nombre='Administrador Principal'
        )
        db.session.add(admin)
        print("✅ Usuario admin creado")
        
        # Crear usuarios de flota SIEMPRE
        flota_emails = [
            'repartidor1@belgranoahorro.com',
            'repartidor2@belgranoahorro.com',
            'repartidor3@belgranoahorro.com',
            'repartidor4@belgranoahorro.com',
            'repartidor5@belgranoahorro.com'
        ]
        
        for i, email in enumerate(flota_emails, 1):
            print(f"🔧 Creando usuario flota {i}...")
            flota = User(
                username=f'repartidor{i}',
                email=email,
                password=generate_password_hash('flota123'),
                role='flota',
                nombre=f'Repartidor {i}'
            )
            db.session.add(flota)
            print(f"✅ Usuario flota {i} creado")
        
        # Commit de todos los cambios
        db.session.commit()
        print("🎉 Inicialización completada - TODOS los usuarios recreados")
        
        # Verificar usuarios finales
        usuarios_finales = User.query.all()
        print(f"📋 Usuarios en BD después de inicialización:")
        for usuario in usuarios_finales:
            print(f"   - {usuario.email} (Role: {usuario.role})")
        
        # Verificar que las contraseñas funcionan
        print("🔐 Verificando contraseñas...")
        admin_test = User.query.filter_by(email='admin@belgranoahorro.com').first()
        if admin_test and check_password_hash(admin_test.password, 'admin123'):
            print("✅ Contraseña admin verificada correctamente")
        else:
            print("❌ ERROR: Contraseña admin no funciona")
        
        flota_test = User.query.filter_by(email='repartidor1@belgranoahorro.com').first()
        if flota_test and check_password_hash(flota_test.password, 'flota123'):
            print("✅ Contraseña flota verificada correctamente")
        else:
            print("❌ ERROR: Contraseña flota no funciona")
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        db.session.rollback()
        raise e

# Crear contexto de aplicación para inicializar la base de datos
with app.app_context():
    inicializar_base_datos()

login_manager = LoginManager(app)

# Middleware para verificar usuarios en cada request
@app.before_request
def verificar_usuarios():
    """Verificar que existan usuarios en cada request"""
    try:
        # Solo verificar en rutas que no sean de debug
        if not request.path.startswith('/debug') and not request.path.startswith('/health') and not request.path.startswith('/crear_'):
            total_usuarios = User.query.count()
            if total_usuarios == 0:
                print("🚨 No hay usuarios en BD - Inicializando...")
                inicializar_base_datos()
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")

# Filtro personalizado para JSON
@app.template_filter('from_json')
def from_json_filter(value):
    try:
        return json.loads(value) if value else []
    except (json.JSONDecodeError, TypeError):
        return []

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Decorador para roles
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(current_user, 'role') or current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rutas principales
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('panel'))
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Health check para Render"""
    try:
        # Verificar que la base de datos esté funcionando
        user_count = User.query.count()
        usuarios = User.query.all()
        usuarios_info = []
        for user in usuarios:
            usuarios_info.append({
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'nombre': user.nombre
            })
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users_count': user_count,
            'users': usuarios_info,
            'message': 'Ticketera funcionando correctamente'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/debug')
def debug_info():
    """Información de debug para verificar estado"""
    try:
        usuarios = User.query.all()
        return jsonify({
            'total_usuarios': len(usuarios),
            'usuarios': [
                {
                    'id': u.id,
                    'email': u.email,
                    'role': u.role,
                    'nombre': u.nombre,
                    'username': u.username
                } for u in usuarios
            ],
            'credenciales_admin': 'admin@belgranoahorro.com / admin123',
            'credenciales_flota': 'repartidor1@belgranoahorro.com / flota123'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reinicializar')
def reinicializar_usuarios():
    """Forzar reinicialización de usuarios (solo para debug)"""
    try:
        # Eliminar todos los usuarios existentes
        User.query.delete()
        db.session.commit()
        print("🗑️ Usuarios eliminados")
        
        # Ejecutar inicialización
        inicializar_base_datos()
        
        return jsonify({
            'status': 'success',
            'message': 'Usuarios reinicializados correctamente',
            'credenciales_admin': 'admin@belgranoahorro.com / admin123',
            'credenciales_flota': 'repartidor1@belgranoahorro.com / flota123'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/crear_admin_emergencia')
def crear_admin_emergencia():
    """Crear admin de emergencia si todo falla"""
    try:
        # Verificar si admin existe
        admin = User.query.filter_by(email='admin@belgranoahorro.com').first()
        if admin:
            # Actualizar contraseña
            admin.password = generate_password_hash('admin123')
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Admin actualizado',
                'email': 'admin@belgranoahorro.com',
                'password': 'admin123'
            }), 200
        else:
            # Crear admin nuevo
            admin = User(
                username='admin',
                email='admin@belgranoahorro.com',
                password=generate_password_hash('admin123'),
                role='admin',
                nombre='Administrador Principal'
            )
            db.session.add(admin)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Admin creado de emergencia',
                'email': 'admin@belgranoahorro.com',
                'password': 'admin123'
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/crear_flota_emergencia')
def crear_flota_emergencia():
    """Crear flota de emergencia si todo falla"""
    try:
        # Crear repartidor 1
        flota = User.query.filter_by(email='repartidor1@belgranoahorro.com').first()
        if flota:
            # Actualizar contraseña
            flota.password = generate_password_hash('flota123')
            db.session.commit()
        else:
            # Crear flota nuevo
            flota = User(
                username='repartidor1',
                email='repartidor1@belgranoahorro.com',
                password=generate_password_hash('flota123'),
                role='flota',
                nombre='Repartidor 1'
            )
            db.session.add(flota)
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Flota creada/actualizada de emergencia',
            'email': 'repartidor1@belgranoahorro.com',
            'password': 'flota123'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/crear_usuarios_directo')
def crear_usuarios_directo():
    """Crear usuarios directamente sin verificar"""
    try:
        # Eliminar todos los usuarios
        User.query.delete()
        db.session.commit()
        
        # Crear admin
        admin = User(
            username='admin',
            email='admin@belgranoahorro.com',
            password=generate_password_hash('admin123'),
            role='admin',
            nombre='Administrador Principal'
        )
        db.session.add(admin)
        
        # Crear flota
        flota = User(
            username='repartidor1',
            email='repartidor1@belgranoahorro.com',
            password=generate_password_hash('flota123'),
            role='flota',
            nombre='Repartidor 1'
        )
        db.session.add(flota)
        
        db.session.commit()
        
        # Verificar
        usuarios = User.query.all()
        
        return jsonify({
            'status': 'success',
            'message': 'Usuarios creados directamente',
            'usuarios_creados': len(usuarios),
            'admin': {
                'email': 'admin@belgranoahorro.com',
                'password': 'admin123',
                'role': 'admin'
            },
            'flota': {
                'email': 'repartidor1@belgranoahorro.com',
                'password': 'flota123',
                'role': 'flota'
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"🔐 Intento de login: {email}")
        
        # Debug: mostrar todos los usuarios en la base de datos
        todos_usuarios = User.query.all()
        print(f"📊 Total de usuarios en BD: {len(todos_usuarios)}")
        for u in todos_usuarios:
            print(f"   - {u.email} (Role: {u.role})")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"✅ Usuario encontrado: {user.nombre} (ID: {user.id})")
            print(f"   Role: {user.role}")
            
            if check_password_hash(user.password, password):
                print("✅ Contraseña correcta - Login exitoso")
                login_user(user)
                return redirect(url_for('panel'))
            else:
                print("❌ Contraseña incorrecta")
                flash('Contraseña incorrecta', 'danger')
        else:
            print(f"❌ Usuario no encontrado: {email}")
            flash('Usuario no encontrado', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/panel')
@login_required
def panel():
    if current_user.role == 'admin':
        # Ordenar tickets por fecha de creación (más reciente primero)
        tickets = Ticket.query.order_by(Ticket.fecha_creacion.desc()).all()
        return render_template('admin_panel.html', tickets=tickets)
    elif current_user.role == 'flota':
        tickets = Ticket.query.filter_by(asignado_a=current_user.id).order_by(Ticket.fecha_creacion.desc()).all()
        return render_template('flota_panel.html', tickets=tickets)
    else:
        return 'Acceso no permitido', 403

@app.route('/ticket/<int:ticket_id>')
@login_required
def detalle_ticket(ticket_id):
    """Ver detalles de un ticket específico"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Verificar permisos
    if current_user.role == 'flota' and ticket.asignado_a != current_user.id:
        abort(403)
    
    return render_template('detalle_ticket.html', ticket=ticket)

@app.route('/ticket/<int:ticket_id>/cambiar_estado', methods=['POST'])
@login_required
def cambiar_estado_ticket(ticket_id):
    """Cambiar estado de un ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    nuevo_estado = request.form.get('estado')
    
    # Verificar permisos
    if current_user.role == 'flota' and ticket.asignado_a != current_user.id:
        abort(403)
    
    if nuevo_estado in ['pendiente', 'en_proceso', 'completado', 'cancelado']:
        ticket.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado del ticket {ticket.numero} cambiado a {nuevo_estado}', 'success')
    
    return redirect(url_for('detalle_ticket', ticket_id=ticket_id))

@app.route('/ticket/<int:ticket_id>/asignar', methods=['POST'])
@login_required
@role_required('admin')
def asignar_ticket(ticket_id):
    """Asignar ticket a un repartidor (solo admin)"""
    ticket = Ticket.query.get_or_404(ticket_id)
    repartidor_id = request.form.get('repartidor_id')
    
    if repartidor_id:
        ticket.asignado_a = int(repartidor_id)
        db.session.commit()
        flash(f'Ticket {ticket.numero} asignado exitosamente', 'success')
    
    return redirect(url_for('detalle_ticket', ticket_id=ticket_id))

@app.route('/gestion_usuarios')
@login_required
@role_required('admin')
def gestion_usuarios():
    """Gestionar usuarios (solo admin)"""
    usuarios = User.query.all()
    return render_template('gestion_usuarios.html', usuarios=usuarios)

@app.route('/crear_usuario', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def crear_usuario():
    """Crear nuevo usuario (solo admin)"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        role = request.form.get('role')
        password = request.form.get('password')
        
        # Validaciones
        if not all([username, email, nombre, role, password]):
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('crear_usuario'))
        
        # Verificar si el username ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'danger')
            return redirect(url_for('crear_usuario'))
        
        # Verificar si el email ya existe
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('crear_usuario'))
        
        # Crear usuario
        nuevo_usuario = User(
            username=username,
            email=email,
            nombre=nombre,
            role=role,
            password=generate_password_hash(password)
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash(f'Usuario {nombre} creado exitosamente', 'success')
        return redirect(url_for('gestion_usuarios'))
    
    return render_template('crear_usuario.html')

@app.route('/cambiar_password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Cambiar contraseña del usuario actual"""
    if request.method == 'POST':
        password_actual = request.form.get('password_actual')
        nueva_password = request.form.get('nueva_password')
        confirmar_password = request.form.get('confirmar_password')
        
        # Validaciones
        if not check_password_hash(current_user.password, password_actual):
            flash('La contraseña actual es incorrecta', 'danger')
            return redirect(url_for('cambiar_password'))
        
        if nueva_password != confirmar_password:
            flash('Las contraseñas nuevas no coinciden', 'danger')
            return redirect(url_for('cambiar_password'))
        
        if len(nueva_password) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres', 'danger')
            return redirect(url_for('cambiar_password'))
        
        # Actualizar contraseña
        current_user.password = generate_password_hash(nueva_password)
        db.session.commit()
        
        flash('Contraseña cambiada exitosamente', 'success')
        return redirect(url_for('panel'))
    
    return render_template('cambiar_password.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("🚀 Iniciando aplicación de tickets simplificada en puerto 5001...")
    print("📱 Abre tu navegador en: http://localhost:5001")
    print("🔐 Credenciales admin: admin@belgranoahorro.com / admin123")
    print("🔐 Credenciales flota: repartidor1@belgranoahorro.com / flota123")
    app.run(debug=True, host='0.0.0.0', port=5001)
