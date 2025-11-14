#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de base de datos PostgreSQL
Todas las funciones usan PostgreSQL - NO hay SQLite
"""

import hashlib
import secrets
import logging
from datetime import datetime
from sqlalchemy import text

# Importar conexión a PostgreSQL
try:
    from db_abstraction import get_db_connection, engine
except ImportError:
    raise ImportError("[DB] No se pudo importar db_abstraction. Asegúrate de que esté configurado correctamente.")

logger = logging.getLogger(__name__)

# ==========================================
# FUNCIONES DE USUARIOS
# ==========================================

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
    except Exception as e:
        logger.warning(f"[DB] Error verificando contraseña: {e}")
        return False

def crear_usuario(nombre, apellido, email, password, telefono=None, direccion=None, rol='cliente'):
    """Crear un nuevo usuario en PostgreSQL"""
    try:
        session = get_db_connection()
        try:
            # Verificar si el email ya existe
            result = session.execute(text('SELECT id FROM usuarios WHERE email = :email'), {'email': email})
            if result.fetchone():
                return {'exito': False, 'mensaje': 'El email ya está registrado'}
            
            # Crear hash de la contraseña
            password_hash = hash_password(password)
            
            # Insertar usuario
            result = session.execute(text('''
                INSERT INTO usuarios (nombre, apellido, email, password_hash, telefono, activo)
                VALUES (:nombre, :apellido, :email, :password_hash, :telefono, TRUE)
                RETURNING id
            '''), {
                'nombre': f"{nombre} {apellido}".strip(),
                'apellido': apellido or '',
                'email': email,
                'password_hash': password_hash,
                'telefono': telefono
            })
            
            row = result.fetchone()
            usuario_id = row[0] if row else None
            session.commit()
            
            logger.info(f"[DB] ✅ Usuario creado: {email} (ID: {usuario_id})")
            return {'exito': True, 'usuario_id': usuario_id, 'mensaje': 'Usuario creado exitosamente'}
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error creando usuario: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'exito': False, 'mensaje': f'Error al crear usuario: {str(e)}'}
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error en crear_usuario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'exito': False, 'mensaje': f'Error al crear usuario: {str(e)}'}

def verificar_usuario(email, password):
    """Verificar credenciales de usuario"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT id, nombre, email, password_hash, activo
                FROM usuarios 
                WHERE email = :email
            '''), {'email': email})
            
            usuario = result.fetchone()
            if usuario and verificar_password(password, usuario[3]):
                return {
                    'exito': True, 
                    'usuario': {
                        'id': usuario[0], 
                        'nombre': usuario[1] or '', 
                        'email': usuario[2]
                    }
                }
            else:
                return {'exito': False, 'mensaje': 'Credenciales incorrectas'}
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error verificando usuario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'exito': False, 'mensaje': 'Error interno del servidor'}

def buscar_usuario_por_email(email):
    """Buscar usuario por email"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT id, nombre, email, telefono, activo
                FROM usuarios 
                WHERE email = :email
            '''), {'email': email})
            
            usuario = result.fetchone()
            if usuario:
                return {
                    'id': usuario[0],
                    'nombre': usuario[1] or '',
                    'email': usuario[2],
                    'telefono': usuario[3] or '',
                    'activo': bool(usuario[4])
                }
            return None
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error buscando usuario: {e}")
        return None

