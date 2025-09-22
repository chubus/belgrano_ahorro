#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Persistencia DevOps
Conecta DevOps con la base de datos real de Belgrano Ahorro
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DevOpsPersistence:
    """Manejador de persistencia para DevOps"""
    
    def __init__(self, db_path: str = None):
        """Inicializar conexión a base de datos"""
        if db_path is None:
            # Buscar la base de datos de Belgrano Ahorro
            possible_paths = [
                'belgrano_ahorro.db',
                '../belgrano_ahorro.db',
                '../../belgrano_ahorro.db',
                os.path.join(os.path.dirname(__file__), 'belgrano_ahorro.db'),
                os.path.join(os.path.dirname(__file__), '..', 'belgrano_ahorro.db')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    db_path = path
                    break
            
            if not db_path or not os.path.exists(db_path):
                raise FileNotFoundError("No se encontró la base de datos belgrano_ahorro.db")
        
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_connection(self):
        """Obtener conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def _ensure_tables(self):
        """Asegurar que las tablas necesarias existan"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de negocios
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
            
            # Tabla de productos
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
            
            # Tabla de ofertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ofertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    productos TEXT,  -- JSON string con lista de productos
                    hasta_agotar_stock BOOLEAN DEFAULT 0,
                    activa BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de categorías
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT,
                    activa BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    # MÉTODOS PARA NEGOCIOS
    def crear_negocio(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crear un nuevo negocio"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datos.get('nombre', ''),
                    datos.get('descripcion', ''),
                    datos.get('direccion', ''),
                    datos.get('telefono', ''),
                    datos.get('email', ''),
                    datos.get('activo', True)
                ))
                
                negocio_id = cursor.lastrowid
                conn.commit()
                
                # Obtener el negocio creado
                cursor.execute('SELECT * FROM negocios WHERE id = ?', (negocio_id,))
                negocio = cursor.fetchone()
                
                return {
                    'id': negocio[0],
                    'nombre': negocio[1],
                    'descripcion': negocio[2],
                    'direccion': negocio[3],
                    'telefono': negocio[4],
                    'email': negocio[5],
                    'activo': bool(negocio[6]),
                    'fecha_creacion': negocio[7] if len(negocio) > 7 else datetime.now().isoformat(),
                    'fecha_actualizacion': negocio[8] if len(negocio) > 8 else datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error creando negocio: {e}")
            raise
    
    def obtener_negocios(self) -> List[Dict[str, Any]]:
        """Obtener todos los negocios"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM negocios ORDER BY fecha_creacion DESC')
                negocios = cursor.fetchall()
                
                return [
                    {
                        'id': negocio[0],
                        'nombre': negocio[1],
                        'descripcion': negocio[2],
                        'direccion': negocio[3],
                        'telefono': negocio[4],
                        'email': negocio[5],
                        'activo': bool(negocio[6]),
                        'fecha_creacion': negocio[7] if len(negocio) > 7 else datetime.now().isoformat(),
                        'fecha_actualizacion': negocio[8] if len(negocio) > 8 else datetime.now().isoformat()
                    }
                    for negocio in negocios
                ]
        except Exception as e:
            logger.error(f"Error obteniendo negocios: {e}")
            return []
    
    def actualizar_negocio(self, negocio_id: int, datos: Dict[str, Any]) -> bool:
        """Actualizar un negocio existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE negocios 
                    SET nombre = ?, descripcion = ?, direccion = ?, telefono = ?, 
                        email = ?, activo = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    datos.get('nombre', ''),
                    datos.get('descripcion', ''),
                    datos.get('direccion', ''),
                    datos.get('telefono', ''),
                    datos.get('email', ''),
                    datos.get('activo', True),
                    negocio_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error actualizando negocio: {e}")
            return False
    
    def eliminar_negocio(self, negocio_id: int) -> bool:
        """Eliminar un negocio"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM negocios WHERE id = ?', (negocio_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error eliminando negocio: {e}")
            return False
    
    # MÉTODOS PARA PRODUCTOS
    def crear_producto(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crear un nuevo producto"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO productos (nombre, precio, categoria, stock, stock_minimo, negocio_id, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datos.get('nombre', ''),
                    float(datos.get('precio', 0)),
                    datos.get('categoria', 'General'),
                    int(datos.get('stock', 0)),
                    int(datos.get('stock_minimo', 0)),
                    datos.get('negocio_id'),
                    datos.get('activo', True)
                ))
                
                producto_id = cursor.lastrowid
                conn.commit()
                
                # Obtener el producto creado
                cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
                producto = cursor.fetchone()
                
                return {
                    'id': producto[0],
                    'nombre': producto[1],
                    'precio': producto[3],
                    'categoria': producto[8],
                    'stock': producto[11],
                    'stock_minimo': producto[12],
                    'negocio_id': producto[13],
                    'activo': bool(producto[10]),
                    'fecha_creacion': producto[14] if len(producto) > 14 else datetime.now().isoformat(),
                    'fecha_actualizacion': producto[15] if len(producto) > 15 else datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            raise
    
    def obtener_productos(self) -> List[Dict[str, Any]]:
        """Obtener todos los productos"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT p.*, n.nombre as negocio_nombre 
                    FROM productos p 
                    LEFT JOIN negocios n ON p.negocio_id = n.id 
                    ORDER BY p.fecha_creacion DESC
                ''')
                productos = cursor.fetchall()
                
                return [
                    {
                        'id': producto[0],
                        'nombre': producto[1],
                        'descripcion': producto[2],
                        'precio': producto[3],
                        'categoria': producto[4],
                        'stock': producto[5],
                        'stock_minimo': producto[6],
                        'negocio_id': producto[7],
                        'activo': bool(producto[8]),
                        'fecha_creacion': producto[9],
                        'fecha_actualizacion': producto[10],
                        'negocio_nombre': producto[11] if len(producto) > 11 else None
                    }
                    for producto in productos
                ]
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []
    
    def actualizar_producto(self, producto_id: int, datos: Dict[str, Any]) -> bool:
        """Actualizar un producto existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE productos 
                    SET nombre = ?, descripcion = ?, precio = ?, categoria = ?, 
                        stock = ?, stock_minimo = ?, negocio_id = ?, activo = ?, 
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    datos.get('nombre', ''),
                    datos.get('descripcion', ''),
                    float(datos.get('precio', 0)),
                    datos.get('categoria', 'General'),
                    int(datos.get('stock', 0)),
                    int(datos.get('stock_minimo', 0)),
                    datos.get('negocio_id'),
                    datos.get('activo', True),
                    producto_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error actualizando producto: {e}")
            return False
    
    def eliminar_producto(self, producto_id: int) -> bool:
        """Eliminar un producto"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error eliminando producto: {e}")
            return False
    
    # MÉTODOS PARA OFERTAS
    def crear_oferta(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crear una nueva oferta"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Convertir lista de productos a JSON string
                productos_json = json.dumps(datos.get('productos', []))
                
                cursor.execute('''
                    INSERT INTO ofertas (titulo, descripcion, productos, hasta_agotar_stock, activa)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    datos.get('titulo', ''),
                    datos.get('descripcion', ''),
                    productos_json,
                    datos.get('hasta_agotar_stock', False),
                    datos.get('activa', True)
                ))
                
                oferta_id = cursor.lastrowid
                conn.commit()
                
                # Obtener la oferta creada
                cursor.execute('SELECT * FROM ofertas WHERE id = ?', (oferta_id,))
                oferta = cursor.fetchone()
                
                return {
                    'id': oferta[0],
                    'titulo': oferta[1],
                    'descripcion': oferta[2],
                    'productos': json.loads(oferta[3]) if oferta[3] else [],
                    'hasta_agotar_stock': bool(oferta[4]),
                    'activa': bool(oferta[5]),
                    'fecha_creacion': oferta[6],
                    'fecha_actualizacion': oferta[7]
                }
                
        except Exception as e:
            logger.error(f"Error creando oferta: {e}")
            raise
    
    def obtener_ofertas(self) -> List[Dict[str, Any]]:
        """Obtener todas las ofertas"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ofertas ORDER BY fecha_creacion DESC')
                ofertas = cursor.fetchall()
                
                return [
                    {
                        'id': oferta[0],
                        'titulo': oferta[1],
                        'descripcion': oferta[2],
                        'productos': json.loads(oferta[3]) if oferta[3] else [],
                        'hasta_agotar_stock': bool(oferta[4]),
                        'activa': bool(oferta[5]),
                        'fecha_creacion': oferta[6],
                        'fecha_actualizacion': oferta[7]
                    }
                    for oferta in ofertas
                ]
        except Exception as e:
            logger.error(f"Error obteniendo ofertas: {e}")
            return []
    
    def actualizar_oferta(self, oferta_id: int, datos: Dict[str, Any]) -> bool:
        """Actualizar una oferta existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                productos_json = json.dumps(datos.get('productos', []))
                
                cursor.execute('''
                    UPDATE ofertas 
                    SET titulo = ?, descripcion = ?, productos = ?, 
                        hasta_agotar_stock = ?, activa = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    datos.get('titulo', ''),
                    datos.get('descripcion', ''),
                    productos_json,
                    datos.get('hasta_agotar_stock', False),
                    datos.get('activa', True),
                    oferta_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error actualizando oferta: {e}")
            return False
    
    def eliminar_oferta(self, oferta_id: int) -> bool:
        """Eliminar una oferta"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM ofertas WHERE id = ?', (oferta_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error eliminando oferta: {e}")
            return False
    
    # MÉTODOS PARA CATEGORÍAS
    def crear_categoria(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crear una nueva categoría"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO categorias (nombre, descripcion, activa)
                    VALUES (?, ?, ?)
                ''', (
                    datos.get('nombre', ''),
                    datos.get('descripcion', ''),
                    datos.get('activa', True)
                ))
                
                categoria_id = cursor.lastrowid
                conn.commit()
                
                return {
                    'id': categoria_id,
                    'nombre': datos.get('nombre', ''),
                    'descripcion': datos.get('descripcion', ''),
                    'activa': datos.get('activa', True),
                    'fecha_creacion': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error creando categoría: {e}")
            raise
    
    def obtener_categorias(self) -> List[Dict[str, Any]]:
        """Obtener todas las categorías"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM categorias ORDER BY nombre')
                categorias = cursor.fetchall()
                
                return [
                    {
                        'id': categoria[0],
                        'nombre': categoria[1],
                        'descripcion': categoria[2],
                        'activa': bool(categoria[3]),
                        'fecha_creacion': categoria[4]
                    }
                    for categoria in categorias
                ]
        except Exception as e:
            logger.error(f"Error obteniendo categorías: {e}")
            return []
    
    # MÉTODOS DE SINCRONIZACIÓN
    def sincronizar_con_belgrano_ahorro(self) -> Dict[str, Any]:
        """Sincronizar datos con la aplicación principal"""
        try:
            # Obtener estadísticas
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Contar registros
                cursor.execute('SELECT COUNT(*) FROM negocios')
                negocios_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM productos')
                productos_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM ofertas')
                ofertas_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM categorias')
                categorias_count = cursor.fetchone()[0]
                
                return {
                    'negocios_sync': negocios_count,
                    'productos_sync': productos_count,
                    'ofertas_sync': ofertas_count,
                    'categorias_sync': categorias_count,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
                
        except Exception as e:
            logger.error(f"Error en sincronización: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Instancia global para uso en la aplicación
devops_db = None

def get_devops_db():
    """Obtener instancia global de DevOpsPersistence"""
    global devops_db
    if devops_db is None:
        devops_db = DevOpsPersistence()
    return devops_db
