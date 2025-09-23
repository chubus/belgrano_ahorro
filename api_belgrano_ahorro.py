#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API RESTful para Belgrano Ahorro
Endpoints para comunicación con DevOps
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
api_bp = Blueprint('api', __name__, url_prefix='/api')

def require_api_key(f):
    """Decorator para requerir API key válida"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener API key del header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header required'}), 401
        
        api_key = auth_header.split(' ')[1]
        expected_api_key = os.getenv('BELGRANO_AHORRO_API_KEY', 'dev_api_key_123')
        
        if api_key != expected_api_key:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Obtener conexión a la base de datos"""
    db_path = os.getenv('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
    return sqlite3.connect(db_path)

@api_bp.route('/products', methods=['GET', 'POST'])
@require_api_key
def api_products():
    """CRUD de productos"""
    try:
        if request.method == 'GET':
            # Listar productos
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.id, p.nombre, p.descripcion, p.precio, p.categoria, 
                           p.stock, p.activo, p.negocio_id, n.nombre as negocio_nombre
                    FROM productos p
                    LEFT JOIN negocios n ON p.negocio_id = n.id
                    ORDER BY p.nombre
                ''')
                rows = cursor.fetchall()
                
                products = []
                for row in rows:
                    products.append({
                        'id': row[0],
                        'nombre': row[1],
                        'descripcion': row[2],
                        'precio': row[3],
                        'categoria': row[4],
                        'stock': row[5],
                        'activo': bool(row[6]),
                        'negocio_id': row[7],
                        'negocio_nombre': row[8]
                    })
                
                return jsonify({
                    'status': 'success',
                    'data': products,
                    'total': len(products)
                })
        
        elif request.method == 'POST':
            # Crear producto
            data = request.get_json()
            required_fields = ['nombre', 'precio', 'categoria']
            
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
                    data['categoria'],
                    data.get('stock', 0),
                    data.get('negocio_id'),
                    data.get('activo', True)
                ))
                
                product_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Product created successfully',
                    'data': {'id': product_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_products: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
@require_api_key
def api_product_detail(product_id):
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
                ''', (product_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Product not found'}), 404
                
                product = {
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
                
                return jsonify({'status': 'success', 'data': product})
            
            elif request.method == 'PUT':
                # Actualizar producto
                data = request.get_json()
                
                # Construir query dinámicamente
                fields = []
                values = []
                
                for field in ['nombre', 'descripcion', 'precio', 'categoria', 'stock', 'negocio_id', 'activo']:
                    if field in data:
                        fields.append(f"{field} = ?")
                        values.append(data[field])
                
                if not fields:
                    return jsonify({'error': 'No fields to update'}), 400
                
                values.append(product_id)
                query = f"UPDATE productos SET {', '.join(fields)} WHERE id = ?"
                
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Product not found'}), 404
                
                return jsonify({'status': 'success', 'message': 'Product updated successfully'})
            
            elif request.method == 'DELETE':
                # Eliminar producto
                cursor.execute('DELETE FROM productos WHERE id = ?', (product_id,))
                conn.commit()
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Product not found'}), 404
                
                return jsonify({'status': 'success', 'message': 'Product deleted successfully'})
    
    except Exception as e:
        logger.error(f"Error in api_product_detail: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/businesses', methods=['GET', 'POST'])
@require_api_key
def api_businesses():
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
                
                businesses = []
                for row in rows:
                    businesses.append({
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
                    'data': businesses,
                    'total': len(businesses)
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
                
                business_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Business created successfully',
                    'data': {'id': business_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_businesses: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/branches', methods=['GET', 'POST'])
@require_api_key
def api_branches():
    """CRUD de sucursales"""
    try:
        if request.method == 'GET':
            # Listar sucursales
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.id, s.nombre, s.direccion, s.telefono, s.email, 
                           s.negocio_id, s.activo, n.nombre as negocio_nombre
                    FROM sucursales s
                    LEFT JOIN negocios n ON s.negocio_id = n.id
                    ORDER BY s.nombre
                ''')
                rows = cursor.fetchall()
                
                branches = []
                for row in rows:
                    branches.append({
                        'id': row[0],
                        'nombre': row[1],
                        'direccion': row[2],
                        'telefono': row[3],
                        'email': row[4],
                        'negocio_id': row[5],
                        'activo': bool(row[6]),
                        'negocio_nombre': row[7]
                    })
                
                return jsonify({
                    'status': 'success',
                    'data': branches,
                    'total': len(branches)
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
                
                branch_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Branch created successfully',
                    'data': {'id': branch_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_branches: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/offers', methods=['GET', 'POST'])
@require_api_key
def api_offers():
    """CRUD de ofertas"""
    try:
        if request.method == 'GET':
            # Listar ofertas
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, titulo, descripcion, productos, hasta_agotar_stock, activa, fecha_creacion
                    FROM ofertas
                    ORDER BY fecha_creacion DESC
                ''')
                rows = cursor.fetchall()
                
                offers = []
                for row in rows:
                    offers.append({
                        'id': row[0],
                        'titulo': row[1],
                        'descripcion': row[2],
                        'productos': row[3],
                        'hasta_agotar_stock': bool(row[4]),
                        'activa': bool(row[5]),
                        'fecha_creacion': row[6]
                    })
                
                return jsonify({
                    'status': 'success',
                    'data': offers,
                    'total': len(offers)
                })
        
        elif request.method == 'POST':
            # Crear oferta
            data = request.get_json()
            
            if 'titulo' not in data:
                return jsonify({'error': 'Missing required field: titulo'}), 400
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ofertas (titulo, descripcion, productos, hasta_agotar_stock, activa)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['titulo'],
                    data.get('descripcion', ''),
                    data.get('productos', ''),
                    data.get('hasta_agotar_stock', False),
                    data.get('activa', True)
                ))
                
                offer_id = cursor.lastrowid
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Offer created successfully',
                    'data': {'id': offer_id}
                }), 201
    
    except Exception as e:
        logger.error(f"Error in api_offers: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cart', methods=['GET', 'POST'])
@require_api_key
def api_cart():
    """Consultar y confirmar carrito"""
    try:
        if request.method == 'GET':
            # Obtener carrito (simulado por ahora)
            return jsonify({
                'status': 'success',
                'data': {
                    'items': [],
                    'total': 0,
                    'message': 'Cart functionality not implemented yet'
                }
            })
        
        elif request.method == 'POST':
            # Confirmar carrito
            data = request.get_json()
            
            return jsonify({
                'status': 'success',
                'message': 'Cart confirmed successfully',
                'data': {'order_id': f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}"}
            })
    
    except Exception as e:
        logger.error(f"Error in api_cart: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Belgrano Ahorro API is running',
        'timestamp': datetime.now().isoformat()
    })