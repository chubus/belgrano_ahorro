#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor DevOps con acceso directo a base local (migrado a paquete devops)
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevOpsBelgranoManager:
    def __init__(self):
        self.db_path = os.environ.get('BELGRANO_AHORRO_DB_PATH', 'belgrano_ahorro.db')
        self.ensure_db_connection()

    def ensure_db_connection(self):
        try:
            if not os.path.exists(self.db_path):
                logger.warning(f"Base de datos no encontrada en: {self.db_path}")
                alternative_paths = ['belgrano_ahorro.db','../belgrano_ahorro.db','./belgrano_ahorro.db']
                for path in alternative_paths:
                    if os.path.exists(path):
                        self.db_path = path
                        logger.info(f"Base de datos encontrada en: {path}")
                        break
                else:
                    logger.error("No se pudo encontrar la base de datos de Belgrano Ahorro")
                    return False
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logger.info(f"✅ Conexión a base de datos establecida: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando a base de datos: {e}")
            return False

    def get_connection(self):
        try:
            return sqlite3.connect(self.db_path)
        except Exception as e:
            logger.error(f"Error obteniendo conexión: {e}")
            return None

    def get_ofertas(self) -> List[Dict]:
        try:
            conn = self.get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, titulo, descripcion, descuento, fecha_inicio, fecha_fin, activa, negocio_id
                FROM ofertas 
                ORDER BY fecha_inicio DESC
            """)
            ofertas = []
            for row in cursor.fetchall():
                ofertas.append({'id': row[0],'titulo': row[1],'descripcion': row[2],'descuento': row[3],'fecha_inicio': row[4],'fecha_fin': row[5],'activa': bool(row[6]),'negocio_id': row[7]})
            conn.close()
            logger.info(f"✅ Ofertas obtenidas: {len(ofertas)}")
            return ofertas
        except Exception as e:
            logger.error(f"Error obteniendo ofertas: {e}")
            return []

    def create_oferta(self, oferta_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ofertas (titulo, descripcion, descuento, fecha_inicio, fecha_fin, activa, negocio_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                oferta_data.get('titulo'),
                oferta_data.get('descripcion'),
                oferta_data.get('descuento'),
                oferta_data.get('fecha_inicio'),
                oferta_data.get('fecha_fin'),
                oferta_data.get('activa', True),
                oferta_data.get('negocio_id')
            ))
            conn.commit()
            conn.close()
            logger.info(f"✅ Oferta creada: {oferta_data.get('titulo')}")
            return True
        except Exception as e:
            logger.error(f"Error creando oferta: {e}")
            return False

    def update_oferta(self, oferta_id: int, oferta_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ofertas 
                SET titulo=?, descripcion=?, descuento=?, fecha_inicio=?, fecha_fin=?, activa=?, negocio_id=?
                WHERE id=?
            """, (
                oferta_data.get('titulo'),
                oferta_data.get('descripcion'),
                oferta_data.get('descuento'),
                oferta_data.get('fecha_inicio'),
                oferta_data.get('fecha_fin'),
                oferta_data.get('activa'),
                oferta_data.get('negocio_id'),
                oferta_id
            ))
            conn.commit()
            conn.close()
            logger.info(f"✅ Oferta actualizada: ID {oferta_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando oferta: {e}")
            return False

    def delete_oferta(self, oferta_id: int) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ofertas WHERE id=?", (oferta_id,))
            conn.commit()
            conn.close()
            logger.info(f"✅ Oferta eliminada: ID {oferta_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando oferta: {e}")
            return False

    def get_productos(self) -> List[Dict]:
        try:
            conn = self.get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, descripcion, precio, categoria_id, negocio_id, activo
                FROM productos 
                ORDER BY nombre
            """)
            productos = []
            for row in cursor.fetchall():
                productos.append({'id': row[0],'nombre': row[1],'descripcion': row[2],'precio': row[3],'categoria_id': row[4],'negocio_id': row[5],'activo': bool(row[6])})
            conn.close()
            logger.info(f"✅ Productos obtenidos: {len(productos)}")
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []

    def create_producto(self, producto_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO productos (nombre, descripcion, precio, categoria_id, negocio_id, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                producto_data.get('nombre'),
                producto_data.get('descripcion'),
                producto_data.get('precio'),
                producto_data.get('categoria_id'),
                producto_data.get('negocio_id'),
                producto_data.get('activo', True)
            ))
            conn.commit()
            conn.close()
            logger.info(f"✅ Producto creado: {producto_data.get('nombre')}")
            return True
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            return False

    def update_producto(self, producto_id: int, producto_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos 
                SET nombre=?, descripcion=?, precio=?, categoria_id=?, negocio_id=?, activo=?
                WHERE id=?
            """, (
                producto_data.get('nombre'),
                producto_data.get('descripcion'),
                producto_data.get('precio'),
                producto_data.get('categoria_id'),
                producto_data.get('negocio_id'),
                producto_data.get('activo'),
                producto_id
            ))
            conn.commit()
            conn.close()
            logger.info(f"✅ Producto actualizado: ID {producto_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando producto: {e}")
            return False

    def delete_producto(self, producto_id: int) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id=?", (producto_id,))
            conn.commit()
            conn.close()
            logger.info(f"✅ Producto eliminado: ID {producto_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando producto: {e}")
            return False

    def get_negocios(self) -> List[Dict]:
        try:
            conn = self.get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, descripcion, direccion, telefono, email, activo
                FROM comerciantes 
                ORDER BY nombre
            """)
            negocios = []
            for row in cursor.fetchall():
                negocios.append({'id': row[0],'nombre': row[1],'descripcion': row[2],'direccion': row[3],'telefono': row[4],'email': row[5],'activo': bool(row[6])})
            conn.close()
            logger.info(f"✅ Negocios obtenidos: {len(negocios)}")
            return negocios
        except Exception as e:
            logger.error(f"Error obteniendo negocios: {e}")
            return []

    def create_negocio(self, negocio_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO comerciantes (nombre, descripcion, direccion, telefono, email, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                negocio_data.get('nombre'),
                negocio_data.get('descripcion'),
                negocio_data.get('direccion'),
                negocio_data.get('telefono'),
                negocio_data.get('email'),
                negocio_data.get('activo', True)
            ))
            conn.commit()
            conn.close()
            logger.info(f"✅ Negocio creado: {negocio_data.get('nombre')}")
            return True
        except Exception as e:
            logger.error(f"Error creando negocio: {e}")
            return False

    def update_negocio(self, negocio_id: int, negocio_data: Dict) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE comerciantes 
                SET nombre=?, descripcion=?, direccion=?, telefono=?, email=?, activo=?
                WHERE id=?
            """, (
                negocio_data.get('nombre'),
                negocio_data.get('descripcion'),
                negocio_data.get('direccion'),
                negocio_data.get('telefono'),
                negocio_data.get('email'),
                negocio_data.get('activo'),
                negocio_id
            ))
            conn.commit()
            conn.close()
            logger.info(f"✅ Negocio actualizado: ID {negocio_id}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando negocio: {e}")
            return False

    def delete_negocio(self, negocio_id: int) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("DELETE FROM comerciantes WHERE id=?", (negocio_id,))
            conn.commit()
            conn.close()
            logger.info(f"✅ Negocio eliminado: ID {negocio_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando negocio: {e}")
            return False

    def get_precios(self, negocio_id: Optional[int] = None) -> List[Dict]:
        try:
            conn = self.get_connection()
            if not conn:
                return []
            cursor = conn.cursor()
            if negocio_id:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.precio, c.nombre as negocio_nombre
                    FROM productos p
                    JOIN comerciantes c ON p.negocio_id = c.id
                    WHERE p.negocio_id = ?
                    ORDER BY p.nombre
                """, (negocio_id,))
            else:
                cursor.execute("""
                    SELECT p.id, p.nombre, p.precio, c.nombre as negocio_nombre
                    FROM productos p
                    JOIN comerciantes c ON p.negocio_id = c.id
                    ORDER BY c.nombre, p.nombre
                """)
            precios = []
            for row in cursor.fetchall():
                precios.append({'id': row[0],'producto_nombre': row[1],'precio': row[2],'negocio_nombre': row[3]})
            conn.close()
            logger.info(f"✅ Precios obtenidos: {len(precios)}")
            return precios
        except Exception as e:
            logger.error(f"Error obteniendo precios: {e}")
            return []

    def update_precio(self, producto_id: int, nuevo_precio: float) -> bool:
        try:
            conn = self.get_connection()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos 
                SET precio = ?
                WHERE id = ?
            """, (nuevo_precio, producto_id))
            conn.commit()
            conn.close()
            logger.info(f"✅ Precio actualizado: Producto ID {producto_id} = ${nuevo_precio}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando precio: {e}")
            return False

    def _read_local_json(self) -> Dict:
        try:
            with open('productos.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo productos.json: {e}")
            return {}

    def _write_local_json(self, data: Dict) -> bool:
        try:
            with open('productos.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error escribiendo productos.json: {e}")
            return False

    def get_items(self, kind: str) -> List[Dict]:
        kind = (kind or '').lower()
        try:
            if kind == 'productos':
                return self.get_productos()
            if kind == 'negocios':
                return self.get_negocios()
            if kind == 'ofertas':
                return self.get_ofertas()
            if kind == 'sucursales':
                data = self._read_local_json()
                sucursales = data.get('sucursales', {})
                out = []
                for negocio_id, suc_dict in sucursales.items():
                    for sid, suc in suc_dict.items():
                        suc['id'] = sid
                        suc['negocio_id'] = negocio_id
                        out.append(suc)
                return out
            logger.warning(f"Tipo no soportado en get_items: {kind}")
            return []
        except Exception as e:
            logger.error(f"Error en get_items({kind}): {e}")
            return []

    def create_item(self, kind: str, data: Dict) -> bool:
        kind = (kind or '').lower()
        try:
            if kind == 'productos':
                return self.create_producto(data)
            if kind == 'negocios':
                return self.create_negocio(data)
            if kind == 'ofertas':
                return self.create_oferta(data)
            if kind == 'sucursales':
                contenido = self._read_local_json()
                sucursales = contenido.setdefault('sucursales', {})
                negocio_id = str(data.get('negocio_id') or data.get('negocio'))
                if not negocio_id:
                    raise ValueError('negocio_id requerido para sucursal')
                sucursales.setdefault(negocio_id, {})
                from uuid import uuid4
                sid = str(data.get('id') or uuid4())
                suc = {
                    'id': sid,
                    'nombre': data.get('nombre', ''),
                    'direccion': data.get('direccion', ''),
                    'telefono': data.get('telefono', ''),
                    'activo': data.get('activo', True),
                }
                sucursales[negocio_id][sid] = suc
                if self._write_local_json(contenido):
                    logger.info(f"✅ Sucursal creada: {suc.get('nombre')} (negocio {negocio_id})")
                    return True
                return False
            logger.warning(f"Tipo no soportado en create_item: {kind}")
            return False
        except Exception as e:
            logger.error(f"Error en create_item({kind}): {e}")
            return False

    def update_item(self, kind: str, item_id: Any, data: Dict) -> bool:
        kind = (kind or '').lower()
        try:
            if kind == 'productos':
                return self.update_producto(int(item_id), data)
            if kind == 'negocios':
                return self.update_negocio(int(item_id), data)
            if kind == 'ofertas':
                return self.update_oferta(int(item_id), data)
            if kind == 'sucursales':
                contenido = self._read_local_json()
                sucursales = contenido.get('sucursales', {})
                for negocio_id, suc_dict in sucursales.items():
                    if str(item_id) in suc_dict:
                        suc = suc_dict[str(item_id)]
                        suc.update({k: v for k, v in data.items() if k != 'id'})
                        if self._write_local_json(contenido):
                            logger.info(f"✅ Sucursal actualizada: {item_id}")
                            return True
                        return False
                logger.warning(f"Sucursal no encontrada: {item_id}")
                return False
            logger.warning(f"Tipo no soportado en update_item: {kind}")
            return False
        except Exception as e:
            logger.error(f"Error en update_item({kind}): {e}")
            return False

    def delete_item(self, kind: str, item_id: Any) -> bool:
        kind = (kind or '').lower()
        try:
            if kind == 'productos':
                return self.delete_producto(int(item_id))
            if kind == 'negocios':
                return self.delete_negocio(int(item_id))
            if kind == 'ofertas':
                return self.delete_oferta(int(item_id))
            if kind == 'sucursales':
                contenido = self._read_local_json()
                sucursales = contenido.get('sucursales', {})
                for negocio_id, suc_dict in list(sucursales.items()):
                    if str(item_id) in suc_dict:
                        del suc_dict[str(item_id)]
                        if self._write_local_json(contenido):
                            logger.info(f"✅ Sucursal eliminada: {item_id}")
                            return True
                        return False
                logger.warning(f"Sucursal no encontrada: {item_id}")
                return False
            logger.warning(f"Tipo no soportado en delete_item: {kind}")
            return False
        except Exception as e:
            logger.error(f"Error en delete_item({kind}): {e}")
            return False
