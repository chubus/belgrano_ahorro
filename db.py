import sqlite3
import hashlib
import secrets
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ==========================================

def crear_base_datos():
    """Crear todas las tablas de la base de datos"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Tabla usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(50) NOT NULL,
                apellido VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefono VARCHAR(20),
                direccion TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                password VARCHAR(100) NOT NULL,
                rol VARCHAR(20) DEFAULT 'cliente'
            )
        ''')
        
        # Tabla productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                store VARCHAR(50) NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                original_price DECIMAL(10,2),
                discount INTEGER,
                new BOOLEAN DEFAULT 0,
                imagen VARCHAR(255),
                categoria VARCHAR(50),
                destacado BOOLEAN DEFAULT 0,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabla carrito
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carrito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        
        # Tabla pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                numero_pedido VARCHAR(50) UNIQUE NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                total DECIMAL(10,2) NOT NULL,
                estado VARCHAR(20) DEFAULT 'pendiente',
                metodo_pago VARCHAR(50),
                direccion_entrega TEXT,
                notas TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabla items de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedido_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        
        # Tabla tokens de recuperación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens_recuperacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token VARCHAR(100) UNIQUE NOT NULL,
                expiracion DATETIME NOT NULL,
                usado BOOLEAN DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al crear base de datos: {e}")

# ========== USUARIOS ==========
def hash_password(password):
    """Hash password usando SHA-256 con salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}${password_hash}"

def verificar_password(password, hashed):
    """Verificar password contra hash"""
    try:
        salt, stored_hash = hashed.split('$', 1)
        password_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return password_hash == stored_hash
    except:
        return False

def crear_usuario(nombre, apellido, email, password, telefono=None, direccion=None):
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return {'exito': False, 'mensaje': 'El email ya está registrado'}
        password_hash = hash_password(password)
        cursor.execute('''INSERT INTO usuarios (nombre, apellido, email, password, telefono, direccion) VALUES (?, ?, ?, ?, ?, ?)''', (nombre, apellido, email, password_hash, telefono, direccion))
        usuario_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {'exito': True, 'usuario_id': usuario_id, 'mensaje': 'Usuario creado exitosamente'}
    except Exception as e:
        logger.error(f"Error al crear usuario: {e}")
        return {'exito': False, 'mensaje': f'Error al crear usuario: {str(e)}'}

def verificar_usuario(email, password):
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id, nombre, apellido, email, password, rol FROM usuarios WHERE email = ?''', (email,))
        usuario = cursor.fetchone()
        conn.close()
        if usuario and verificar_password(password, usuario[4]):
            return {'exito': True, 'usuario': {'id': usuario[0], 'nombre': f"{usuario[1]} {usuario[2]}", 'email': usuario[3], 'rol': usuario[5]}}
        else:
            return {'exito': False, 'mensaje': 'Credenciales incorrectas'}
    except Exception as e:
        logger.error(f"Error al verificar usuario: {e}")
        return {'exito': False, 'mensaje': 'Error interno del servidor'}

def buscar_usuario_por_email(email):
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id, nombre, apellido, email, telefono, direccion, rol FROM usuarios WHERE email = ?''', (email,))
        usuario = cursor.fetchone()
        conn.close()
        if usuario:
            return {'id': usuario[0], 'nombre': f"{usuario[1]} {usuario[2]}", 'email': usuario[3], 'telefono': usuario[4], 'direccion': usuario[5], 'rol': usuario[6]}
        return None
    except Exception as e:
        logger.error(f"Error al buscar usuario: {e}")
        return None

# ========== RECUPERACIÓN DE CONTRASEÑA ==========
def guardar_token_recuperacion(usuario_id, token, expiracion):
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tokens_recuperacion (usuario_id, token, expiracion) VALUES (?, ?, ?)', (usuario_id, token, expiracion))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al guardar token: {e}")
        return False

def verificar_token_recuperacion(email, token):
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT t.id, t.usuario_id, t.expiracion, t.usado FROM tokens_recuperacion t JOIN usuarios u ON t.usuario_id = u.id WHERE u.email = ? AND t.token = ?''', (email, token))
        row = cursor.fetchone()
        conn.close()
        if row and not row[3]:
            return {'exito': True, 'token_id': row[0], 'usuario_id': row[1]}
        return {'exito': False, 'mensaje': 'Token inválido o expirado'}
    except Exception as e:
        logger.error(f"Error al verificar token: {e}")
        return {'exito': False, 'mensaje': 'Error interno'}

def cambiar_password_por_token(email, token_id, nueva_password):
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT u.id FROM usuarios u JOIN tokens_recuperacion t ON u.id = t.usuario_id WHERE t.id = ? AND u.email = ?''', (token_id, email))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        usuario_id = row[0]
        password_hash = hash_password(nueva_password)
        cursor.execute('UPDATE usuarios SET password = ? WHERE id = ?', (password_hash, usuario_id))
        cursor.execute('UPDATE tokens_recuperacion SET usado = 1 WHERE id = ?', (token_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al cambiar password por token: {e}")
        return False

# ========== MÁS FUNCIONES (carrito, pedidos, etc.) ==========
# Puedes agregar aquí el resto de funciones según las necesite la app (copiando de tu backup de database.py)

def obtener_usuario_por_id(usuario_id):
    """Obtener usuario por ID"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id, nombre, apellido, email, telefono, direccion, rol, fecha_registro FROM usuarios WHERE id = ?''', (usuario_id,))
        usuario = cursor.fetchone()
        conn.close()
        if usuario and len(usuario) >= 8:
            return {
                'id': usuario[0], 
                'nombre': f"{usuario[1] or ''} {usuario[2] or ''}".strip(), 
                'email': usuario[3] or '', 
                'telefono': usuario[4] or '', 
                'direccion': usuario[5] or '', 
                'rol': usuario[6] or 'cliente',
                'fecha_registro': usuario[7] if usuario[7] and isinstance(usuario[7], str) else None
            }
        return None
    except Exception as e:
        logger.error(f"Error al obtener usuario por ID: {e}")
        return None

def actualizar_usuario(usuario_id, nombre, telefono, direccion):
    """Actualizar información del usuario"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''UPDATE usuarios SET nombre = ?, telefono = ?, direccion = ? WHERE id = ?''', (nombre, telefono, direccion, usuario_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {e}")
        return False

def cambiar_password(usuario_id, password_actual, password_nuevo):
    """Cambiar contraseña del usuario"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Verificar password actual
        cursor.execute('SELECT password FROM usuarios WHERE id = ?', (usuario_id,))
        usuario = cursor.fetchone()
        if not usuario or not verificar_password(password_actual, usuario[0]):
            conn.close()
            return False
        
        # Cambiar password
        password_hash = hash_password(password_nuevo)
        cursor.execute('UPDATE usuarios SET password = ? WHERE id = ?', (password_hash, usuario_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al cambiar password: {e}")
        return False

def guardar_pedido(usuario_id, numero_pedido, total, metodo_pago, direccion_entrega, notas):
    """Guardar un nuevo pedido"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO pedidos (usuario_id, numero_pedido, total, metodo_pago, direccion_entrega, notas) VALUES (?, ?, ?, ?, ?, ?)''', 
                      (usuario_id, numero_pedido, total, metodo_pago, direccion_entrega, notas))
        pedido_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pedido_id
    except Exception as e:
        logger.error(f"Error al guardar pedido: {e}")
        return None