def obtener_usuario_por_id(usuario_id):
    """Obtener usuario por ID"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT id, nombre, email, telefono, activo, fecha_creacion
                FROM usuarios 
                WHERE id = :id
            '''), {'id': usuario_id})
            
            usuario = result.fetchone()
            if usuario:
                return {
                    'id': usuario[0],
                    'nombre': usuario[1] or '',
                    'email': usuario[2],
                    'telefono': usuario[3] or '',
                    'activo': bool(usuario[4]),
                    'fecha_registro': str(usuario[5]) if usuario[5] else None
                }
            return None
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error obteniendo usuario por ID: {e}")
        return None

def actualizar_usuario(usuario_id, nombre, telefono, direccion):
    """Actualizar información del usuario"""
    try:
        session = get_db_connection()
        try:
            session.execute(text('''
                UPDATE usuarios 
                SET nombre = :nombre, telefono = :telefono, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {
                'id': usuario_id,
                'nombre': nombre,
                'telefono': telefono
            })
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error actualizando usuario: {e}")
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error actualizando usuario: {e}")
        return False

def cambiar_password(usuario_id, password_actual, password_nuevo):
    """Cambiar contraseña del usuario"""
    try:
        session = get_db_connection()
        try:
            # Verificar password actual
            result = session.execute(text('SELECT password_hash FROM usuarios WHERE id = :id'), {'id': usuario_id})
            usuario = result.fetchone()
            if not usuario or not verificar_password(password_actual, usuario[0]):
                return False
            
            # Cambiar password
            password_hash = hash_password(password_nuevo)
            session.execute(text('''
                UPDATE usuarios 
                SET password_hash = :password_hash, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {'id': usuario_id, 'password_hash': password_hash})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error cambiando password: {e}")
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error cambiando password: {e}")
        return False

# ==========================================
# FUNCIONES DE RECUPERACIÓN DE CONTRASEÑA
# ==========================================

def guardar_token_recuperacion(usuario_id, token, expiracion):
    """Guardar token de recuperación"""
    try:
        session = get_db_connection()
        try:
            # Crear tabla si no existe
            session.execute(text('''
                CREATE TABLE IF NOT EXISTS tokens_recuperacion (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expiracion TIMESTAMP NOT NULL,
                    usado BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            '''))
            
            session.execute(text('''
                INSERT INTO tokens_recuperacion (usuario_id, token, expiracion)
                VALUES (:usuario_id, :token, :expiracion)
            '''), {
                'usuario_id': usuario_id,
                'token': token,
                'expiracion': expiracion
            })
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error guardando token: {e}")
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error guardando token: {e}")
        return False

def verificar_token_recuperacion(email, token):
    """Verificar token de recuperación"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT t.id, t.usuario_id, t.expiracion, t.usado
                FROM tokens_recuperacion t
                JOIN usuarios u ON t.usuario_id = u.id
                WHERE u.email = :email AND t.token = :token
            '''), {'email': email, 'token': token})
            
            row = result.fetchone()
            if row and not row[3]:
                return {'exito': True, 'token_id': row[0], 'usuario_id': row[1]}
            return {'exito': False, 'mensaje': 'Token inválido o expirado'}
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error verificando token: {e}")
        return {'exito': False, 'mensaje': 'Error interno'}

def cambiar_password_por_token(email, token_id, nueva_password):
    """Cambiar password usando token"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT u.id
                FROM usuarios u
                JOIN tokens_recuperacion t ON u.id = t.usuario_id
                WHERE t.id = :token_id AND u.email = :email
            '''), {'token_id': token_id, 'email': email})
            
            row = result.fetchone()
            if not row:
                return False
            
            usuario_id = row[0]
            password_hash = hash_password(nueva_password)
            
            session.execute(text('UPDATE usuarios SET password_hash = :password_hash WHERE id = :id'), {
                'password_hash': password_hash,
                'id': usuario_id
            })
            session.execute(text('UPDATE tokens_recuperacion SET usado = TRUE WHERE id = :id'), {'id': token_id})
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error cambiando password por token: {e}")
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error cambiando password por token: {e}")
        return False

# ==========================================
# FUNCIONES DE PEDIDOS
# ==========================================

