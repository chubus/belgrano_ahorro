#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API RESTful para Belgrano Ahorro
Endpoints completos para comunicación con DevOps
Soporte bilingüe: español e inglés
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from functools import wraps

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
    """Decorator para requerir API key válida"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener API key del header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header required'}), 401
        
        api_key = auth_header.split(' ')[1]
        expected_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', 'belgrano_ahorro_api_key_2025')
        
        if api_key != expected_api_key:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Obtener conexión a la base de datos"""
    db_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
    return sqlite3.connect(db_path)

def ensure_tables():
    """Crear tablas requeridas si no existen"""
    try:
        with get_db_connection() as conn:
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
                    descripcion TEXT,
                    precio REAL NOT NULL,
                    categoria TEXT,
                    stock INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 0,
                    negocio_id INTEGER,
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (negocio_id) REFERENCES negocios(id)
                )
            ''')
            
            # Tabla ofertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ofertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    descuento_porcentaje REAL DEFAULT 0.0,
                    descuento_fijo REAL DEFAULT 0.0,
                    activa BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla precios_historial
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS precios_historial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    precio_anterior REAL NOT NULL,
                    precio_nuevo REAL NOT NULL,
                    motivo TEXT,
                    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            ''')
            
            # Insertar datos de ejemplo si las tablas están vacías
            cursor.execute('SELECT COUNT(*) FROM negocios')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo)
                    VALUES ('Negocio Ejemplo', 'Descripción del negocio', 'Dirección ejemplo', '123456789', 'ejemplo@email.com', 1)
                ''')
            
            cursor.execute('SELECT COUNT(*) FROM productos')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO productos (nombre, descripcion, precio, categoria, stock, negocio_id, activo)
                    VALUES ('Producto Ejemplo', 'Descripción del producto', 100.0, 'Categoría', 10, 1, 1)
                ''')
            
            cursor.execute('SELECT COUNT(*) FROM sucursales')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO sucursales (nombre, direccion, telefono, email, negocio_id, activo)
                    VALUES ('Sucursal Ejemplo', 'Dirección sucursal', '987654321', 'sucursal@email.com', 1, 1)
                ''')
            
            conn.commit()
            logger.info("Tablas verificadas/creadas correctamente con datos de ejemplo")
            return True
    except Exception as e:
        logger.error(f"Error asegurando tablas: {e}")
        return False

# Garantizar tablas al importar el módulo
ensure_tables()

# =============================
# ENDPOINTS DE NEGOCIOS
# =============================

@api_bp.route('/negocios', methods=['GET', 'POST'])
@require_api_key
def api_negocios():
    """CRUD de negocios"""
    try:
        if request.method == 'GET':
            # Listar negocios
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, nombre, descripcion, direccion, telefono, email, activo, fecha_creacion
                    FROM negocios
                    ORDER BY nombre
                ''')
                rows = cursor.fetchall()
                
                negocios = []
                for row in rows:
                    negocios.append({
                        'id': row[0],
                        'nombre': row[1],
                        'descripcion': row[2],
                        'direccion': row[3],
                        'telefono': row[4],
                        'email': row[5],
                        'activo': bool(row[6]),
                        'fecha_creacion': row[7]
                    })
                
                return jsonify({
                    'status': 'success',
                    'data': negocios,
                    'total': len(negocios)
                })
        
        elif request.method == 'POST':
            # Crear negocio
            data = request.get_json()
            
            if 'nombre' not in data:
                return jsonify({'error': 'Missing required field: nombre'}), 400
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['nombre'],
                    data.get('descripcion', ''),
                    data.get('direccion', ''),
                    data.get('telefono', ''),
                    data.get('email', ''),
                    data.get('activo', True)
                ))
                
                negocio_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Negocio creado exitosamente',
                    'data': {'id': negocio_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_negocios: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/negocios/<int:negocio_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_negocio_detail(negocio_id):
    """CRUD individual de negocio"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if request.method == 'GET':
                # Obtener negocio específico
                cursor.execute('''
                    SELECT id, nombre, descripcion, direccion, telefono, email, activo, fecha_creacion
                    FROM negocios WHERE id = ?
                ''', (negocio_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Negocio no encontrado'}), 404
                
                negocio = {
                    'id': row[0], 'nombre': row[1], 'descripcion': row[2], 'direccion': row[3],
                    'telefono': row[4], 'email': row[5], 'activo': bool(row[6]), 'fecha_creacion': row[7]
                }
                
                return jsonify({'status': 'success', 'data': negocio})
            
            elif request.method == 'PUT':
                # Actualizar negocio
                data = request.get_json()
                fields, values = [], []
                
                for field in ['nombre', 'descripcion', 'direccion', 'telefono', 'email', 'activo']:
                    if field in data:
                        fields.append(f"{field} = ?")
                        values.append(data[field])
                
                if not fields:
                    return jsonify({'error': 'No fields to update'}), 400
                
                values.append(negocio_id)
                query = f"UPDATE negocios SET {', '.join(fields)}, fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Negocio no encontrado'}), 404
                
                return jsonify({'status': 'success', 'message': 'Negocio actualizado exitosamente'})
            
            elif request.method == 'DELETE':
                # Eliminar negocio
                cursor.execute('DELETE FROM negocios WHERE id = ?', (negocio_id,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Negocio no encontrado'}), 404
                
                return jsonify({'status': 'success', 'message': 'Negocio eliminado exitosamente'})
    
    except Exception as e:
        logger.error(f"Error in api_negocio_detail: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE SUCURSALES
# =============================

@api_bp.route('/sucursales', methods=['GET', 'POST'])
@require_api_key
def api_sucursales():
    """CRUD de sucursales"""
    try:
        if request.method == 'GET':
            # Listar sucursales
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.id, s.nombre, s.direccion, s.telefono, s.email, 
                           s.activo, s.horario_apertura, s.horario_cierre
                    FROM sucursales s
                    ORDER BY s.nombre
                ''')
                rows = cursor.fetchall()
                
                sucursales = []
                for row in rows:
                    sucursales.append({
                        'id': row[0],
                        'nombre': row[1],
                        'direccion': row[2],
                        'telefono': row[3],
                        'email': row[4],
                        'activo': bool(row[5]),
                        'horario_apertura': row[6],
                        'horario_cierre': row[7]
                    })
                
                return jsonify({
                    'status': 'success',
                    'data': sucursales,
                    'total': len(sucursales)
                })
        
        elif request.method == 'POST':
            # Crear sucursal
            data = request.get_json()
            required_fields = ['nombre', 'negocio_id']
            
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sucursales (nombre, direccion, telefono, email, negocio_id, activo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['nombre'],
                    data.get('direccion', ''),
                    data.get('telefono', ''),
                    data.get('email', ''),
                    data['negocio_id'],
                    data.get('activo', True)
                ))
                
                sucursal_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Sucursal creada exitosamente',
                    'data': {'id': sucursal_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_sucursales: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sucursales/<int:sucursal_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_sucursal_detail(sucursal_id):
    """CRUD individual de sucursal"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if request.method == 'GET':
                cursor.execute('''
                    SELECT s.id, s.nombre, s.direccion, s.telefono, s.email, s.negocio_id, s.activo, n.nombre
                    FROM sucursales s LEFT JOIN negocios n ON s.negocio_id = n.id WHERE s.id = ?
                ''', (sucursal_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Sucursal no encontrada'}), 404
                
                sucursal = {
                    'id': row[0], 'nombre': row[1], 'direccion': row[2], 'telefono': row[3], 'email': row[4],
                    'negocio_id': row[5], 'activo': bool(row[6]), 'negocio_nombre': row[7]
                }
                
                return jsonify({'status': 'success', 'data': sucursal})
            
            elif request.method == 'PUT':
                data = request.get_json()
                fields, values = [], []
                
                for field in ['nombre', 'direccion', 'telefono', 'email', 'negocio_id', 'activo']:
                    if field in data:
                        fields.append(f"{field} = ?")
                        values.append(data[field])
                
                if not fields:
                    return jsonify({'error': 'No fields to update'}), 400
                
                values.append(sucursal_id)
                query = f"UPDATE sucursales SET {', '.join(fields)}, fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Sucursal no encontrada'}), 404
                
                return jsonify({'status': 'success', 'message': 'Sucursal actualizada exitosamente'})
            
            elif request.method == 'DELETE':
                cursor.execute('DELETE FROM sucursales WHERE id = ?', (sucursal_id,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Sucursal no encontrada'}), 404
                
                return jsonify({'status': 'success', 'message': 'Sucursal eliminada exitosamente'})
    
    except Exception as e:
        logger.error(f"Error in api_sucursal_detail: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE PRODUCTOS
# =============================

@api_bp.route('/productos', methods=['GET', 'POST'])
@require_api_key
def api_productos():
    """CRUD de productos"""
    try:
        if request.method == 'GET':
            # Listar productos
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, p.nombre, p.store, p.precio, p.categoria, 
                           p.stock, p.activo, p.negocio_id, p.imagen
                    FROM productos p
                    ORDER BY p.nombre
                ''')
                rows = cursor.fetchall()
                
                productos = []
                for row in rows:
                    productos.append({
                        'id': row[0],
                        'nombre': row[1],
                        'store': row[2],
                        'precio': row[3],
                        'categoria': row[4],
                        'stock': row[5],
                        'activo': bool(row[6]),
                        'negocio_id': row[7],
                        'imagen': row[8]
                    })
                
                return jsonify({
                    'status': 'success',
                    'data': productos,
                    'total': len(productos)
                })
        
        elif request.method == 'POST':
            # Crear producto
            data = request.get_json()
            required_fields = ['nombre', 'precio']
            
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO productos (nombre, descripcion, precio, categoria, stock, negocio_id, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['nombre'],
                    data.get('descripcion', ''),
                    data['precio'],
                    data.get('categoria', ''),
                    data.get('stock', 0),
                    data.get('negocio_id'),
                    data.get('activo', True)
                ))
                
                producto_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Producto creado exitosamente',
                    'data': {'id': producto_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_productos: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_producto_detail(producto_id):
    """CRUD individual de producto"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if request.method == 'GET':
                # Obtener producto específico
                cursor.execute('''
                    SELECT p.id, p.nombre, p.descripcion, p.precio, p.categoria, 
                           p.stock, p.activo, p.negocio_id, n.nombre as negocio_nombre
                    FROM productos p
                    LEFT JOIN negocios n ON p.negocio_id = n.id
                    WHERE p.id = ?
                ''', (producto_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Producto no encontrado'}), 404
                
                producto = {
                    'id': row[0],
                    'nombre': row[1],
                    'descripcion': row[2],
                    'precio': row[3],
                    'categoria': row[4],
                    'stock': row[5],
                    'activo': bool(row[6]),
                    'negocio_id': row[7],
                    'negocio_nombre': row[8]
                }
                
                return jsonify({'status': 'success', 'data': producto})
            
            elif request.method == 'PUT':
                # Actualizar producto
                data = request.get_json()
                fields, values = [], []
                
                for field in ['nombre', 'descripcion', 'precio', 'categoria', 'stock', 'negocio_id', 'activo']:
                    if field in data:
                        fields.append(f"{field} = ?")
                        values.append(data[field])
                
                if not fields:
                    return jsonify({'error': 'No fields to update'}), 400
                
                values.append(producto_id)
                query = f"UPDATE productos SET {', '.join(fields)}, fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Producto no encontrado'}), 404
                
                return jsonify({'status': 'success', 'message': 'Producto actualizado exitosamente'})
            
            elif request.method == 'DELETE':
                # Eliminar producto
                cursor.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Producto no encontrado'}), 404
                
                return jsonify({'status': 'success', 'message': 'Producto eliminado exitosamente'})
    
    except Exception as e:
        logger.error(f"Error in api_producto_detail: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE OFERTAS
# =============================

@api_bp.route('/ofertas', methods=['GET', 'POST'])
@require_api_key
def api_ofertas():
    """CRUD de ofertas"""
    try:
        if request.method == 'GET':
            # Listar ofertas
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, titulo, descripcion, descuento_porcentaje, descuento_fijo, activa, fecha_creacion
                    FROM ofertas
                    ORDER BY fecha_creacion DESC
                ''')
                rows = cursor.fetchall()
                
                ofertas = []
                for row in rows:
                    ofertas.append({
                        'id': row[0],
                        'titulo': row[1],
                        'descripcion': row[2],
                        'descuento_porcentaje': float(row[3]) if row[3] is not None else 0.0,
                        'descuento_fijo': float(row[4]) if row[4] is not None else 0.0,
                        'activa': bool(row[5]),
                        'fecha_creacion': row[6]
                    })
                
                return jsonify({
                    'status': 'success',
                    'data': ofertas,
                    'total': len(ofertas)
                })
        
        elif request.method == 'POST':
            # Crear oferta
            data = request.get_json()
            
            if 'titulo' not in data:
                return jsonify({'error': 'Missing required field: titulo'}), 400
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ofertas (titulo, descripcion, descuento_porcentaje, descuento_fijo, activa)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['titulo'],
                    data.get('descripcion', ''),
                    data.get('descuento_porcentaje', 0.0),
                    data.get('descuento_fijo', 0.0),
                    data.get('activa', True)
                ))
                
                oferta_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Oferta creada exitosamente',
                    'data': {'id': oferta_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_ofertas: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/ofertas/<int:oferta_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_oferta_detail(oferta_id):
    """CRUD individual de oferta"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if request.method == 'GET':
                cursor.execute('''
                    SELECT id, titulo, descripcion, descuento_porcentaje, descuento_fijo, activa, fecha_creacion
                    FROM ofertas WHERE id = ?
                ''', (oferta_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Oferta no encontrada'}), 404
                
                oferta = {
                    'id': row[0], 'titulo': row[1], 'descripcion': row[2], 
                    'descuento_porcentaje': float(row[3]) if row[3] is not None else 0.0,
                    'descuento_fijo': float(row[4]) if row[4] is not None else 0.0,
                    'activa': bool(row[5]), 'fecha_creacion': row[6]
                }
                
                return jsonify({'status': 'success', 'data': oferta})
            
            elif request.method == 'PUT':
                data = request.get_json()
                fields, values = [], []
                
                for field in ['titulo', 'descripcion', 'descuento_porcentaje', 'descuento_fijo', 'activa']:
                    if field in data:
                        fields.append(f"{field} = ?")
                        values.append(data[field])
                
                if not fields:
                    return jsonify({'error': 'No fields to update'}), 400
                
                values.append(oferta_id)
                query = f"UPDATE ofertas SET {', '.join(fields)}, fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Oferta no encontrada'}), 404
                
                return jsonify({'status': 'success', 'message': 'Oferta actualizada exitosamente'})
            
            elif request.method == 'DELETE':
                cursor.execute('DELETE FROM ofertas WHERE id = ?', (oferta_id,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Oferta no encontrada'}), 404
                
                return jsonify({'status': 'success', 'message': 'Oferta eliminada exitosamente'})
    
    except Exception as e:
        logger.error(f"Error in api_oferta_detail: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ENDPOINTS DE PRECIOS
# =============================

@api_bp.route('/precios', methods=['GET'])
@require_api_key
def api_precios_list():
    """Listar precios y historial"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.nombre, p.precio,
                       (SELECT ph.precio_nuevo FROM precios_historial ph WHERE ph.producto_id = p.id ORDER BY ph.fecha_cambio DESC LIMIT 1) AS ultimo_precio,
                       (SELECT ph.fecha_cambio FROM precios_historial ph WHERE ph.producto_id = p.id ORDER BY ph.fecha_cambio DESC LIMIT 1) AS fecha_ultimo
                FROM productos p ORDER BY p.fecha_actualizacion DESC
            ''')
            rows = cursor.fetchall()
            data = []
            for r in rows:
                data.append({
                    'producto_id': r[0], 'nombre': r[1], 'precio': r[2], 
                    'ultimo_precio': r[3] if r[3] is not None else r[2], 
                    'fecha_ultimo': r[4]
                })
            return jsonify({'status': 'success', 'data': data, 'total': len(data)})
    except Exception as e:
        logger.error(f"Error in api_precios_list: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/precios/<int:producto_id>', methods=['PUT'])
@require_api_key
def api_precios_update(producto_id):
    """Actualizar precio de un producto y registrar historial"""
    try:
        data = request.get_json() or {}
        if 'precio' not in data:
            return jsonify({'error': 'Missing field: precio'}), 400
        
        motivo = data.get('motivo', 'Actualización vía API DevOps')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT precio FROM productos WHERE id = ?', (producto_id,))
            row = cursor.fetchone()
            
            if not row:
                return jsonify({'error': 'Producto no encontrado'}), 404
            
            precio_anterior = float(row[0])
            nuevo_precio = float(data['precio'])
            
            cursor.execute('UPDATE productos SET precio = ?, fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = ?', (nuevo_precio, producto_id))
            cursor.execute('INSERT INTO precios_historial (producto_id, precio_anterior, precio_nuevo, motivo) VALUES (?, ?, ?, ?)', (producto_id, precio_anterior, nuevo_precio, motivo))
            conn.commit()
            
            return jsonify({'status': 'success', 'message': 'Precio actualizado exitosamente'})
    
    except Exception as e:
        logger.error(f"Error in api_precios_update: {e}")
        return jsonify({'error': str(e)}), 500

# =============================
# ALIAS EN INGLÉS (SIN ROMPER RUTAS EXISTENTES)
# =============================

# Negocios
api_bp.add_url_rule('/businesses', view_func=api_negocios, methods=['GET', 'POST'])
api_bp.add_url_rule('/businesses/<int:negocio_id>', view_func=api_negocio_detail, methods=['GET', 'PUT', 'DELETE'])

# Sucursales
api_bp.add_url_rule('/branches', view_func=api_sucursales, methods=['GET', 'POST'])
api_bp.add_url_rule('/branches/<int:sucursal_id>', view_func=api_sucursal_detail, methods=['GET', 'PUT', 'DELETE'])

# Productos
api_bp.add_url_rule('/products', view_func=api_productos, methods=['GET', 'POST'])
api_bp.add_url_rule('/products/<int:producto_id>', view_func=api_producto_detail, methods=['GET', 'PUT', 'DELETE'])

# Ofertas
api_bp.add_url_rule('/offers', view_func=api_ofertas, methods=['GET', 'POST'])
api_bp.add_url_rule('/offers/<int:oferta_id>', view_func=api_oferta_detail, methods=['GET', 'PUT', 'DELETE'])

# Precios
api_bp.add_url_rule('/prices', view_func=api_precios_list, methods=['GET'])
api_bp.add_url_rule('/prices/<int:producto_id>', view_func=api_precios_update, methods=['PUT'])

# =============================
# ENDPOINTS DE UTILIDAD
# =============================

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Belgrano Ahorro API is running',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/status', methods=['GET'])
def api_status():
    """Status detallado de la API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar registros en tablas principales
        cursor.execute("SELECT COUNT(*) FROM productos")
        productos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM negocios")
        negocios_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sucursales")
        sucursales_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ofertas")
        ofertas_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'status': 'operational',
            'timestamp': datetime.now().isoformat(),
            'service': 'belgrano_ahorro_api',
            'version': '2.0.0',
            'database': {
                'productos': productos_count,
                'negocios': negocios_count,
                'sucursales': sucursales_count,
                'ofertas': ofertas_count
            }
        })
    except Exception as e:
        logger.error(f"Error en status check: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@api_bp.route('/ping', methods=['GET'])
def api_ping():
    """Ping simple para verificar conectividad"""
    return jsonify({
        'pong': True,
        'timestamp': datetime.now().isoformat()
    })