def guardar_items_pedido(pedido_id, items):
    """Guardar items de un pedido"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        for item in items:
            cursor.execute('''INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)''',
                          (pedido_id, item['producto_id'], item['cantidad'], item['precio_unitario'], item['subtotal']))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al guardar items de pedido: {e}")
        return False

def obtener_pedidos_usuario(usuario_id):
    """Obtener todos los pedidos de un usuario"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id, numero_pedido, fecha, total, estado FROM pedidos WHERE usuario_id = ? ORDER BY fecha DESC''', (usuario_id,))
        pedidos = []
        for row in cursor.fetchall():
            pedidos.append({
                'id': row[0],
                'numero_pedido': row[1],
                'fecha': row[2],
                'total': row[3],
                'estado': row[4]
            })
        conn.close()
        return pedidos
    except Exception as e:
        logger.error(f"Error al obtener pedidos: {e}")
        return []

def obtener_pedido_completo(pedido_id):
    """Obtener un pedido completo con sus items"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Obtener pedido
        cursor.execute('''SELECT id, numero_pedido, fecha, total, estado, metodo_pago, direccion_entrega, notas FROM pedidos WHERE id = ?''', (pedido_id,))
        pedido_row = cursor.fetchone()
        if not pedido_row:
            conn.close()
            return None
        
        pedido = {
            'id': pedido_row[0],
            'numero_pedido': pedido_row[1],
            'fecha': pedido_row[2],
            'total': pedido_row[3],
            'estado': pedido_row[4],
            'metodo_pago': pedido_row[5],
            'direccion_entrega': pedido_row[6],
            'notas': pedido_row[7],
            'items': []
        }
        
        # Obtener items del pedido
        cursor.execute('''SELECT pi.producto_id, pi.cantidad, pi.precio_unitario, pi.subtotal, p.nombre, p.imagen 
                         FROM pedido_items pi 
                         JOIN productos p ON pi.producto_id = p.id 
                         WHERE pi.pedido_id = ?''', (pedido_id,))
        
        for row in cursor.fetchall():
            pedido['items'].append({
                'producto_id': row[0],
                'cantidad': row[1],
                'precio_unitario': row[2],
                'subtotal': row[3],
                'nombre': row[4],
                'imagen': row[5]
            })
        
        conn.close()
        return pedido
    except Exception as e:
        logger.error(f"Error al obtener pedido completo: {e}")
        return None

def repetir_pedido(pedido_id, usuario_id):
    """Repetir un pedido anterior"""
    try:
        # Obtener pedido original
        pedido_original = obtener_pedido_completo(pedido_id)
        if not pedido_original:
            return False, "Pedido no encontrado"
        
        # Crear nuevo pedido
        numero_pedido = generar_numero_pedido()
        nuevo_pedido_id = guardar_pedido(
            usuario_id=usuario_id,
            numero_pedido=numero_pedido,
            total=pedido_original['total'],
            metodo_pago=pedido_original['metodo_pago'],
            direccion_entrega=pedido_original['direccion_entrega'],
            notas=f"Pedido repetido del {pedido_original['numero_pedido']}"
        )
        
        if nuevo_pedido_id:
            # Copiar items del pedido original
            items = []
            for item in pedido_original['items']:
                items.append({
                    'producto_id': item['producto_id'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario'],
                    'subtotal': item['subtotal']
                })
            
            guardar_items_pedido(nuevo_pedido_id, items)
            return True, numero_pedido
        else:
            return False, "Error al crear nuevo pedido"
            
    except Exception as e:
        logger.error(f"Error al repetir pedido: {e}")
        return False, str(e)

def generar_numero_pedido():
    """Generar número único de pedido"""
    import uuid
    from datetime import datetime
    fecha = datetime.now().strftime("%Y%m%d")
    codigo = str(uuid.uuid4())[:8].upper()
    return f"PED-{fecha}-{codigo}"
