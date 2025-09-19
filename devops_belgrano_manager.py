#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de gestión DevOps para Belgrano Ahorro
Permite gestionar ofertas, productos, negocios y precios de forma segura
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DevOpsBelgranoManager:
    """Gestor DevOps para Belgrano Ahorro"""
    
    def __init__(self, db_path: str = 'belgrano_ahorro.db'):
        """Inicializar el gestor DevOps"""
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Asegurar que la base de datos existe"""
        if not os.path.exists(self.db_path):
            logger.warning(f"Base de datos {self.db_path} no encontrada")
            return False
        return True
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
            return conn
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {e}")
            return None
    
    # =================================================================
    # GESTIÓN DE PRODUCTOS
    # =================================================================
    
    def get_productos(self, activos_only: bool = True) -> List[Dict]:
        """Obtener todos los productos"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            query = "SELECT * FROM productos"
            if activos_only:
                query += " WHERE activo = 1"
            query += " ORDER BY id DESC"
            
            cursor = conn.cursor()
            cursor.execute(query)
            productos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []
    
    def get_producto(self, producto_id: int) -> Optional[Dict]:
        """Obtener un producto específico"""
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo producto {producto_id}: {e}")
            return None
    
    def crear_producto(self, datos: Dict) -> bool:
        """Crear un nuevo producto"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO productos (nombre, store, precio, original_price, discount, 
                                    new, imagen, categoria, destacado, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos.get('nombre', ''),
                datos.get('store', ''),
                datos.get('precio', 0.0),
                datos.get('original_price', 0.0),
                datos.get('discount', 0),
                datos.get('new', 0),
                datos.get('imagen', ''),
                datos.get('categoria', ''),
                datos.get('destacado', 0),
                datos.get('activo', 1)
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Producto creado: {datos.get('nombre')}")
            return True
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            return False
    
    def actualizar_producto(self, producto_id: int, datos: Dict) -> bool:
        """Actualizar un producto existente"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            # Construir query dinámicamente
            campos = []
            valores = []
            
            for campo, valor in datos.items():
                if campo in ['nombre', 'store', 'precio', 'original_price', 'discount', 
                           'new', 'imagen', 'categoria', 'destacado', 'activo']:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos:
                return False
            
            valores.append(producto_id)
            query = f"UPDATE productos SET {', '.join(campos)} WHERE id = ?"
            
            cursor = conn.cursor()
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            
            logger.info(f"Producto {producto_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"Error actualizando producto {producto_id}: {e}")
            return False
    
    def eliminar_producto(self, producto_id: int) -> bool:
        """Eliminar un producto (marcar como inactivo)"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET activo = 0 WHERE id = ?", (producto_id,))
            conn.commit()
            conn.close()
            
            logger.info(f"Producto {producto_id} eliminado (marcado como inactivo)")
            return True
        except Exception as e:
            logger.error(f"Error eliminando producto {producto_id}: {e}")
            return False
    
    # =================================================================
    # GESTIÓN DE COMERCIANTES/NEGOCIOS
    # =================================================================
    
    def get_comerciantes(self, activos_only: bool = True) -> List[Dict]:
        """Obtener todos los comerciantes"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            query = """
                SELECT c.*, u.nombre, u.apellido, u.email 
                FROM comerciantes c 
                JOIN usuarios u ON c.usuario_id = u.id
            """
            if activos_only:
                query += " WHERE c.activo = 1"
            query += " ORDER BY c.id DESC"
            
            cursor = conn.cursor()
            cursor.execute(query)
            comerciantes = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return comerciantes
        except Exception as e:
            logger.error(f"Error obteniendo comerciantes: {e}")
            return []
    
    def get_comerciante(self, comerciante_id: int) -> Optional[Dict]:
        """Obtener un comerciante específico"""
        try:
            conn = self.get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, u.nombre, u.apellido, u.email 
                FROM comerciantes c 
                JOIN usuarios u ON c.usuario_id = u.id 
                WHERE c.id = ?
            """, (comerciante_id,))
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error obteniendo comerciante {comerciante_id}: {e}")
            return None
    
    def actualizar_comerciante(self, comerciante_id: int, datos: Dict) -> bool:
        """Actualizar un comerciante existente"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            # Construir query dinámicamente
            campos = []
            valores = []
            
            for campo, valor in datos.items():
                if campo in ['nombre_negocio', 'cuit', 'direccion_comercial', 
                           'telefono_comercial', 'tipo_negocio', 'activo']:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos:
                return False
            
            valores.append(comerciante_id)
            query = f"UPDATE comerciantes SET {', '.join(campos)} WHERE id = ?"
            
            cursor = conn.cursor()
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            
            logger.info(f"Comerciante {comerciante_id} actualizado")
            return True
        except Exception as e:
            logger.error(f"Error actualizando comerciante {comerciante_id}: {e}")
            return False
    
    # =================================================================
    # GESTIÓN DE OFERTAS (productos destacados)
    # =================================================================
    
    def get_ofertas(self) -> List[Dict]:
        """Obtener productos en oferta"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM productos 
                WHERE activo = 1 AND (discount > 0 OR destacado = 1)
                ORDER BY discount DESC, destacado DESC
            """)
            ofertas = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return ofertas
        except Exception as e:
            logger.error(f"Error obteniendo ofertas: {e}")
            return []
    
    def crear_oferta(self, producto_id: int, descuento: int, destacado: bool = False) -> bool:
        """Crear una oferta para un producto"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos 
                SET discount = ?, destacado = ?
                WHERE id = ?
            """, (descuento, 1 if destacado else 0, producto_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Oferta creada para producto {producto_id}")
            return True
        except Exception as e:
            logger.error(f"Error creando oferta: {e}")
            return False
    
    def eliminar_oferta(self, producto_id: int) -> bool:
        """Eliminar oferta de un producto"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos 
                SET discount = 0, destacado = 0
                WHERE id = ?
            """, (producto_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Oferta eliminada para producto {producto_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando oferta: {e}")
            return False
    
    # =================================================================
    # GESTIÓN DE PRECIOS
    # =================================================================
    
    def actualizar_precio(self, producto_id: int, nuevo_precio: float, precio_original: float = None) -> bool:
        """Actualizar precio de un producto"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            if precio_original:
                # Actualizar precio y precio original
                cursor.execute("""
                    UPDATE productos 
                    SET precio = ?, original_price = ?
                    WHERE id = ?
                """, (nuevo_precio, precio_original, producto_id))
            else:
                # Solo actualizar precio
                cursor.execute("""
                    UPDATE productos 
                    SET precio = ?
                    WHERE id = ?
                """, (nuevo_precio, producto_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Precio actualizado para producto {producto_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando precio: {e}")
            return False
    
    # =================================================================
    # GESTIÓN DE ELEMENTOS DE PÁGINA PRINCIPAL
    # =================================================================
    
    def get_productos_destacados(self) -> List[Dict]:
        """Obtener productos destacados para la página principal"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM productos 
                WHERE activo = 1 AND destacado = 1
                ORDER BY id DESC
                LIMIT 10
            """)
            destacados = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return destacados
        except Exception as e:
            logger.error(f"Error obteniendo productos destacados: {e}")
            return []
    
    def get_productos_nuevos(self) -> List[Dict]:
        """Obtener productos nuevos para la página principal"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM productos 
                WHERE activo = 1 AND new = 1
                ORDER BY id DESC
                LIMIT 10
            """)
            nuevos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return nuevos
        except Exception as e:
            logger.error(f"Error obteniendo productos nuevos: {e}")
            return []
    
    def set_producto_destacado(self, producto_id: int, destacado: bool = True) -> bool:
        """Marcar/desmarcar producto como destacado"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos 
                SET destacado = ?
                WHERE id = ?
            """, (1 if destacado else 0, producto_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Producto {producto_id} {'destacado' if destacado else 'no destacado'}")
            return True
        except Exception as e:
            logger.error(f"Error marcando producto como destacado: {e}")
            return False
    
    def set_producto_nuevo(self, producto_id: int, nuevo: bool = True) -> bool:
        """Marcar/desmarcar producto como nuevo"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos 
                SET new = ?
                WHERE id = ?
            """, (1 if nuevo else 0, producto_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Producto {producto_id} {'marcado como nuevo' if nuevo else 'no marcado como nuevo'}")
            return True
        except Exception as e:
            logger.error(f"Error marcando producto como nuevo: {e}")
            return False
    
    # =================================================================
    # GESTIÓN DE PRECIOS POR NEGOCIO
    # =================================================================
    
    def get_precios_por_negocio(self, comerciante_id: int) -> List[Dict]:
        """Obtener precios de productos por negocio específico"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, c.nombre_negocio 
                FROM productos p
                JOIN comerciantes c ON p.store = c.nombre_negocio
                WHERE c.id = ? AND p.activo = 1
                ORDER BY p.nombre
            """, (comerciante_id,))
            
            productos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo precios por negocio {comerciante_id}: {e}")
            return []
    
    def actualizar_precio_negocio(self, comerciante_id: int, producto_id: int, nuevo_precio: float, precio_original: float = None) -> bool:
        """Actualizar precio de un producto específico de un negocio"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Verificar que el producto pertenece al negocio
            cursor.execute("""
                SELECT p.id FROM productos p
                JOIN comerciantes c ON p.store = c.nombre_negocio
                WHERE c.id = ? AND p.id = ?
            """, (comerciante_id, producto_id))
            
            if not cursor.fetchone():
                logger.warning(f"Producto {producto_id} no pertenece al negocio {comerciante_id}")
                return False
            
            # Actualizar precio
            if precio_original:
                cursor.execute("""
                    UPDATE productos 
                    SET precio = ?, original_price = ?
                    WHERE id = ?
                """, (nuevo_precio, precio_original, producto_id))
            else:
                cursor.execute("""
                    UPDATE productos 
                    SET precio = ?
                    WHERE id = ?
                """, (nuevo_precio, producto_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Precio actualizado para producto {producto_id} del negocio {comerciante_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando precio del negocio: {e}")
            return False
    
    def get_estadisticas_negocio(self, comerciante_id: int) -> Dict:
        """Obtener estadísticas de un negocio específico"""
        try:
            conn = self.get_connection()
            if not conn:
                return {}
            
            cursor = conn.cursor()
            
            # Obtener información del comerciante
            cursor.execute("SELECT * FROM comerciantes WHERE id = ?", (comerciante_id,))
            comerciante = cursor.fetchone()
            if not comerciante:
                return {}
            
            # Contar productos del negocio
            cursor.execute("""
                SELECT COUNT(*) FROM productos p
                JOIN comerciantes c ON p.store = c.nombre_negocio
                WHERE c.id = ? AND p.activo = 1
            """, (comerciante_id,))
            total_productos = cursor.fetchone()[0]
            
            # Contar productos en oferta
            cursor.execute("""
                SELECT COUNT(*) FROM productos p
                JOIN comerciantes c ON p.store = c.nombre_negocio
                WHERE c.id = ? AND p.activo = 1 AND p.discount > 0
            """, (comerciante_id,))
            productos_oferta = cursor.fetchone()[0]
            
            # Contar productos destacados
            cursor.execute("""
                SELECT COUNT(*) FROM productos p
                JOIN comerciantes c ON p.store = c.nombre_negocio
                WHERE c.id = ? AND p.activo = 1 AND p.destacado = 1
            """, (comerciante_id,))
            productos_destacados = cursor.fetchone()[0]
            
            # Precio promedio
            cursor.execute("""
                SELECT AVG(precio) FROM productos p
                JOIN comerciantes c ON p.store = c.nombre_negocio
                WHERE c.id = ? AND p.activo = 1
            """, (comerciante_id,))
            precio_promedio = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'comerciante': dict(comerciante),
                'productos': {
                    'total': total_productos,
                    'ofertas': productos_oferta,
                    'destacados': productos_destacados,
                    'precio_promedio': round(precio_promedio, 2)
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del negocio {comerciante_id}: {e}")
            return {}
    
    def crear_oferta_negocio(self, comerciante_id: int, producto_id: int, descuento: int, destacado: bool = False) -> bool:
        """Crear oferta para un producto específico de un negocio"""
        try:
            conn = self.get_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Verificar que el producto pertenece al negocio
            cursor.execute("""
                SELECT p.id FROM productos p
                JOIN comerciantes c ON p.store = c.nombre_negocio
                WHERE c.id = ? AND p.id = ?
            """, (comerciante_id, producto_id))
            
            if not cursor.fetchone():
                logger.warning(f"Producto {producto_id} no pertenece al negocio {comerciante_id}")
                return False
            
            # Crear oferta
            cursor.execute("""
                UPDATE productos 
                SET discount = ?, destacado = ?
                WHERE id = ?
            """, (descuento, 1 if destacado else 0, producto_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Oferta creada para producto {producto_id} del negocio {comerciante_id}")
            return True
        except Exception as e:
            logger.error(f"Error creando oferta del negocio: {e}")
            return False

    # =================================================================
    # ESTADÍSTICAS Y REPORTES
    # =================================================================
    
    def get_estadisticas(self) -> Dict:
        """Obtener estadísticas del sistema"""
        try:
            conn = self.get_connection()
            if not conn:
                return {}
            
            cursor = conn.cursor()
            
            # Contar productos
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
            total_productos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1 AND destacado = 1")
            productos_destacados = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1 AND new = 1")
            productos_nuevos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1 AND discount > 0")
            productos_oferta = cursor.fetchone()[0]
            
            # Contar comerciantes
            cursor.execute("SELECT COUNT(*) FROM comerciantes WHERE activo = 1")
            total_comerciantes = cursor.fetchone()[0]
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cursor.fetchone()[0]
            
            # Contar pedidos
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            total_pedidos = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'productos': {
                    'total': total_productos,
                    'destacados': productos_destacados,
                    'nuevos': productos_nuevos,
                    'ofertas': productos_oferta
                },
                'comerciantes': total_comerciantes,
                'usuarios': total_usuarios,
                'pedidos': total_pedidos,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
