#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API RESTful Mejorada para Belgrano Ahorro
Endpoints completos con múltiples métodos de autenticación
Soporte bilingüe: español e inglés
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from functools import wraps
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint para la API
api_bp = Blueprint('belgrano_api', __name__, url_prefix='/api')

def register_api_blueprint(app):
    """Registrar el blueprint de API en la aplicación Flask"""
    if 'belgrano_api' not in [bp.name for bp in app.blueprints.values()]:
        app.register_blueprint(api_bp)
        logger.info("API blueprint registrado correctamente")
    else:
        logger.info("API blueprint ya estaba registrado")

def require_api_key(f):
    """Decorator mejorado para requerir API key válida con múltiples métodos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        api_key = None
        
        # Método 1: Bearer token en Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header.split(' ')[1]
        
        # Método 2: X-API-Key header
        if not api_key:
            api_key = request.headers.get('X-API-Key')
        
        # Método 3: Query parameter
        if not api_key:
            api_key = request.args.get('api_key')
        
        # Verificar API key
        if not api_key:
            return jsonify({'error': 'API key required', 'methods': ['Bearer token', 'X-API-Key header', 'api_key query param']}), 401
        
        if api_key != expected_api_key:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Obtener conexión a la base de datos (SQLite o PostgreSQL)"""
    # Intentar usar abstracción de base de datos
    try:
        from db_abstraction import get_db_connection as get_db_conn_abstracted
        return get_db_conn_abstracted()
    except ImportError:
        # Fallback a SQLite tradicional
        db_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

