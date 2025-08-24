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
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar db desde models
from models import db, User, Ticket

# Inicializar db con la app
db.init_app(app)

# Crear contexto de aplicación para inicializar la base de datos
with app.app_context():
    db.create_all()

login_manager = LoginManager(app)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"🔐 Intento de login: {email}")
        
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
