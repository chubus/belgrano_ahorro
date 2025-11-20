#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capa de acceso a datos para Belgrano Ahorro.
Totalmente preparada para PostgreSQL en Render (tablas: negocios, categorias,
productos, sucursales, ofertas, usuarios, pedidos, items_pedido, tokens_recuperacion).
"""

import hashlib
import logging
import secrets
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text

try:
    from db_abstraction import get_db_connection, engine
except ImportError as exc:
    raise ImportError("[DB] No se pudo importar db_abstraction. Verifica la configuración.") from exc

logger = logging.getLogger(__name__)

if engine:
    logger.info("[DB] Motor PostgreSQL inicializado correctamente.")
else:
    logger.warning("[DB] No se detectó engine de PostgreSQL. Revisa db_abstraction.")


@contextmanager
def session_scope(commit: bool = False):
    """
    Context manager para manejar sesiones de SQLAlchemy/psycopg2 de forma segura.
    commit=False para lecturas, True para escrituras.
    """
    session = get_db_connection()
    try:
        yield session
        if commit:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# =========================================================
# UTILIDADES DE CONTRASEÑAS
# =========================================================

def hash_password(password: str) -> str:
    """Generar hash de contraseña (SHA-256 con salt)."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return f"{salt}${password_hash}"


def verificar_password(password: str, hashed: str) -> bool:
    """Verificar contraseña contra hash almacenado."""
    try:
        salt, stored_hash = hashed.split("$", 1)
        password_hash = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
        return password_hash == stored_hash
    except Exception as exc:
        logger.warning(f"[DB] Error verificando contraseña: {exc}")
        return False


# =========================================================
# USUARIOS
# =========================================================

def crear_usuario(
    nombre: str,
    apellido: str,
    email: str,
    password: str,
    telefono: Optional[str] = None,
    direccion: Optional[str] = None,
    rol: str = "cliente",
) -> Dict[str, object]:
    """Crear un nuevo usuario."""
    try:
        with session_scope(commit=True) as session:
            existente = session.execute(
                text("SELECT id FROM usuarios WHERE email = :email"),
                {"email": email},
            ).fetchone()

            if existente:
                return {"exito": False, "mensaje": "El email ya está registrado"}

            password_hash = hash_password(password)
            nombre_completo = f"{nombre} {apellido}".strip()

            resultado = session.execute(
                text(
                    """
                    INSERT INTO usuarios (
                        nombre, apellido, email, password_hash, telefono, direccion, rol, activo
                    )
                    VALUES (:nombre, :apellido, :email, :password_hash, :telefono, :direccion, :rol, TRUE)
                    RETURNING id
                    """
                ),
                {
                    "nombre": nombre_completo or nombre or "",
                    "apellido": apellido or "",
                    "email": email,
                    "password_hash": password_hash,
                    "telefono": telefono,
                    "direccion": direccion,
                    "rol": rol or "cliente",
                },
            )

            row = resultado.fetchone()
            usuario_id = row[0] if row else None

            logger.info(f"[DB] ✅ Usuario creado: {email} (ID: {usuario_id})")
            return {"exito": True, "usuario_id": usuario_id, "mensaje": "Usuario creado exitosamente"}
    except Exception as exc:
        logger.error(f"[DB] ❌ Error creando usuario: {exc}", exc_info=True)
        return {"exito": False, "mensaje": f"Error al crear usuario: {exc}"}


def verificar_usuario(email: str, password: str) -> Dict[str, object]:
    """Verificar credenciales de usuario."""
    try:
        with session_scope(commit=False) as session:
            usuario = session.execute(
                text(
                    """
                    SELECT id, nombre, email, password_hash, activo
                    FROM usuarios
                    WHERE email = :email
                    """
                ),
                {"email": email},
            ).fetchone()

            if usuario and verificar_password(password, usuario[3]):
                return {
                    "exito": True,
                    "usuario": {
                        "id": usuario[0],
                        "nombre": usuario[1] or "",
                        "email": usuario[2],
                    },
                }

            return {"exito": False, "mensaje": "Credenciales incorrectas"}
    except Exception as exc:
        logger.error(f"[DB] ❌ Error verificando usuario: {exc}", exc_info=True)
        return {"exito": False, "mensaje": "Error interno del servidor"}