def guardar_pedido(usuario_id, numero_pedido, total, metodo_pago, direccion_entrega, notas):
    """Guardar un nuevo pedido"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                INSERT INTO pedidos (usuario_id, numero_pedido, total, metodo_pago, direccion_entrega, notas)
                VALUES (:usuario_id, :numero_pedido, :total, :metodo_pago, :direccion_entrega, :notas)
                RETURNING id
            '''), {
                'usuario_id': usuario_id,
                'numero_pedido': numero_pedido,
                'total': total,
                'metodo_pago': metodo_pago,
                'direccion_entrega': direccion_entrega,
                'notas': notas
            })
            
            row = result.fetchone()
            pedido_id = row[0] if row else None
            session.commit()
            return pedido_id
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error guardando pedido: {e}")
            return None
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error guardando pedido: {e}")
        return None

def guardar_items_pedido(pedido_id, items):
    """Guardar items de un pedido"""
    try:
        session = get_db_connection()
        try:
            for item in items:
                session.execute(text('''
                    INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (:pedido_id, :producto_id, :cantidad, :precio_unitario, :subtotal)
                '''), {
                    'pedido_id': pedido_id,
                    'producto_id': item['producto_id'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario'],
                    'subtotal': item['subtotal']
                })
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error guardando items de pedido: {e}")
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error guardando items de pedido: {e}")
        return False

def obtener_pedidos_usuario(usuario_id):
    """Obtener todos los pedidos de un usuario"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT id, numero_pedido, fecha_creacion, total, estado
                FROM pedidos 
                WHERE usuario_id = :usuario_id
                ORDER BY fecha_creacion DESC
            '''), {'usuario_id': usuario_id})
            
            pedidos = []
            for row in result.fetchall():
                pedidos.append({
                    'id': row[0],
                    'numero_pedido': row[1],
                    'fecha': str(row[2]) if row[2] else '',
                    'total': float(row[3]) if row[3] else 0.0,
                    'estado': row[4] or 'pendiente'
                })
            return pedidos
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error obteniendo pedidos: {e}")
        return []

def obtener_pedido_completo(pedido_id):
    """Obtener un pedido completo con sus items"""
    try:
        session = get_db_connection()
        try:
            # Obtener pedido
            result = session.execute(text('''
                SELECT id, numero_pedido, fecha_creacion, total, estado, metodo_pago, direccion_entrega, notas
                FROM pedidos 
                WHERE id = :id
            '''), {'id': pedido_id})
            
            pedido_row = result.fetchone()
            if not pedido_row:
                return None
            
            pedido = {
                'id': pedido_row[0],
                'numero_pedido': pedido_row[1],
                'fecha': str(pedido_row[2]) if pedido_row[2] else '',
                'total': float(pedido_row[3]) if pedido_row[3] else 0.0,
                'estado': pedido_row[4] or 'pendiente',
                'metodo_pago': pedido_row[5] or '',
                'direccion_entrega': pedido_row[6] or '',
                'notas': pedido_row[7] or '',
                'items': []
            }
            
            # Obtener items del pedido
            result = session.execute(text('''
                SELECT pi.producto_id, pi.cantidad, pi.precio_unitario, pi.subtotal, p.nombre, p.imagen
                FROM items_pedido pi
                JOIN productos p ON pi.producto_id = p.id
                WHERE pi.pedido_id = :pedido_id
            '''), {'pedido_id': pedido_id})
            
            for row in result.fetchall():
                pedido['items'].append({
                    'producto_id': row[0],
                    'cantidad': row[1],
                    'precio_unitario': float(row[2]) if row[2] else 0.0,
                    'subtotal': float(row[3]) if row[3] else 0.0,
                    'nombre': row[4] or '',
                    'imagen': row[5] or ''
                })
            
            return pedido
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error obteniendo pedido completo: {e}")
        return None

def generar_numero_pedido():
    """Generar número único de pedido"""
    import uuid
    fecha = datetime.now().strftime("%Y%m%d")
    codigo = str(uuid.uuid4())[:8].upper()
    return f"PED-{fecha}-{codigo}"

# ==========================================
# FUNCIONES DE STOCK
# ==========================================

def validar_stock_producto(producto_id, cantidad_solicitada):
    """Validar si hay stock suficiente para un producto"""
    try:
        session = get_db_connection()
        try:
            result = session.execute(text('''
                SELECT stock FROM productos 
                WHERE id = :id AND activo = TRUE
            '''), {'id': producto_id})
            
            row = result.fetchone()
            if not row:
                return False, 'Producto no encontrado o inactivo'
            
            stock_disponible = int(row[0]) if row[0] else 0
            if stock_disponible < cantidad_solicitada:
                return False, f'Stock insuficiente. Disponible: {stock_disponible}, Solicitado: {cantidad_solicitada}'
            
            return True, stock_disponible
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error validando stock: {e}")
        return False, f'Error al validar stock: {str(e)}'

def validar_stock_carrito(carrito_items):
    """Validar stock para todos los items del carrito"""
    errores = []
    productos_validos = []
    
    for item in carrito_items:
        producto_id = item.get('producto_id') or item.get('producto', {}).get('id')
        cantidad = item.get('cantidad', 0)
        
        if not producto_id:
            errores.append('Producto sin ID válido')
            continue
        
        valido, resultado = validar_stock_producto(producto_id, cantidad)
        if not valido:
            producto_nombre = item.get('producto', {}).get('nombre', f'Producto ID {producto_id}')
            errores.append(f'{producto_nombre}: {resultado}')
        else:
            productos_validos.append({
                'producto_id': producto_id,
                'cantidad': cantidad,
                'stock_disponible': resultado
            })
    
    return len(errores) == 0, errores, productos_validos

def actualizar_stock_producto(producto_id, cantidad_vendida):
    """Actualizar stock de un producto después de una venta"""
    try:
        session = get_db_connection()
        try:
            # Verificar stock actual
            result = session.execute(text('SELECT stock FROM productos WHERE id = :id'), {'id': producto_id})
            row = result.fetchone()
            
            if not row:
                return False, 'Producto no encontrado'
            
            stock_actual = int(row[0]) if row[0] else 0
            nuevo_stock = max(0, stock_actual - cantidad_vendida)
            
            # Actualizar stock
            session.execute(text('''
                UPDATE productos 
                SET stock = :stock, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = :id
            '''), {'stock': nuevo_stock, 'id': producto_id})
            
            session.commit()
            logger.info(f"[DB] ✅ Stock actualizado: Producto {producto_id} - Stock anterior: {stock_actual}, Vendido: {cantidad_vendida}, Nuevo stock: {nuevo_stock}")
            return True, nuevo_stock
        except Exception as e:
            session.rollback()
            logger.error(f"[DB] ❌ Error actualizando stock: {e}")
            return False, f'Error al actualizar stock: {str(e)}'
        finally:
            session.close()
    except Exception as e:
        logger.error(f"[DB] ❌ Error actualizando stock: {e}")
        return False, f'Error al actualizar stock: {str(e)}'

def actualizar_stock_carrito(carrito_items):
    """Actualizar stock para todos los items del carrito"""
    resultados = []
    errores = []
    
    for item in carrito_items:
        producto_id = item.get('producto_id') or item.get('producto', {}).get('id')
        cantidad = item.get('cantidad', 0)
        
        if not producto_id:
            errores.append('Producto sin ID válido')
            continue
        
        exito, resultado = actualizar_stock_producto(producto_id, cantidad)
        if exito:
            resultados.append({
                'producto_id': producto_id,
                'cantidad_vendida': cantidad,
                'nuevo_stock': resultado
            })
        else:
            errores.append(f'Producto {producto_id}: {resultado}')
    
    return len(errores) == 0, resultados, errores

# ==========================================
# FUNCIONES DEPRECADAS (mantener compatibilidad)
# ==========================================

def inicializar_base_datos():
    """DEPRECATED: Usar init_db() de init_db.py"""
    logger.warning("[DB] inicializar_base_datos() está deprecado. Use init_db() de init_db.py")
    try:
        from init_db import init_db
        init_db()
    except ImportError:
        logger.error("[DB] No se pudo importar init_db")

def crear_base_datos():
    """DEPRECATED: Usar init_db() de init_db.py"""
    logger.warning("[DB] crear_base_datos() está deprecado. Use init_db() de init_db.py")
    try:
        from init_db import init_db
        init_db()
    except ImportError:
        logger.error("[DB] No se pudo importar init_db")
