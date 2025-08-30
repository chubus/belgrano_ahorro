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
        
        # Tabla comerciantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comerciantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                nombre_negocio VARCHAR(100) NOT NULL,
                cuit VARCHAR(20),
                direccion_comercial TEXT,
                telefono_comercial VARCHAR(20),
                tipo_negocio VARCHAR(50),
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        
        # Tabla paquetes de comerciantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paquetes_comerciantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comerciante_id INTEGER NOT NULL,
                nombre_paquete VARCHAR(100) NOT NULL,
                descripcion TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1,
                frecuencia VARCHAR(20) DEFAULT 'mensual',
                proximo_pedido DATE,
                FOREIGN KEY (comerciante_id) REFERENCES comerciantes (id)
            )
        ''')
        
        # Tabla items de paquetes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paquete_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paquete_id INTEGER NOT NULL,
                producto_id VARCHAR(50) NOT NULL,
                cantidad INTEGER NOT NULL,
                FOREIGN KEY (paquete_id) REFERENCES paquetes_comerciantes (id)
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

def crear_usuario(nombre, apellido, email, password, telefono=None, direccion=None, rol='cliente'):
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return {'exito': False, 'mensaje': 'El email ya está registrado'}
        password_hash = hash_password(password)
        cursor.execute('''INSERT INTO usuarios (nombre, apellido, email, password, telefono, direccion, rol) VALUES (?, ?, ?, ?, ?, ?, ?)''', (nombre, apellido, email, password_hash, telefono, direccion, rol))
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

# ========== COMERCIANTES ==========
def crear_comerciante(usuario_id, nombre_negocio, cuit=None, direccion_comercial=None, telefono_comercial=None, tipo_negocio=None):
    """Crear un nuevo comerciante"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Verificar si el usuario ya es comerciante
        cursor.execute('SELECT id FROM comerciantes WHERE usuario_id = ?', (usuario_id,))
        if cursor.fetchone():
            return {'exito': False, 'mensaje': 'El usuario ya está registrado como comerciante'}
        
        # Insertar comerciante
        cursor.execute('''
            INSERT INTO comerciantes (usuario_id, nombre_negocio, cuit, direccion_comercial, telefono_comercial, tipo_negocio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario_id, nombre_negocio, cuit, direccion_comercial, telefono_comercial, tipo_negocio))
        
        conn.commit()
        conn.close()
        return {'exito': True, 'mensaje': 'Comerciante registrado exitosamente'}
    except Exception as e:
        logger.error(f"Error creando comerciante: {e}")
        return {'exito': False, 'mensaje': f'Error al crear comerciante: {str(e)}'}

def obtener_comerciante_por_usuario(usuario_id):
    """Obtener información del comerciante por usuario_id"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.nombre, u.apellido, u.email, u.telefono
            FROM comerciantes c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.usuario_id = ? AND c.activo = 1
        ''', (usuario_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'usuario_id': row[1],
                'nombre_negocio': row[2],
                'cuit': row[3],
                'direccion_comercial': row[4],
                'telefono_comercial': row[5],
                'tipo_negocio': row[6],
                'fecha_registro': row[7],
                'activo': row[8],
                'nombre': row[9],
                'apellido': row[10],
                'email': row[11],
                'telefono': row[12]
            }
        return None
    except Exception as e:
        logger.error(f"Error obteniendo comerciante: {e}")
        return None

def crear_paquete_comerciante(comerciante_id, nombre_paquete, descripcion=None, frecuencia='mensual'):
    """Crear un nuevo paquete para comerciante"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Calcular próximo pedido (1 mes desde hoy)
        from datetime import datetime, timedelta
        proximo_pedido = (datetime.now() + timedelta(days=30)).date()
        
        cursor.execute('''
            INSERT INTO paquetes_comerciantes (comerciante_id, nombre_paquete, descripcion, frecuencia, proximo_pedido)
            VALUES (?, ?, ?, ?, ?)
        ''', (comerciante_id, nombre_paquete, descripcion, frecuencia, proximo_pedido))
        
        paquete_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {'exito': True, 'paquete_id': paquete_id, 'mensaje': 'Paquete creado exitosamente'}
    except Exception as e:
        logger.error(f"Error creando paquete: {e}")
        return {'exito': False, 'mensaje': f'Error al crear paquete: {str(e)}'}