def buscar_usuario_por_email(email: str) -> Optional[Dict[str, object]]:
    """Buscar usuario por email."""
    try:
        with session_scope(commit=False) as session:
            usuario = session.execute(
                text(
                    """
                    SELECT id, nombre, email, telefono, activo
                    FROM usuarios
                    WHERE email = :email
                    """
                ),
                {"email": email},
            ).fetchone()

            if not usuario:
                return None

            return {
                "id": usuario[0],
                "nombre": usuario[1] or "",
                "email": usuario[2],
                "telefono": usuario[3] or "",
                "activo": bool(usuario[4]),
            }
    except Exception as exc:
        logger.error(f"[DB] ❌ Error buscando usuario: {exc}", exc_info=True)
        return None


def obtener_usuario_por_id(usuario_id: int) -> Optional[Dict[str, object]]:
    """Obtener un usuario por su ID."""
    try:
        with session_scope(commit=False) as session:
            usuario = session.execute(
                text(
                    """
                    SELECT id, nombre, email, telefono, activo, fecha_creacion
                    FROM usuarios
                    WHERE id = :id
                    """
                ),
                {"id": usuario_id},
            ).fetchone()

            if not usuario:
                return None

            return {
                "id": usuario[0],
                "nombre": usuario[1] or "",
                "email": usuario[2],
                "telefono": usuario[3] or "",
                "activo": bool(usuario[4]),
                "fecha_registro": str(usuario[5]) if usuario[5] else None,
            }
    except Exception as exc:
        logger.error(f"[DB] ❌ Error obteniendo usuario por ID: {exc}", exc_info=True)
        return None


def actualizar_usuario(usuario_id: int, nombre: str, telefono: str, direccion: Optional[str]) -> bool:
    """Actualizar datos del usuario."""
    try:
        with session_scope(commit=True) as session:
            session.execute(
                text(
                    """
                    UPDATE usuarios
                    SET nombre = :nombre,
                        telefono = :telefono,
                        direccion = :direccion,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = :id
                    """
                ),
                {
                    "id": usuario_id,
                    "nombre": nombre,
                    "telefono": telefono,
                    "direccion": direccion,
                },
            )
        return True
    except Exception as exc:
        logger.error(f"[DB] ❌ Error actualizando usuario: {exc}", exc_info=True)
        return False


def cambiar_password(usuario_id: int, password_actual: str, password_nuevo: str) -> bool:
    """Cambiar contraseña verificando la actual."""
    try:
        with session_scope(commit=True) as session:
            row = session.execute(
                text("SELECT password_hash FROM usuarios WHERE id = :id"),
                {"id": usuario_id},
            ).fetchone()

            if not row or not verificar_password(password_actual, row[0]):
                return False

            password_hash = hash_password(password_nuevo)
            session.execute(
                text(
                    """
                    UPDATE usuarios
                    SET password_hash = :password_hash,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = :id
                    """
                ),
                {"id": usuario_id, "password_hash": password_hash},
            )
        return True
    except Exception as exc:
        logger.error(f"[DB] ❌ Error cambiando password: {exc}", exc_info=True)
        return False


# =========================================================
# RECUPERACIÓN DE CONTRASEÑA
# =========================================================