@contextmanager
def db_connection():
    """
    Context manager para conexión de base de datos
    Compatible con SQLite y PostgreSQL
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def execute_insert_returning_id(query: str, params: tuple, table_name: str = None):
    """
    Ejecutar INSERT y retornar el ID del registro insertado
    Compatible con SQLite y PostgreSQL
    
    Args:
        query: Query INSERT (puede usar ? para parámetros)
        params: Tupla de parámetros
        table_name: Nombre de la tabla (para PostgreSQL RETURNING)
    
    Returns:
        ID del registro insertado
    """
    database_url = os.getenv('DATABASE_URL', '')
    use_postgres = database_url and (database_url.startswith('postgresql://') or database_url.startswith('postgres://'))
    
    conn = get_db_connection()
    try:
        if use_postgres:
            # PostgreSQL: usar RETURNING para obtener ID
            from sqlalchemy import text
            
            # Convertir ? a :param para PostgreSQL
            adapted_query = query
            param_dict = {}
            if '?' in query and params:
                for i, param in enumerate(params):
                    param_name = f'p{i}'
                    adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                    param_dict[param_name] = param
            
            # Agregar RETURNING si no está
            if 'RETURNING' not in adapted_query.upper():
                # Extraer nombre de tabla del query si no se proporciona
                if not table_name:
                    # Intentar extraer de "INSERT INTO tabla"
                    import re
                    match = re.search(r'INSERT\s+INTO\s+(\w+)', adapted_query, re.IGNORECASE)
                    if match:
                        table_name = match.group(1)
                
                if table_name:
                    adapted_query = adapted_query.rstrip(';') + f' RETURNING {table_name}.id'
            
            result = conn.execute(text(adapted_query), param_dict)
            row = result.fetchone()
            if row:
                inserted_id = row[0] if hasattr(row, '__getitem__') else row.id
                conn.commit()
                return inserted_id
            else:
                conn.commit()
                return None
        else:
            # SQLite: usar cursor tradicional
            cursor = conn.cursor()
            cursor.execute(query, params)
            inserted_id = cursor.lastrowid
            conn.commit()
            return inserted_id
    except Exception as e:
        if use_postgres:
            conn.rollback()
        else:
            conn.rollback()
        logger.error(f"Error en execute_insert_returning_id: {e}")
        raise
    finally:
        conn.close()

def execute_select(query: str, params: tuple = None):
    """
    Ejecutar SELECT y retornar resultados
    Compatible con SQLite y PostgreSQL
    
    Returns:
        Lista de diccionarios con los resultados
    """
    database_url = os.getenv('DATABASE_URL', '')
    use_postgres = database_url and (database_url.startswith('postgresql://') or database_url.startswith('postgres://'))
    
    conn = get_db_connection()
    try:
        if use_postgres:
            from sqlalchemy import text
            
            # Convertir ? a :param si es necesario
            adapted_query = query
            param_dict = {}
            if '?' in query and params:
                for i, param in enumerate(params):
                    param_name = f'p{i}'
                    adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                    param_dict[param_name] = param
            
            result = conn.execute(text(adapted_query), param_dict if param_dict else {})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        else:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def execute_update_delete(query: str, params: tuple = None):
    """
    Ejecutar UPDATE o DELETE
    Compatible con SQLite y PostgreSQL
    
    Returns:
        Número de filas afectadas
    """
    database_url = os.getenv('DATABASE_URL', '')
    use_postgres = database_url and (database_url.startswith('postgresql://') or database_url.startswith('postgres://'))
    
    conn = get_db_connection()
    try:
        if use_postgres:
            from sqlalchemy import text
            
            # Convertir ? a :param si es necesario
            adapted_query = query
            param_dict = {}
            if '?' in query and params:
                for i, param in enumerate(params):
                    param_name = f'p{i}'
                    adapted_query = adapted_query.replace('?', f':{param_name}', 1)
                    param_dict[param_name] = param
            
            result = conn.execute(text(adapted_query), param_dict if param_dict else {})
            conn.commit()
            return result.rowcount
        else:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        if use_postgres:
            conn.rollback()
        else:
            conn.rollback()
        logger.error(f"Error en execute_update_delete: {e}")
        raise
    finally:
        conn.close()

def ensure_tables():
    """Crear tablas requeridas si no existen (compatible SQLite y PostgreSQL)"""
    try:
        # Detectar si estamos usando PostgreSQL
        database_url = os.getenv('DATABASE_URL', '')
        use_postgres = database_url and (database_url.startswith('postgresql://') or database_url.startswith('postgres://'))
        
        conn = get_db_connection()
        
        if use_postgres:
            # PostgreSQL: usar SQL adaptado
            from sqlalchemy import text
            
            # Tabla negocios
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS negocios (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # Tabla categorías (crear antes de productos)
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT,
                    activa BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # Tabla productos
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    store TEXT,
                    precio DECIMAL(10,2) NOT NULL,
                    original_price DECIMAL(10,2),
                    categoria TEXT,
                    imagen TEXT,
                    stock INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 5,
                    negocio_id INTEGER DEFAULT 1,
                    activo BOOLEAN DEFAULT TRUE,
                    destacado BOOLEAN DEFAULT FALSE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            '''))
            
            # Tabla sucursales
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS sucursales (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    negocio_id INTEGER NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            '''))
            
            # Tabla ofertas
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS ofertas (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    descuento DECIMAL(10,2) NOT NULL,
                    fecha_inicio TIMESTAMP,
                    fecha_fin TIMESTAMP,
                    producto_id INTEGER,
                    negocio_id INTEGER,
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (producto_id) REFERENCES productos(id),
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            '''))
            
            conn.commit()
            logger.info("✅ Tablas de API verificadas/creadas en PostgreSQL")
        else:
            # SQLite: usar queries tradicionales
            cursor = conn.cursor()
            
            # Tabla negocios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS negocios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla categorías
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT,
                    activa BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla sucursales
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sucursales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    negocio_id INTEGER NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            ''')
            
            # Tabla productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    store TEXT,
                    precio REAL NOT NULL,
                    original_price REAL,
                    categoria TEXT,
                    imagen TEXT,
                    stock INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 5,
                    negocio_id INTEGER DEFAULT 1,
                    activo BOOLEAN DEFAULT 1,
                    destacado BOOLEAN DEFAULT 0,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            ''')
            
            # Tabla ofertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ofertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    descuento REAL NOT NULL,
                    fecha_inicio TIMESTAMP,
                    fecha_fin TIMESTAMP,
                    producto_id INTEGER,
                    negocio_id INTEGER,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (producto_id) REFERENCES productos(id),
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            ''')
            
            conn.commit()
            logger.info("✅ Tablas de API verificadas/creadas en SQLite")
        
        conn.close()
            
    except Exception as e:
        logger.error(f"Error creando tablas: {e}")
        import traceback
        logger.error(traceback.format_exc())

# =============================
# ENDPOINTS DE NEGOCIOS
# =============================

@api_bp.route('/negocios', methods=['GET'])
@require_api_key
def api_negocios():
    """Obtener lista de negocios"""
    try:
        # Detectar si estamos usando PostgreSQL
        database_url = os.getenv('DATABASE_URL', '')
        use_postgres = database_url and (database_url.startswith('postgresql://') or database_url.startswith('postgres://'))
        
        conn = get_db_connection()
        
        try:
            if use_postgres:
                # PostgreSQL: usar SQLAlchemy
                from sqlalchemy import text
                result = conn.execute(text('''
                    SELECT id, nombre, descripcion, direccion, telefono, email, activo,
                           fecha_creacion, fecha_actualizacion
                    FROM negocios 
                    WHERE activo = TRUE
                    ORDER BY nombre
                '''))
                negocios = [dict(row._mapping) for row in result.fetchall()]
            else:
                # SQLite: usar cursor tradicional
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, nombre, descripcion, direccion, telefono, email, activo,
                           fecha_creacion, fecha_actualizacion
                    FROM negocios 
                    WHERE activo = 1
                    ORDER BY nombre
                ''')
                negocios = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': negocios,
                'total': len(negocios),
                'timestamp': datetime.now().isoformat()
            })
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error in api_negocios: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios', methods=['POST'])
@require_api_key
def api_negocio_create():
    """Crear nuevo negocio"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data:
            return jsonify({'error': 'Nombre es requerido'}), 400
        
        # Aceptar activo (booleano o entero) y convertirlo
        activo = 1
        if 'activo' in data:
            activo = 1 if (data['activo'] is True or data['activo'] == 1 or str(data['activo']).lower() == 'true') else 0
        
        # Usar función helper compatible con SQLite y PostgreSQL
        negocio_id = execute_insert_returning_id(
            '''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                data['nombre'],
                data.get('descripcion', ''),
                data.get('direccion', ''),
                data.get('telefono', ''),
                data.get('email', ''),
                activo
            ),
            table_name='negocios'
        )
        
        if negocio_id:
            return jsonify({
                'status': 'success',
                'message': 'Negocio creado exitosamente',
                'data': {'id': negocio_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear negocio'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_negocio_create: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios/<int:negocio_id>', methods=['GET'])
@require_api_key
def api_negocio_detail(negocio_id):
    """Obtener detalles de un negocio específico"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, descripcion, direccion, telefono, email, activo,
                       fecha_creacion, fecha_actualizacion
                FROM negocios 
                WHERE id = ? AND activo = 1
            ''', (negocio_id,))
            
            negocio = cursor.fetchone()
            if not negocio:
                return jsonify({'error': 'Negocio no encontrado'}), 404
            
            return jsonify({
                'status': 'success',
                'data': dict(negocio),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_negocio_detail: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios/<int:negocio_id>', methods=['PUT'])
@require_api_key
def api_negocio_update(negocio_id):
    """Actualizar negocio existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el negocio existe
            cursor.execute('SELECT id FROM negocios WHERE id = ? AND activo = 1', (negocio_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Negocio no encontrado'}), 404
            
            # Actualizar campos
            update_fields = []
            values = []
            
            for field in ['nombre', 'descripcion', 'direccion', 'telefono', 'email']:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    values.append(data[field])
            
            if not update_fields:
                return jsonify({'error': 'No hay campos para actualizar'}), 400
            
            update_fields.append("fecha_actualizacion = CURRENT_TIMESTAMP")
            values.append(negocio_id)
            
            cursor.execute(f'''
                UPDATE negocios 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', values)
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Negocio actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_negocio_update: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios/<int:negocio_id>', methods=['DELETE'])
@require_api_key
def api_negocio_delete(negocio_id):
    """Eliminar negocio (soft delete)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el negocio existe
            cursor.execute('SELECT id FROM negocios WHERE id = ? AND activo = 1', (negocio_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Negocio no encontrado'}), 404
            
            # Soft delete
            cursor.execute('''
                UPDATE negocios 
                SET activo = 0, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (negocio_id,))
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Negocio eliminado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_negocio_delete: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE PRODUCTOS
# =============================

@api_bp.route('/productos', methods=['GET'])
@require_api_key
def api_productos():
    """Obtener lista de productos"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.id, p.nombre, p.store, p.precio, p.original_price, p.categoria,
                       p.imagen, p.stock, p.stock_minimo, p.negocio_id, p.activo, p.destacado,
                       p.fecha_creacion, p.fecha_actualizacion,
                       n.nombre as negocio_nombre
                FROM productos p
                LEFT JOIN negocios n ON p.negocio_id = n.id
                WHERE p.activo = 1
                ORDER BY p.destacado DESC, p.nombre
            ''')
            
            productos = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': productos,
                'total': len(productos),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_productos: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos', methods=['POST'])
@require_api_key
def api_producto_create():
    """Crear nuevo producto"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'precio' not in data:
            return jsonify({'error': 'Nombre y precio son requeridos'}), 400
        
        # Mapear campos: DevOps puede enviar 'descripcion' -> 'store', 'categoria_id' -> 'categoria'
        store = data.get('store', data.get('descripcion', ''))
        categoria = data.get('categoria', '')
        # Si viene categoria_id, intentar obtener el nombre de la categoría (por ahora usar el ID como string)
        if not categoria and 'categoria_id' in data:
            categoria = str(data['categoria_id'])
        
        # Aceptar activo (booleano o entero) y convertirlo a 1 o 0
        activo = 1
        if 'activo' in data:
            activo = 1 if (data['activo'] is True or data['activo'] == 1 or str(data['activo']).lower() == 'true') else 0
        
        # Usar función helper compatible con SQLite y PostgreSQL
        producto_id = execute_insert_returning_id(
            '''
            INSERT INTO productos (nombre, store, precio, original_price, categoria, imagen, 
                                stock, stock_minimo, negocio_id, activo, destacado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['nombre'],
                store,
                float(data['precio']),
                float(data.get('original_price', data['precio'])),
                categoria,
                data.get('imagen', ''),
                int(data.get('stock', 0)),
                int(data.get('stock_minimo', 5)),
                int(data.get('negocio_id', 1)),
                activo,
                int(data.get('destacado', 0))
            ),
            table_name='productos'
        )
        
        if producto_id:
            return jsonify({
                'status': 'success',
                'message': 'Producto creado exitosamente',
                'data': {'id': producto_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear producto'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_producto_create: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos/<int:producto_id>', methods=['GET'])
@require_api_key
def api_producto_detail(producto_id):
    """Obtener detalles de un producto específico"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.id, p.nombre, p.store, p.precio, p.original_price, p.categoria,
                       p.imagen, p.stock, p.stock_minimo, p.negocio_id, p.activo, p.destacado,
                       p.fecha_creacion, p.fecha_actualizacion,
                       n.nombre as negocio_nombre
                FROM productos p
                LEFT JOIN negocios n ON p.negocio_id = n.id
                WHERE p.id = ? AND p.activo = 1
            ''', (producto_id,))
            
            producto = cursor.fetchone()
            if not producto:
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            return jsonify({
                'status': 'success',
                'data': dict(producto),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_producto_detail: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos/<int:producto_id>', methods=['PUT'])
@require_api_key
def api_producto_update(producto_id):
    """Actualizar producto existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el producto existe
            cursor.execute('SELECT id FROM productos WHERE id = ? AND activo = 1', (producto_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            # Actualizar campos
            update_fields = []
            values = []
            
            for field in ['nombre', 'store', 'precio', 'original_price', 'categoria', 'imagen', 
                         'stock', 'stock_minimo', 'negocio_id', 'activo', 'destacado']:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    values.append(data[field])
            
            if not update_fields:
                return jsonify({'error': 'No hay campos para actualizar'}), 400
            
            update_fields.append("fecha_actualizacion = CURRENT_TIMESTAMP")
            values.append(producto_id)
            
            cursor.execute(f'''
                UPDATE productos 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', values)
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Producto actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_producto_update: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos/<int:producto_id>', methods=['DELETE'])
@require_api_key
def api_producto_delete(producto_id):
    """Eliminar producto (soft delete)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el producto existe
            cursor.execute('SELECT id FROM productos WHERE id = ? AND activo = 1', (producto_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            # Soft delete
            cursor.execute('''
                UPDATE productos 
                SET activo = 0, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (producto_id,))
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Producto eliminado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_producto_delete: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE CATEGORÍAS (NUEVO)
# =============================

@api_bp.route('/categorias', methods=['GET'])
@require_api_key
def api_categorias():
    """Obtener lista de categorías"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, descripcion, activa, fecha_creacion
                FROM categorias 
                WHERE activa = 1
                ORDER BY nombre
            ''')
            
            categorias = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': categorias,
                'total': len(categorias),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_categorias: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/categorias', methods=['POST'])
@require_api_key
def api_categoria_create():
    """Crear nueva categoría"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data:
            return jsonify({'error': 'Nombre es requerido'}), 400
        
        # Usar función helper compatible con SQLite y PostgreSQL
        categoria_id = execute_insert_returning_id(
            '''
            INSERT INTO categorias (nombre, descripcion)
            VALUES (?, ?)
            ''',
            (
                data['nombre'],
                data.get('descripcion', '')
            ),
            table_name='categorias'
        )
        
        if categoria_id:
            return jsonify({
                'status': 'success',
                'message': 'Categoría creada exitosamente',
                'data': {'id': categoria_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear categoría'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_categoria_create: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE OFERTAS
# =============================

@api_bp.route('/ofertas', methods=['GET'])
@require_api_key
def api_ofertas():
    """Obtener lista de ofertas"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT o.id, o.nombre, o.descripcion, o.descuento, o.fecha_inicio, o.fecha_fin,
                       o.producto_id, o.negocio_id, o.activo, o.fecha_creacion, o.fecha_actualizacion,
                       p.nombre as producto_nombre, n.nombre as negocio_nombre
                FROM ofertas o
                LEFT JOIN productos p ON o.producto_id = p.id
                LEFT JOIN negocios n ON o.negocio_id = n.id
                WHERE o.activo = 1
                ORDER BY o.fecha_inicio DESC
            ''')
            
            ofertas = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': ofertas,
                'total': len(ofertas),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_ofertas: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ofertas', methods=['POST'])
@require_api_key
def api_oferta_create():
    """Crear nueva oferta"""
    try:
        data = request.get_json()
        # Aceptar tanto 'nombre' como 'titulo' (DevOps envía 'titulo')
        nombre_oferta = data.get('nombre') or data.get('titulo')
        if not nombre_oferta or 'descuento' not in data:
            return jsonify({'error': 'Nombre/titulo y descuento son requeridos'}), 400
        
        # Aceptar activa (booleano) o activo (entero) y convertirlo a 1 o 0
        activo = 1
        if 'activa' in data:
            activo = 1 if (data['activa'] is True or data['activa'] == 1 or str(data['activa']).lower() == 'true') else 0
        elif 'activo' in data:
            activo = 1 if (data['activo'] is True or data['activo'] == 1 or str(data['activo']).lower() == 'true') else 0
        
        # Obtener negocio_id del producto si no viene directamente
        negocio_id = data.get('negocio_id')
        if not negocio_id and data.get('producto_id'):
            try:
                resultados = execute_select('SELECT negocio_id FROM productos WHERE id = ?', (data['producto_id'],))
                if resultados:
                    negocio_id = resultados[0]['negocio_id']
            except Exception:
                pass  # Si falla, negocio_id queda None
        
        # Usar función helper compatible con SQLite y PostgreSQL
        oferta_id = execute_insert_returning_id(
            '''
            INSERT INTO ofertas (nombre, descripcion, descuento, fecha_inicio, fecha_fin,
                              producto_id, negocio_id, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                nombre_oferta,
                data.get('descripcion', ''),
                float(data['descuento']),
                data.get('fecha_inicio'),
                data.get('fecha_fin'),
                data.get('producto_id'),
                negocio_id,
                activo
            ),
            table_name='ofertas'
        )
        
        if oferta_id:
            return jsonify({
                'status': 'success',
                'message': 'Oferta creada exitosamente',
                'data': {'id': oferta_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear oferta'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_oferta_create: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE SUCURSALES
# =============================

@api_bp.route('/sucursales', methods=['GET'])
@require_api_key
def api_sucursales():
    """Obtener lista de sucursales"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.id, s.nombre, s.direccion, s.telefono, s.email, s.negocio_id, s.activo,
                       s.fecha_creacion, s.fecha_actualizacion, n.nombre as negocio_nombre
                FROM sucursales s
                LEFT JOIN negocios n ON s.negocio_id = n.id
                WHERE s.activo = 1
                ORDER BY s.nombre
            ''')
            
            sucursales = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': sucursales,
                'total': len(sucursales),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_sucursales: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sucursales', methods=['POST'])
@require_api_key
def api_sucursal_create():
    """Crear nueva sucursal"""
    try:
        data = request.get_json()
        if not data or 'nombre' not in data or 'negocio_id' not in data:
            return jsonify({'error': 'Nombre y negocio_id son requeridos'}), 400
        
        # Usar función helper compatible con SQLite y PostgreSQL
        sucursal_id = execute_insert_returning_id(
            '''
            INSERT INTO sucursales (nombre, direccion, telefono, email, negocio_id)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                data['nombre'],
                data.get('direccion', ''),
                data.get('telefono', ''),
                data.get('email', ''),
                data['negocio_id']
            ),
            table_name='sucursales'
        )
        
        if sucursal_id:
            return jsonify({
                'status': 'success',
                'message': 'Sucursal creada exitosamente',
                'data': {'id': sucursal_id},
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({'error': 'Error al crear sucursal'}), 500
            
    except Exception as e:
        logger.error(f"Error in api_sucursal_create: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE PRECIOS
# =============================

@api_bp.route('/precios', methods=['GET'])
@require_api_key
def api_precios_list():
    """Obtener lista de precios"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.id as producto_id, p.nombre as producto_nombre, p.precio, p.original_price,
                       p.categoria, n.nombre as negocio_nombre
                FROM productos p
                LEFT JOIN negocios n ON p.negocio_id = n.id
                WHERE p.activo = 1
                ORDER BY p.categoria, p.nombre
            ''')
            
            precios = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': precios,
                'total': len(precios),
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_precios_list: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/precios/<int:producto_id>', methods=['PUT'])
@require_api_key
def api_precios_update(producto_id):
    """Actualizar precio de producto"""
    try:
        data = request.get_json()
        if not data or 'precio' not in data:
            return jsonify({'error': 'Precio es requerido'}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el producto existe
            cursor.execute('SELECT id FROM productos WHERE id = ? AND activo = 1', (producto_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            # Actualizar precio
            cursor.execute('''
                UPDATE productos 
                SET precio = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (data['precio'], producto_id))
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Precio actualizado exitosamente',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_precios_update: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS V1 (COMPATIBILIDAD)
# =============================

# Crear endpoints v1 que redirijan a los endpoints principales
@api_bp.route('/v1/negocios', methods=['GET', 'POST'])
@require_api_key
def api_v1_negocios():
    """Endpoint v1 para negocios"""
    if request.method == 'GET':
        return api_negocios()
    else:
        return api_negocio_create()

@api_bp.route('/v1/negocios/<int:negocio_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_v1_negocio_detail(negocio_id):
    """Endpoint v1 para detalle de negocio"""
    if request.method == 'GET':
        return api_negocio_detail(negocio_id)
    elif request.method == 'PUT':
        return api_negocio_update(negocio_id)
    else:
        return api_negocio_delete(negocio_id)

@api_bp.route('/v1/productos', methods=['GET', 'POST'])
@require_api_key
def api_v1_productos():
    """Endpoint v1 para productos"""
    if request.method == 'GET':
        return api_productos()
    else:
        return api_producto_create()

@api_bp.route('/v1/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_v1_producto_detail(producto_id):
    """Endpoint v1 para detalle de producto"""
    if request.method == 'GET':
        return api_producto_detail(producto_id)
    elif request.method == 'PUT':
        return api_producto_update(producto_id)
    else:
        return api_producto_delete(producto_id)

@api_bp.route('/v1/categorias', methods=['GET', 'POST'])
@require_api_key
def api_v1_categorias():
    """Endpoint v1 para categorías"""
    if request.method == 'GET':
        return api_categorias()
    else:
        return api_categoria_create()

@api_bp.route('/v1/ofertas', methods=['GET', 'POST'])
@require_api_key
def api_v1_ofertas():
    """Endpoint v1 para ofertas"""
    if request.method == 'GET':
        return api_ofertas()
    else:
        return api_oferta_create()

@api_bp.route('/v1/sucursales', methods=['GET', 'POST'])
@require_api_key
def api_v1_sucursales():
    """Endpoint v1 para sucursales"""
    if request.method == 'GET':
        return api_sucursales()
    else:
        return api_sucursal_create()

@api_bp.route('/v1/precios', methods=['GET'])
@require_api_key
def api_v1_precios():
    """Endpoint v1 para precios"""
    return api_precios_list()

@api_bp.route('/v1/precios/<int:producto_id>', methods=['PUT'])
@require_api_key
def api_v1_precios_update(producto_id):
    """Endpoint v1 para actualizar precios"""
    return api_precios_update(producto_id)

# =============================
# ALIAS EN INGLÉS (COMPATIBILIDAD)
# =============================

# Negocios
api_bp.add_url_rule('/businesses', view_func=api_negocios, methods=['GET', 'POST'])
api_bp.add_url_rule('/businesses/<int:negocio_id>', view_func=api_negocio_detail, methods=['GET', 'PUT', 'DELETE'])

# Sucursales
api_bp.add_url_rule('/branches', view_func=api_sucursales, methods=['GET', 'POST'])
api_bp.add_url_rule('/branches/<int:sucursal_id>', view_func=api_sucursales, methods=['GET', 'PUT', 'DELETE'])

# Productos
api_bp.add_url_rule('/products', view_func=api_productos, methods=['GET', 'POST'])
api_bp.add_url_rule('/products/<int:producto_id>', view_func=api_producto_detail, methods=['GET', 'PUT', 'DELETE'])

# Ofertas
api_bp.add_url_rule('/offers', view_func=api_ofertas, methods=['GET', 'POST'])
api_bp.add_url_rule('/offers/<int:oferta_id>', view_func=api_ofertas, methods=['GET', 'PUT', 'DELETE'])

# Precios
api_bp.add_url_rule('/prices', view_func=api_precios_list, methods=['GET'])
api_bp.add_url_rule('/prices/<int:producto_id>', view_func=api_precios_update, methods=['PUT'])

# Categorías
api_bp.add_url_rule('/categories', view_func=api_categorias, methods=['GET', 'POST'])

# =============================
# ENDPOINTS DE UTILIDAD
# =============================

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Belgrano Ahorro API is running',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'negocios': '/api/negocios',
            'productos': '/api/productos',
            'categorias': '/api/categorias',
            'ofertas': '/api/ofertas',
            'sucursales': '/api/sucursales',
            'precios': '/api/precios',
            'v1': '/api/v1/*'
        }
    })

@api_bp.route('/status', methods=['GET'])
@require_api_key
def api_status():
    """Status detallado de la API"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Contar registros
            cursor.execute('SELECT COUNT(*) FROM negocios WHERE activo = 1')
            negocios_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM productos WHERE activo = 1')
            productos_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM categorias WHERE activa = 1')
            categorias_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM ofertas WHERE activo = 1')
            ofertas_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM sucursales WHERE activo = 1')
            sucursales_count = cursor.fetchone()[0]
            
            return jsonify({
                'status': 'success',
                'api_version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'database': {
                    'negocios': negocios_count,
                    'productos': productos_count,
                    'categorias': categorias_count,
                    'ofertas': ofertas_count,
                    'sucursales': sucursales_count
                },
                'authentication': {
                    'methods': ['Bearer token', 'X-API-Key header', 'api_key query param'],
                    'required': True
                }
            })
            
    except Exception as e:
        logger.error(f"Error in api_status: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE COMPRAS/PEDIDOS
# =============================

@api_bp.route('/compras', methods=['POST'])
@require_api_key
def api_crear_compra():
    """Crear una nueva compra con validación de stock"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Validar campos requeridos
        required_fields = ['usuario_id', 'items', 'metodo_pago', 'direccion_entrega']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        items = data['items']
        if not items or not isinstance(items, list):
            return jsonify({'error': 'Items debe ser una lista no vacía'}), 400
        
        # Importar funciones de validación de stock
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import db as database
        
        # Validar stock para todos los items
        items_para_validar = []
        for item in items:
            if 'producto_id' not in item or 'cantidad' not in item:
                return jsonify({'error': 'Cada item debe tener producto_id y cantidad'}), 400
            items_para_validar.append({
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad']
            })
        
        stock_valido, errores_stock, productos_validos = database.validar_stock_carrito(items_para_validar)
        
        if not stock_valido:
            return jsonify({
                'error': 'Stock insuficiente',
                'detalles': errores_stock
            }), 400
        
        # Calcular total
        total = 0
        carrito_items = []
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for item in items:
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                
                cursor.execute('''
                    SELECT id, nombre, precio FROM productos 
                    WHERE id = ? AND activo = 1
                ''', (producto_id,))
                producto = cursor.fetchone()
                
                if not producto:
                    return jsonify({'error': f'Producto {producto_id} no encontrado'}), 404
                
                precio = producto['precio']
                subtotal = precio * cantidad
                total += subtotal
                
                carrito_items.append({
                    'producto_id': producto_id,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal
                })
        
        # Generar número de pedido
        numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{data['usuario_id']}"
        
        # Guardar pedido
        pedido_id = database.guardar_pedido(
            usuario_id=data['usuario_id'],
            numero_pedido=numero_pedido,
            total=total,
            metodo_pago=data['metodo_pago'],
            direccion_entrega=data['direccion_entrega'],
            notas=data.get('notas', '')
        )
        
        if not pedido_id:
            return jsonify({'error': 'Error al crear el pedido'}), 500
        
        # Guardar items del pedido
        items_db = []
        for item in carrito_items:
            items_db.append({
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'subtotal': item['subtotal']
            })
        
        database.guardar_items_pedido(pedido_id, items_db)
        
        # Actualizar stock
        stock_actualizado, resultados_stock, errores_stock = database.actualizar_stock_carrito(items_para_validar)
        
        if not stock_actualizado:
            logger.error(f"Error actualizando stock después de compra: {errores_stock}")
            # El pedido ya está guardado, pero registrar el error
        
        # Intentar enviar a Ticketera si está configurado
        ticket_creado = None
        try:
            ticketera_url = os.getenv('TICKETERA_URL', '')
            if ticketera_url:
                # Obtener datos del usuario
                with get_db_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM usuarios WHERE id = ?', (data['usuario_id'],))
                    usuario_row = cursor.fetchone()
                    
                    if usuario_row:
                        usuario = dict(usuario_row)
                        # Preparar datos para Ticketera
                        productos_lista = []
                        for item in carrito_items:
                            cursor.execute('SELECT nombre FROM productos WHERE id = ?', (item['producto_id'],))
                            prod = cursor.fetchone()
                            productos_lista.append({
                                'id': item['producto_id'],
                                'nombre': prod['nombre'] if prod else 'Producto',
                                'precio': item['precio_unitario'],
                                'cantidad': item['cantidad']
                            })
                        
                        # Enviar a Ticketera
                        import requests
                        ticket_data = {
                            'numero': numero_pedido,
                            'cliente_nombre': f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip() or usuario.get('email', 'Cliente'),
                            'cliente_direccion': data['direccion_entrega'],
                            'cliente_telefono': usuario.get('telefono', ''),
                            'cliente_email': usuario.get('email', ''),
                            'productos': json.dumps(productos_lista),
                            'total': total,
                            'estado': 'pendiente',
                            'prioridad': 'normal'
                        }
                        
                        response = requests.post(
                            f"{ticketera_url.rstrip('/')}/api/tickets",
                            json=ticket_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=10
                        )
                        
                        if response.status_code == 201:
                            ticket_creado = response.json()
                            logger.info(f"✅ Ticket creado en Ticketera para pedido {numero_pedido}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo enviar a Ticketera: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Compra realizada exitosamente',
            'data': {
                'pedido_id': pedido_id,
                'numero_pedido': numero_pedido,
                'total': total,
                'items': carrito_items,
                'stock_actualizado': stock_actualizado,
                'ticket_creado': ticket_creado is not None
            },
            'timestamp': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error in api_crear_compra: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/compras/<int:pedido_id>', methods=['GET'])
@require_api_key
def api_obtener_compra(pedido_id):
    """Obtener detalles de una compra"""
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obtener pedido
            cursor.execute('''
                SELECT p.*, u.email, u.nombre, u.apellido
                FROM pedidos p
                LEFT JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.id = ?
            ''', (pedido_id,))
            
            pedido = cursor.fetchone()
            if not pedido:
                return jsonify({'error': 'Pedido no encontrado'}), 404
            
            # Obtener items del pedido
            cursor.execute('''
                SELECT pi.*, pr.nombre as producto_nombre
                FROM pedido_items pi
                LEFT JOIN productos pr ON pi.producto_id = pr.id
                WHERE pi.pedido_id = ?
            ''', (pedido_id,))
            
            items = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'status': 'success',
                'data': {
                    'pedido': dict(pedido),
                    'items': items
                },
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error in api_obtener_compra: {e}")
        return jsonify({'error': str(e)}), 500

# Inicializar tablas al importar el módulo
ensure_tables()
