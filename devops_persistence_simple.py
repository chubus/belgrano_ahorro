#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Persistencia DevOps Simplificado
Conecta DevOps con la base de datos real de Belgrano Ahorro
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DevOpsPersistenceSimple:
    """Manejador de persistencia simplificado para DevOps"""
    
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
            
            # Tabla de negocios (si no existe)
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
            
            # Tabla de ofertas (si no existe)
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
                
                return {
                    'id': negocio_id,
                    'nombre': datos.get('nombre', ''),
                    'descripcion': datos.get('descripcion', ''),
                    'direccion': datos.get('direccion', ''),
                    'telefono': datos.get('telefono', ''),
                    'email': datos.get('email', ''),
                    'activo': datos.get('activo', True),
                    'fecha_creacion': datetime.now().isoformat(),
                    'fecha_actualizacion': datetime.now().isoformat()
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
                        'descripcion': negocio[2] if len(negocio) > 2 else '',
                        'direccion': negocio[3] if len(negocio) > 3 else '',
                        'telefono': negocio[4] if len(negocio) > 4 else '',
                        'email': negocio[5] if len(negocio) > 5 else '',
                        'activo': bool(negocio[6]) if len(negocio) > 6 else True,
                        'fecha_creacion': negocio[7] if len(negocio) > 7 else datetime.now().isoformat(),
                        'fecha_actualizacion': negocio[8] if len(negocio) > 8 else datetime.now().isoformat()
                    }
                    for negocio in negocios
                ]
        except Exception as e:
            logger.error(f"Error obteniendo negocios: {e}")
            return []
    
    # MÉTODOS PARA PRODUCTOS (usando tabla existente)
    def crear_producto(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crear un nuevo producto usando la tabla existente"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Usar la estructura existente de la tabla productos
                cursor.execute('''
                    INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datos.get('nombre', ''),
                    datos.get('store', 'DevOps'),
                    float(datos.get('precio', 0)),
                    datos.get('categoria', 'General'),
                    int(datos.get('stock', 0)),
                    int(datos.get('stock_minimo', 0)),
                    datos.get('negocio_id'),
                    datos.get('activo', True)
                ))
                
                producto_id = cursor.lastrowid
                conn.commit()
                
                return {
                    'id': producto_id,
                    'nombre': datos.get('nombre', ''),
                    'precio': float(datos.get('precio', 0)),
                    'categoria': datos.get('categoria', 'General'),
                    'stock': int(datos.get('stock', 0)),
                    'stock_minimo': int(datos.get('stock_minimo', 0)),
                    'negocio_id': datos.get('negocio_id'),
                    'activo': datos.get('activo', True),
                    'fecha_creacion': datetime.now().isoformat(),
                    'fecha_actualizacion': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            raise
    
    def obtener_productos(self) -> List[Dict[str, Any]]:
        """Obtener todos los productos"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM productos ORDER BY fecha_creacion DESC')
                productos = cursor.fetchall()
                
                return [
                    {
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
                    for producto in productos
                ]
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []
    
    # MÉTODOS PARA OFERTAS
    def crear_oferta(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crear una nueva oferta"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Convertir lista de productos a JSON string
                productos_json = json.dumps(datos.get('productos', []))
                
                cursor.execute('''
                    INSERT INTO ofertas (titulo, descripcion, descuento_porcentaje, descuento_fijo, fecha_inicio, fecha_fin, activa)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datos.get('titulo', ''),
                    datos.get('descripcion', ''),
                    datos.get('descuento_porcentaje', 0),
                    datos.get('descuento_fijo', 0),
                    datos.get('fecha_inicio', datetime.now().date().isoformat()),
                    datos.get('fecha_fin', datetime.now().date().isoformat()),
                    datos.get('activa', True)
                ))
                
                oferta_id = cursor.lastrowid
                conn.commit()
                
                return {
                    'id': oferta_id,
                    'titulo': datos.get('titulo', ''),
                    'descripcion': datos.get('descripcion', ''),
                    'descuento_porcentaje': datos.get('descuento_porcentaje', 0),
                    'descuento_fijo': datos.get('descuento_fijo', 0),
                    'fecha_inicio': datos.get('fecha_inicio', datetime.now().date().isoformat()),
                    'fecha_fin': datos.get('fecha_fin', datetime.now().date().isoformat()),
                    'activa': datos.get('activa', True),
                    'fecha_creacion': datetime.now().isoformat(),
                    'fecha_actualizacion': datetime.now().isoformat()
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
                        'descuento_porcentaje': oferta[3],
                        'descuento_fijo': oferta[4],
                        'fecha_inicio': oferta[5],
                        'fecha_fin': oferta[6],
                        'activa': bool(oferta[7]),
                        'fecha_creacion': oferta[8] if len(oferta) > 8 else datetime.now().isoformat(),
                        'fecha_actualizacion': oferta[9] if len(oferta) > 9 else datetime.now().isoformat()
                    }
                    for oferta in ofertas
                ]
        except Exception as e:
            logger.error(f"Error obteniendo ofertas: {e}")
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
                
                return {
                    'negocios_sync': negocios_count,
                    'productos_sync': productos_count,
                    'ofertas_sync': ofertas_count,
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
devops_db_simple = None

def get_devops_db_simple():
    """Obtener instancia global de DevOpsPersistenceSimple"""
    global devops_db_simple
    if devops_db_simple is None:
        devops_db_simple = DevOpsPersistenceSimple()
    return devops_db_simple