def _ensure_tokens_table(session) -> None:
    """Asegura la existencia de tokens_recuperacion (compatibilidad)."""
    session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS tokens_recuperacion (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                token TEXT UNIQUE NOT NULL,
                expiracion TIMESTAMP NOT NULL,
                usado BOOLEAN DEFAULT FALSE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def guardar_token_recuperacion(usuario_id: int, token: str, expiracion: datetime) -> bool:
    """Guardar token de recuperación."""
    try:
        with session_scope(commit=True) as session:
            _ensure_tokens_table(session)
            session.execute(
                text(
                    """
                    INSERT INTO tokens_recuperacion (usuario_id, token, expiracion)
                    VALUES (:usuario_id, :token, :expiracion)
                    """
                ),
                {"usuario_id": usuario_id, "token": token, "expiracion": expiracion},
            )
        return True
    except Exception as exc:
        logger.error(f"[DB] ❌ Error guardando token: {exc}", exc_info=True)
        return False


def verificar_token_recuperacion(email: str, token: str) -> Dict[str, object]:
    """Verificar un token de recuperación."""
    try:
        with session_scope(commit=False) as session:
            row = session.execute(
                text(
                    """
                    SELECT t.id, t.usuario_id, t.expiracion, t.usado
                    FROM tokens_recuperacion t
                    JOIN usuarios u ON t.usuario_id = u.id
                    WHERE u.email = :email AND t.token = :token
                    """
                ),
                {"email": email, "token": token},
            ).fetchone()

            if row and not row[3]:
                return {"exito": True, "token_id": row[0], "usuario_id": row[1]}

            return {"exito": False, "mensaje": "Token inválido o expirado"}
    except Exception as exc:
        logger.error(f"[DB] ❌ Error verificando token: {exc}", exc_info=True)
        return {"exito": False, "mensaje": "Error interno"}


def cambiar_password_por_token(email: str, token_id: int, nueva_password: str) -> bool:
    """Cambiar password a través de un token válido."""
    try:
        with session_scope(commit=True) as session:
            row = session.execute(
                text(
                    """
                    SELECT u.id
                    FROM usuarios u
                    JOIN tokens_recuperacion t ON u.id = t.usuario_id
                    WHERE t.id = :token_id AND u.email = :email AND t.usado = FALSE
                    """
                ),
                {"token_id": token_id, "email": email},
            ).fetchone()

            if not row:
                return False

            password_hash = hash_password(nueva_password)

            session.execute(
                text("UPDATE usuarios SET password_hash = :password_hash WHERE id = :id"),
                {"password_hash": password_hash, "id": row[0]},
            )
            session.execute(
                text("UPDATE tokens_recuperacion SET usado = TRUE WHERE id = :id"),
                {"id": token_id},
            )
        return True
    except Exception as exc:
        logger.error(f"[DB] ❌ Error cambiando password por token: {exc}", exc_info=True)
        return False


# =========================================================
# PEDIDOS
# =========================================================

def guardar_pedido(
    usuario_id: int,
    numero_pedido: str,
    total: float,
    metodo_pago: str,
    direccion_entrega: str,
    notas: Optional[str],
) -> Optional[int]:
    """Crear pedido y retornar su ID."""
    try:
        with session_scope(commit=True) as session:
            resultado = session.execute(
                text(
                    """
                    INSERT INTO pedidos (usuario_id, numero_pedido, total, metodo_pago, direccion_entrega, notas)
                    VALUES (:usuario_id, :numero_pedido, :total, :metodo_pago, :direccion_entrega, :notas)
                    RETURNING id
                    """
                ),
                {
                    "usuario_id": usuario_id,
                    "numero_pedido": numero_pedido,
                    "total": total,
                    "metodo_pago": metodo_pago,
                    "direccion_entrega": direccion_entrega,
                    "notas": notas,
                },
            )

            row = resultado.fetchone()
            return row[0] if row else None
    except Exception as exc:
        logger.error(f"[DB] ❌ Error guardando pedido: {exc}", exc_info=True)
        return None


def guardar_items_pedido(pedido_id: int, items: List[Dict[str, object]]) -> bool:
    """Guardar items asociados a un pedido."""
    try:
        with session_scope(commit=True) as session:
            for item in items:
                session.execute(
                    text(
                        """
                        INSERT INTO items_pedido (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (:pedido_id, :producto_id, :cantidad, :precio_unitario, :subtotal)
                        """
                    ),
                    {
                        "pedido_id": pedido_id,
                        "producto_id": item["producto_id"],
                        "cantidad": item["cantidad"],
                        "precio_unitario": item["precio_unitario"],
                        "subtotal": item["subtotal"],
                    },
                )
        return True
    except Exception as exc:
        logger.error(f"[DB] ❌ Error guardando items de pedido: {exc}", exc_info=True)
        return False


def obtener_pedidos_usuario(usuario_id: int) -> List[Dict[str, object]]:
    """Lista de pedidos de un usuario."""
    try:
        with session_scope(commit=False) as session:
            resultados = session.execute(
                text(
                    """
                    SELECT id, numero_pedido, fecha_creacion, total, estado
                    FROM pedidos
                    WHERE usuario_id = :usuario_id
                    ORDER BY fecha_creacion DESC
                    """
                ),
                {"usuario_id": usuario_id},
            )

            pedidos = []
            for row in resultados.fetchall():
                pedidos.append(
                    {
                        "id": row[0],
                        "numero_pedido": row[1],
                        "fecha": str(row[2]) if row[2] else "",
                        "total": float(row[3]) if row[3] else 0.0,
                        "estado": row[4] or "pendiente",
                    }
                )
            return pedidos
    except Exception as exc:
        logger.error(f"[DB] ❌ Error obteniendo pedidos: {exc}", exc_info=True)
        return []


def obtener_pedido_completo(pedido_id: int) -> Optional[Dict[str, object]]:
    """Obtener pedido completo con items."""
    try:
        with session_scope(commit=False) as session:
            pedido_row = session.execute(
                text(
                    """
                    SELECT id, numero_pedido, fecha_creacion, total, estado, metodo_pago, direccion_entrega, notas
                    FROM pedidos
                    WHERE id = :id
                    """
                ),
                {"id": pedido_id},
            ).fetchone()

            if not pedido_row:
                return None

            pedido = {
                "id": pedido_row[0],
                "numero_pedido": pedido_row[1],
                "fecha": str(pedido_row[2]) if pedido_row[2] else "",
                "total": float(pedido_row[3]) if pedido_row[3] else 0.0,
                "estado": pedido_row[4] or "pendiente",
                "metodo_pago": pedido_row[5] or "",
                "direccion_entrega": pedido_row[6] or "",
                "notas": pedido_row[7] or "",
                "items": [],
            }

            items_result = session.execute(
                text(
                    """
                    SELECT pi.producto_id,
                           pi.cantidad,
                           pi.precio_unitario,
                           pi.subtotal,
                           p.nombre,
                           p.imagen
                    FROM items_pedido pi
                    JOIN productos p ON pi.producto_id = p.id
                    WHERE pi.pedido_id = :pedido_id
                    """
                ),
                {"pedido_id": pedido_id},
            )

            for row in items_result.fetchall():
                pedido["items"].append(
                    {
                        "producto_id": row[0],
                        "cantidad": row[1],
                        "precio_unitario": float(row[2]) if row[2] else 0.0,
                        "subtotal": float(row[3]) if row[3] else 0.0,
                        "nombre": row[4] or "",
                        "imagen": row[5] or "",
                    }
                )

            return pedido
    except Exception as exc:
        logger.error(f"[DB] ❌ Error obteniendo pedido completo: {exc}", exc_info=True)
        return None


def generar_numero_pedido() -> str:
    """Generar un identificador único para pedidos."""
    import uuid

    fecha = datetime.now().strftime("%Y%m%d")
    codigo = str(uuid.uuid4())[:8].upper()
    return f"PED-{fecha}-{codigo}"


# =========================================================
# STOCK
# =========================================================

def validar_stock_producto(producto_id: int, cantidad_solicitada: int) -> Tuple[bool, object]:
    """Validar stock de un producto específico."""
    try:
        with session_scope(commit=False) as session:
            row = session.execute(
                text(
                    """
                    SELECT stock
                    FROM productos
                    WHERE id = :id AND activo = TRUE
                    """
                ),
                {"id": producto_id},
            ).fetchone()

            if not row:
                return False, "Producto no encontrado o inactivo"

            stock_disponible = int(row[0]) if row[0] is not None else 0

            if stock_disponible < cantidad_solicitada:
                return False, f"Stock insuficiente. Disponible: {stock_disponible}, Solicitado: {cantidad_solicitada}"

            return True, stock_disponible
    except Exception as exc:
        logger.error(f"[DB] ❌ Error validando stock: {exc}", exc_info=True)
        return False, f"Error al validar stock: {exc}"


def validar_stock_carrito(carrito_items: List[Dict[str, object]]) -> Tuple[bool, List[str], List[Dict[str, object]]]:
    """Validar stock para todos los items del carrito."""
    errores: List[str] = []
    productos_validos: List[Dict[str, object]] = []

    for item in carrito_items:
        producto_id = item.get("producto_id") or item.get("producto", {}).get("id")
        cantidad = item.get("cantidad", 0)

        if not producto_id:
            errores.append("Producto sin ID válido")
            continue

        valido, resultado = validar_stock_producto(producto_id, cantidad)
        if not valido:
            nombre = item.get("producto", {}).get("nombre", f"Producto ID {producto_id}")
            errores.append(f"{nombre}: {resultado}")
        else:
            productos_validos.append(
                {"producto_id": producto_id, "cantidad": cantidad, "stock_disponible": resultado}
            )

    return len(errores) == 0, errores, productos_validos


def actualizar_stock_producto(producto_id: int, cantidad_vendida: int) -> Tuple[bool, object]:
    """Descontar stock de un producto."""
    try:
        with session_scope(commit=True) as session:
            row = session.execute(
                text("SELECT stock FROM productos WHERE id = :id"),
                {"id": producto_id},
            ).fetchone()

            if not row:
                return False, "Producto no encontrado"

            stock_actual = int(row[0]) if row[0] is not None else 0
            nuevo_stock = max(0, stock_actual - cantidad_vendida)

            session.execute(
                text(
                    """
                    UPDATE productos
                    SET stock = :stock,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = :id
                    """
                ),
                {"stock": nuevo_stock, "id": producto_id},
            )

            logger.info(
                f"[DB] ✅ Stock actualizado - Producto {producto_id}: {stock_actual} -> {nuevo_stock} (vendido {cantidad_vendida})"
            )
            return True, nuevo_stock
    except Exception as exc:
        logger.error(f"[DB] ❌ Error actualizando stock: {exc}", exc_info=True)
        return False, f"Error al actualizar stock: {exc}"


def actualizar_stock_carrito(carrito_items: List[Dict[str, object]]) -> Tuple[bool, List[Dict[str, object]], List[str]]:
    """Actualizar el stock de todos los productos comprados."""
    resultados: List[Dict[str, object]] = []
    errores: List[str] = []

    for item in carrito_items:
        producto_id = item.get("producto_id") or item.get("producto", {}).get("id")
        cantidad = item.get("cantidad", 0)

        if not producto_id:
            errores.append("Producto sin ID válido")
            continue

        exito, respuesta = actualizar_stock_producto(producto_id, cantidad)
        if exito:
            resultados.append({"producto_id": producto_id, "cantidad_vendida": cantidad, "nuevo_stock": respuesta})
        else:
            errores.append(f"Producto {producto_id}: {respuesta}")

    return len(errores) == 0, resultados, errores


# =========================================================
# FUNCIONES DEPRECADAS (compatibilidad)
# =========================================================

def inicializar_base_datos():
    """Mantener compatibilidad con scripts anteriores."""
    logger.warning("[DB] inicializar_base_datos() está deprecado. Usa init_db.py")
    try:
        from init_db import init_db as _init_db

        _init_db()
    except ImportError:
        logger.error("[DB] No se pudo importar init_db")


def crear_base_datos():
    """Mantener compatibilidad con scripts anteriores."""
    logger.warning("[DB] crear_base_datos() está deprecado. Usa init_db.py")
    try:
        from init_db import init_db as _init_db

        _init_db()
    except ImportError:
        logger.error("[DB] No se pudo importar init_db")