def agregar_producto_a_paquete(paquete_id, producto_id, cantidad):
    """Agregar un producto a un paquete"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO paquete_items (paquete_id, producto_id, cantidad)
            VALUES (?, ?, ?)
        ''', (paquete_id, producto_id, cantidad))
        
        conn.commit()
        conn.close()
        return {'exito': True, 'mensaje': 'Producto agregado al paquete'}
    except Exception as e:
        logger.error(f"Error agregando producto a paquete: {e}")
        return {'exito': False, 'mensaje': f'Error al agregar producto: {str(e)}'}

def obtener_paquetes_comerciante(comerciante_id):
    """Obtener todos los paquetes de un comerciante"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nombre_paquete, descripcion, fecha_creacion, frecuencia, proximo_pedido, activo
            FROM paquetes_comerciantes
            WHERE comerciante_id = ? AND activo = 1
            ORDER BY fecha_creacion DESC
        ''', (comerciante_id,))
        
        paquetes = []
        for row in cursor.fetchall():
            paquete = {
                'id': row[0],
                'nombre_paquete': row[1],
                'descripcion': row[2],
                'fecha_creacion': row[3],
                'frecuencia': row[4],
                'proximo_pedido': row[5],
                'activo': row[6]
            }
            
            # Obtener items del paquete
            cursor.execute('''
                SELECT producto_id, cantidad
                FROM paquete_items
                WHERE paquete_id = ?
            ''', (paquete['id'],))
            
            paquete['items'] = [{'producto_id': row[0], 'cantidad': row[1]} for row in cursor.fetchall()]
            paquetes.append(paquete)
        
        conn.close()
        return paquetes
    except Exception as e:
        logger.error(f"Error obteniendo paquetes: {e}")
        return []

def procesar_pedido_automatico_paquete(paquete_id):
    """Procesar pedido automático de un paquete"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Obtener información del paquete y comerciante
        cursor.execute('''
            SELECT pc.comerciante_id, pc.nombre_paquete, c.usuario_id
            FROM paquetes_comerciantes pc
            JOIN comerciantes c ON pc.comerciante_id = c.id
            WHERE pc.id = ?
        ''', (paquete_id,))
        
        row = cursor.fetchone()
        if not row:
            return {'exito': False, 'mensaje': 'Paquete no encontrado'}
        
        comerciante_id, nombre_paquete, usuario_id = row
        
        # Obtener items del paquete
        cursor.execute('''
            SELECT producto_id, cantidad
            FROM paquete_items
            WHERE paquete_id = ?
        ''', (paquete_id,))
        
        items = cursor.fetchall()
        if not items:
            return {'exito': False, 'mensaje': 'Paquete sin productos'}
        
        # Crear pedido automático
        numero_pedido = f"PAQ-{paquete_id}-{datetime.now().strftime('%Y%m%d')}"
        total = 0
        
        # Calcular total (necesitarías obtener precios de productos.json)
        # Por ahora usamos un total estimado
        total = sum(cantidad * 100 for _, cantidad in items)  # Precio estimado $100 por producto
        
        cursor.execute('''
            INSERT INTO pedidos (usuario_id, numero_pedido, total, estado, metodo_pago, direccion_entrega, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (usuario_id, numero_pedido, total, 'pendiente', 'transferencia', 'Entrega comercial', f'Pedido automático - {nombre_paquete}'))
        
        pedido_id = cursor.lastrowid
        
        # Agregar items al pedido
        for producto_id, cantidad in items:
            cursor.execute('''
                INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (pedido_id, producto_id, cantidad, 100, cantidad * 100))  # Precio estimado
        
        # Actualizar próximo pedido
        from datetime import datetime, timedelta
        proximo_pedido = (datetime.now() + timedelta(days=30)).date()
        cursor.execute('''
            UPDATE paquetes_comerciantes
            SET proximo_pedido = ?
            WHERE id = ?
        ''', (proximo_pedido, paquete_id))
        
        conn.commit()
        conn.close()
        return {'exito': True, 'numero_pedido': numero_pedido, 'mensaje': 'Pedido automático procesado'}
    except Exception as e:
        logger.error(f"Error procesando pedido automático: {e}")
        return {'exito': False, 'mensaje': f'Error al procesar pedido: {str(e)}'}

# ==========================================
# FUNCIONES PARA TICKETS
# ==========================================

def crear_tabla_tickets():
    """Crear tabla de tickets si no existe"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero VARCHAR(50) UNIQUE NOT NULL,
                cliente_nombre VARCHAR(100) NOT NULL,
                cliente_direccion TEXT,
                cliente_telefono VARCHAR(20),
                cliente_email VARCHAR(100),
                productos TEXT NOT NULL,
                total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                estado VARCHAR(20) DEFAULT 'pendiente',
                estado_envio VARCHAR(20) DEFAULT 'pendiente',
                prioridad VARCHAR(20) DEFAULT 'normal',
                indicaciones TEXT,
                repartidor VARCHAR(50),
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_envio DATETIME,
                fecha_entrega DATETIME
            )
        ''')
        
        # Crear tabla de registro de tickets (historial)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                numero VARCHAR(50) NOT NULL,
                cliente_nombre VARCHAR(100) NOT NULL,
                cliente_direccion TEXT,
                cliente_telefono VARCHAR(20),
                cliente_email VARCHAR(100),
                productos TEXT NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                estado_final VARCHAR(20) NOT NULL,
                estado_envio_final VARCHAR(20) NOT NULL,
                prioridad VARCHAR(20),
                indicaciones TEXT,
                repartidor VARCHAR(50),
                fecha_creacion DATETIME,
                fecha_envio DATETIME,
                fecha_entrega DATETIME,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        ''')
        
        # Agregar columnas si no existen (para compatibilidad con bases de datos existentes)
        try:
            cursor.execute('ALTER TABLE tickets ADD COLUMN total DECIMAL(10,2) DEFAULT 0.00')
        except:
            pass  # La columna ya existe
            
        try:
            cursor.execute('ALTER TABLE tickets ADD COLUMN estado_envio VARCHAR(20) DEFAULT "pendiente"')
        except:
            pass  # La columna ya existe
            
        try:
            cursor.execute('ALTER TABLE tickets ADD COLUMN fecha_envio DATETIME')
        except:
            pass  # La columna ya existe
            
        try:
            cursor.execute('ALTER TABLE tickets ADD COLUMN fecha_entrega DATETIME')
        except:
            pass  # La columna ya existe
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creando tabla tickets: {e}")
        return False

def guardar_ticket(**kwargs):
    """Guardar un nuevo ticket"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (
                numero, cliente_nombre, cliente_direccion, cliente_telefono,
                cliente_email, productos, total, estado, estado_envio, prioridad, 
                indicaciones, repartidor, fecha_creacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            kwargs.get('numero'),
            kwargs.get('cliente_nombre'),
            kwargs.get('cliente_direccion'),
            kwargs.get('cliente_telefono'),
            kwargs.get('cliente_email'),
            kwargs.get('productos'),
            kwargs.get('total', 0.00),
            kwargs.get('estado', 'pendiente'),
            kwargs.get('estado_envio', 'pendiente'),
            kwargs.get('prioridad', 'normal'),
            kwargs.get('indicaciones'),
            kwargs.get('repartidor'),
            kwargs.get('fecha_creacion', datetime.now())
        ))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticket_id
    except Exception as e:
        logger.error(f"Error guardando ticket: {e}")
        return None

def obtener_todos_los_tickets():
    """Obtener todos los tickets"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, numero, cliente_nombre, cliente_direccion, cliente_telefono,
                   cliente_email, productos, total, estado, estado_envio, prioridad, 
                   indicaciones, repartidor, fecha_creacion, fecha_actualizacion,
                   fecha_envio, fecha_entrega
            FROM tickets
            ORDER BY fecha_creacion DESC
        ''')
        
        tickets = []
        for row in cursor.fetchall():
            tickets.append({
                'id': row[0],
                'numero': row[1],
                'cliente_nombre': row[2],
                'cliente_direccion': row[3],
                'cliente_telefono': row[4],
                'cliente_email': row[5],
                'productos': row[6],
                'total': row[7] or 0.00,
                'estado': row[8],
                'estado_envio': row[9],
                'prioridad': row[10],
                'indicaciones': row[11],
                'repartidor': row[12],
                'fecha_creacion': row[13],
                'fecha_actualizacion': row[14],
                'fecha_envio': row[15],
                'fecha_entrega': row[16]
            })
        
        conn.close()
        return tickets
    except Exception as e:
        logger.error(f"Error obteniendo tickets: {e}")
        return []

def obtener_tickets_por_repartidor(repartidor):
    """Obtener tickets asignados a un repartidor"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, numero, cliente_nombre, cliente_direccion, cliente_telefono,
                   cliente_email, productos, total, estado, estado_envio, prioridad, 
                   indicaciones, repartidor, fecha_creacion, fecha_actualizacion,
                   fecha_envio, fecha_entrega
            FROM tickets
            WHERE repartidor = ?
            ORDER BY fecha_creacion DESC
        ''', (repartidor,))
        
        tickets = []
        for row in cursor.fetchall():
            tickets.append({
                'id': row[0],
                'numero': row[1],
                'cliente_nombre': row[2],
                'cliente_direccion': row[3],
                'cliente_telefono': row[4],
                'cliente_email': row[5],
                'productos': row[6],
                'total': row[7] or 0.00,
                'estado': row[8],
                'estado_envio': row[9],
                'prioridad': row[10],
                'indicaciones': row[11],
                'repartidor': row[12],
                'fecha_creacion': row[13],
                'fecha_actualizacion': row[14],
                'fecha_envio': row[15],
                'fecha_entrega': row[16]
            })
        
        conn.close()
        return tickets
    except Exception as e:
        logger.error(f"Error obteniendo tickets por repartidor: {e}")
        return []

def obtener_usuarios_por_rol(rol):
    """Obtener usuarios por rol"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nombre, apellido, email, telefono, rol
            FROM usuarios
            WHERE rol = ?
            ORDER BY nombre
        ''', (rol,))
        
        usuarios = []
        for row in cursor.fetchall():
            usuarios.append({
                'id': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'email': row[3],
                'telefono': row[4],
                'rol': row[5]
            })
        
        conn.close()
        return usuarios
    except Exception as e:
        logger.error(f"Error obteniendo usuarios por rol: {e}")
        return []

def contar_tickets():
    """Contar total de tickets"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM tickets')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    except Exception as e:
        logger.error(f"Error contando tickets: {e}")
        return 0

def actualizar_estado_ticket(ticket_id, estado, estado_envio=None, repartidor=None, prioridad=None):
    """Actualizar estado de un ticket"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Preparar la consulta dinámicamente
        query_parts = ['UPDATE tickets SET']
        params = []
        
        if estado:
            query_parts.append('estado = ?')
            params.append(estado)
            
        if estado_envio:
            query_parts.append('estado_envio = ?')
            params.append(estado_envio)
            
        if repartidor:
            query_parts.append('repartidor = ?')
            params.append(repartidor)
            
        if prioridad:
            query_parts.append('prioridad = ?')
            params.append(prioridad)
            
        # Agregar fecha de actualización
        query_parts.append('fecha_actualizacion = ?')
        params.append(datetime.now())
        
        # Agregar fechas específicas según el estado
        if estado_envio == 'en-envio':
            query_parts.append('fecha_envio = ?')
            params.append(datetime.now())
        elif estado_envio == 'entregado':
            query_parts.append('fecha_entrega = ?')
            params.append(datetime.now())
        
        query_parts.append('WHERE id = ?')
        params.append(ticket_id)
        
        query = ', '.join(query_parts)
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error actualizando estado del ticket: {e}")
        return False

def mover_ticket_a_registro(ticket_id):
    """Mover un ticket completado al registro de tickets"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        # Obtener datos del ticket
        cursor.execute('''
            SELECT id, numero, cliente_nombre, cliente_direccion, cliente_telefono,
                   cliente_email, productos, total, estado, estado_envio, prioridad,
                   indicaciones, repartidor, fecha_creacion, fecha_envio, fecha_entrega
            FROM tickets
            WHERE id = ?
        ''', (ticket_id,))
        
        ticket = cursor.fetchone()
        if not ticket:
            conn.close()
            return False
        
        # Insertar en registro de tickets
        cursor.execute('''
            INSERT INTO registro_tickets (
                ticket_id, numero, cliente_nombre, cliente_direccion, cliente_telefono,
                cliente_email, productos, total, estado_final, estado_envio_final,
                prioridad, indicaciones, repartidor, fecha_creacion, fecha_envio, fecha_entrega
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticket[0], ticket[1], ticket[2], ticket[3], ticket[4], ticket[5],
            ticket[6], ticket[7], ticket[8], ticket[9], ticket[10], ticket[11],
            ticket[12], ticket[13], ticket[14], ticket[15]
        ))
        
        # Eliminar el ticket de la tabla principal
        cursor.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error moviendo ticket a registro: {e}")
        return False

def obtener_tickets_registro():
    """Obtener tickets del registro (historial)"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, ticket_id, numero, cliente_nombre, cliente_direccion, cliente_telefono,
                   cliente_email, productos, total, estado_final, estado_envio_final,
                   prioridad, indicaciones, repartidor, fecha_creacion, fecha_envio,
                   fecha_entrega, fecha_registro
            FROM registro_tickets
            ORDER BY fecha_registro DESC
        ''')
        
        tickets = []
        for row in cursor.fetchall():
            tickets.append({
                'id': row[0],
                'ticket_id': row[1],
                'numero': row[2],
                'cliente_nombre': row[3],
                'cliente_direccion': row[4],
                'cliente_telefono': row[5],
                'cliente_email': row[6],
                'productos': row[7],
                'total': row[8] or 0.00,
                'estado_final': row[9],
                'estado_envio_final': row[10],
                'prioridad': row[11],
                'indicaciones': row[12],
                'repartidor': row[13],
                'fecha_creacion': row[14],
                'fecha_envio': row[15],
                'fecha_entrega': row[16],
                'fecha_registro': row[17]
            })
        
        conn.close()
        return tickets
    except Exception as e:
        logger.error(f"Error obteniendo tickets del registro: {e}")
        return []

def obtener_ticket_por_id(ticket_id):
    """Obtener un ticket específico por ID"""
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, numero, cliente_nombre, cliente_direccion, cliente_telefono,
                   cliente_email, productos, total, estado, estado_envio, prioridad,
                   indicaciones, repartidor, fecha_creacion, fecha_actualizacion,
                   fecha_envio, fecha_entrega
            FROM tickets
            WHERE id = ?
        ''', (ticket_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'numero': row[1],
                'cliente_nombre': row[2],
                'cliente_direccion': row[3],
                'cliente_telefono': row[4],
                'cliente_email': row[5],
                'productos': row[6],
                'total': row[7] or 0.00,
                'estado': row[8],
                'estado_envio': row[9],
                'prioridad': row[10],
                'indicaciones': row[11],
                'repartidor': row[12],
                'fecha_creacion': row[13],
                'fecha_actualizacion': row[14],
                'fecha_envio': row[15],
                'fecha_entrega': row[16]
            }
        return None
    except Exception as e:
        logger.error(f"Error obteniendo ticket por ID: {e}")
        return None
