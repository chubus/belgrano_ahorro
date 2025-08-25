# app.py
# =================================================================
# ARCHIVO PRINCIPAL DE LA APLICACIÓN FLASK - BELGRANO AHORRO
# =================================================================
# 
# DESCRIPCIÓN:
# Este archivo contiene toda la lógica de la aplicación web, incluyendo:
# - Rutas y endpoints de la aplicación
# - Gestión de usuarios y autenticación
# - Manejo de productos, ofertas y categorías
# - Procesamiento de carrito y pedidos
# - Funciones auxiliares para el sistema
#
# MANTENIMIENTO:
# - Para agregar nuevas rutas: agregar nuevas funciones @app.route()
# - Para modificar productos: editar productos.json (ver GUIA_MANTENIMIENTO.md)
# - Para cambiar ofertas: modificar sección "ofertas" en productos.json
# - Para agregar negocios: agregar en sección "negocios" de productos.json
#
# EJECUCIÓN:
# python app.py
# 
# DEPENDENCIAS:
# - Flask (framework web)
# - db.py (módulo de base de datos)
# - productos.json (datos de productos, ofertas, categorías)
# =================================================================

import json
import logging
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import re
import secrets
import hashlib

# Importar base de datos con manejo de errores
try:
    import db as database
    print("✅ Módulo db importado correctamente")
    print("DEBUG: database =", database)
    print("DEBUG: database.crear_usuario =", getattr(database, 'crear_usuario', None))
except Exception as e:
    print(f"❌ Error importando db: {e}")
    raise  # Detén la app si el import falla

# Configurar logging para ver mensajes de debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la instancia de Flask
app = Flask(__name__)
app.secret_key = 'belgrano_ahorro_secret_key_2025'  # Clave secreta para sesiones

# =================================================================
# FUNCIONES DE BÚSQUEDA Y FILTRADO DE PRODUCTOS
# =================================================================

def buscar_productos(productos, busqueda):
    """
    Buscar productos por nombre, descripción o categoría
    
    PARÁMETROS:
    - productos: lista de productos a buscar
    - busqueda: texto de búsqueda ingresado por el usuario
    
    RETORNA:
    - Lista de productos que coinciden con la búsqueda
    
    MANTENIMIENTO:
    - Para agregar más campos de búsqueda: agregar condiciones en el bucle
    - Para cambiar la lógica de búsqueda: modificar las comparaciones
    """
    if not busqueda:
        return productos
    
    busqueda = busqueda.lower()
    resultados = []
    
    for producto in productos:
        nombre = producto.get('nombre', '').lower()
        if busqueda in nombre:
            resultados.append(producto)
    
    return resultados

# =================================================================
# FUNCIONES DE CARGA DE DATOS DESDE JSON
# =================================================================

def cargar_productos():
    """
    Cargar productos desde el archivo productos.json
    
    RETORNA:
    - Lista de productos activos
    
    MANTENIMIENTO:
    - Para agregar productos: editar productos.json (ver GUIA_MANTENIMIENTO.md)
    - Para cambiar estructura: modificar el acceso a data.get('productos', [])
    - Para agregar validaciones: agregar condiciones antes del return
    """
    try:
        with open('productos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            productos = data.get('productos', [])
            logger.info(f"Productos cargados correctamente: {len(productos)} productos")
            return productos
    except Exception as e:
        logger.error(f"Error al cargar productos: {e}")
        return []

def cargar_datos_completos():
    """
    Cargar todos los datos del JSON incluyendo negocios, categorías y ofertas
    
    RETORNA:
    - Diccionario completo con todos los datos del sistema
    
    MANTENIMIENTO:
    - Para agregar nuevas secciones: agregar en productos.json
    - Para cambiar estructura: modificar el acceso a los datos
    """
    try:
        with open('productos.json', 'r', encoding='utf-8') as file:
            datos = json.load(file)
        return datos
    except Exception as e:
        logger.error(f"Error al cargar datos completos: {e}")
        return {}

def obtener_negocios():
    """
    Obtener lista de negocios activos
    
    RETORNA:
    - Diccionario con todos los negocios del sistema
    
    MANTENIMIENTO:
    - Para agregar negocios: editar sección "negocios" en productos.json
    - Para cambiar estado: modificar "activo": true/false en el negocio
    """
    datos = cargar_datos_completos()
    return datos.get('negocios', {})

def obtener_categorias():
    """
    Obtener lista de categorías
    
    RETORNA:
    - Diccionario con todas las categorías del sistema
    
    MANTENIMIENTO:
    - Para agregar categorías: editar sección "categorias" en productos.json
    - Para cambiar iconos: modificar campo "icono" en la categoría
    """
    datos = cargar_datos_completos()
    return datos.get('categorias', {})

def obtener_ofertas():
    """
    Obtener ofertas activas
    
    RETORNA:
    - Diccionario con todas las ofertas del sistema
    
    MANTENIMIENTO:
    - Para agregar ofertas: editar sección "ofertas" en productos.json
    - Para cambiar estado: modificar "activa": true/false en la oferta
    """
    datos = cargar_datos_completos()
    return datos.get('ofertas', {})

def obtener_sucursales():
    """
    Obtener todas las sucursales del sistema
    
    RETORNA:
    - Diccionario con todas las sucursales organizadas por negocio
    
    MANTENIMIENTO:
    - Para agregar sucursales: editar sección "sucursales" en productos.json
    - Para cambiar estado: modificar "activo": true/false en la sucursal
    """
    datos = cargar_datos_completos()
    return datos.get('sucursales', {})

def obtener_sucursales_por_negocio(negocio_id):
    """
    Obtener sucursales de un negocio específico
    
    PARÁMETROS:
    - negocio_id: ID del negocio
    
    RETORNA:
    - Lista de sucursales activas del negocio
    """
    sucursales = obtener_sucursales()
    if negocio_id in sucursales:
        return [suc for suc in sucursales[negocio_id].values() if suc.get('activo', True)]
    return []

def obtener_productos_por_sucursal(negocio_id, sucursal_id):
    """
    Obtener productos disponibles en una sucursal específica
    
    PARÁMETROS:
    - negocio_id: ID del negocio
    - sucursal_id: ID de la sucursal
    
    RETORNA:
    - Lista de productos disponibles en la sucursal
    """
    datos = cargar_datos_completos()
    productos = datos.get('productos', [])
    
    productos_sucursal = []
    for producto in productos:
        if (producto.get('negocio') == negocio_id and 
            producto.get('activo', True) and
            'sucursales' in producto and
            sucursal_id in producto['sucursales']):
            productos_sucursal.append(producto)
    
    return productos_sucursal

def obtener_productos_por_negocio(negocio_id):
    """Obtener productos de un negocio específico"""
    datos = cargar_datos_completos()
    productos = datos.get('productos', [])
    return [p for p in productos if p.get('negocio') == negocio_id and p.get('activo', True)]

def obtener_productos_destacados():
    """Obtener productos destacados de todos los negocios"""
    datos = cargar_datos_completos()
    productos = datos.get('productos', [])
    return [p for p in productos if p.get('destacado', False) and p.get('activo', True)]

def obtener_ofertas_activas():
    """Obtener ofertas activas con información de productos"""
    datos = cargar_datos_completos()
    ofertas = datos.get('ofertas', {})
    productos = datos.get('productos', [])
    
    ofertas_activas = {}
    for negocio, ofertas_negocio in ofertas.items():
        ofertas_activas[negocio] = []
        for oferta in ofertas_negocio:
            # Agregar información de productos a la oferta
            productos_oferta = []
            for producto_id in oferta.get('productos', []):
                producto = next((p for p in productos if p['id'] == producto_id), None)
                if producto:
                    productos_oferta.append(producto)
            
            oferta['productos_info'] = productos_oferta
            ofertas_activas[negocio].append(oferta)
    
    return ofertas_activas

# ==========================================
# BASE DE DATOS SIMPLE (USUARIOS Y PEDIDOS)
# ==========================================
# En una aplicación real, usarías una base de datos como SQLite o MySQL
# Por ahora usamos diccionarios en memoria para simplicidad

# usuarios = {
#     'admin@belgrano.com': {
#         'password': generate_password_hash('admin123'),
#         'nombre': 'Administrador',
#         'email': 'admin@belgrano.com',
#         'rol': 'admin'
#     }
# }

# Almacenar pedidos (en una app real sería una base de datos)
# pedidos = {}

# ==========================================
# CARGA DE DATOS
# ==========================================
# Esta sección carga los productos desde el archivo JSON
# Si hay algún error, crea una lista vacía para evitar que la app falle
try:
    with open("productos.json", "r", encoding="utf-8") as f:
        productos = json.load(f)
    logger.info(f"Productos cargados correctamente: {len(productos['productos'])} productos")
except Exception as e:
    logger.error(f"Error al cargar productos.json: {e}")
    productos = {"productos": []}  # Lista vacía para evitar fallos

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def obtener_producto_por_id(producto_id):
    """
    Busca un producto por su ID en la lista de productos
    """
    for producto in productos['productos']:
        if str(producto['id']) == str(producto_id):
            return producto
    return None

def calcular_total_carrito():
    """
    Calcula el total del carrito de compras
    """
    total = 0
    if 'carrito' in session:
        for producto_id, cantidad in session['carrito'].items():
            producto = obtener_producto_por_id(producto_id)
            if producto:
                total += producto['precio'] * cantidad
    return total

def usuario_logueado():
    """
    Verifica si hay un usuario logueado
    """
    return 'usuario_id' in session

def obtener_usuario_actual():
    """
    Obtener información del usuario actualmente logueado
    """
    if not usuario_logueado():
        return None
    
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return None
    
    if database is None:
        return None
    
    return database.obtener_usuario_por_id(usuario_id)

def generar_numero_pedido():
    """
    Genera un número único de pedido
    """
    fecha = datetime.now().strftime("%Y%m%d")
    codigo = str(uuid.uuid4())[:8].upper()
    return f"PED-{fecha}-{codigo}"

# ==========================================
# FUNCIONES DE RECUPERACIÓN DE CONTRASEÑA
# ==========================================

def generar_token_recuperacion():
    """Genera un token seguro para recuperación de contraseña"""
    return secrets.token_urlsafe(32)

def sanitizar_email(email):
    """Sanitiza y valida el formato del email"""
    if not email:
        return None, "Email es requerido"
    
    email = email.strip().lower()
    
    # Validación básica de formato
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return None, "Formato de email inválido"
    
    # Sanitización adicional
    email = re.sub(r'[<>"\']', '', email)  # Remover caracteres peligrosos
    
    return email, None

def sanitizar_codigo(codigo):
    """Sanitiza el código de verificación"""
    if not codigo:
        return None, "Código es requerido"
    
    codigo = codigo.strip()
    
    # Solo permitir números y letras
    if not re.match(r"^[A-Za-z0-9]{6,8}$", codigo):
        return None, "Código inválido"
    
    return codigo, None

# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================

@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    RUTA DE LOGIN - Página de inicio de sesión
    """
    if usuario_logueado():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Debug logs
        logger.info(f"Intento de login - Email: {email}")
        
        if not email or not password:
            logger.warning("Login fallido - Campos incompletos")
            flash('Por favor completa todos los campos', 'danger')
            return render_template('login.html')
        
        # Verificar credenciales
        if database is None:
            logger.error("Login fallido - Database es None")
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template('login.html')
        
        logger.info("Intentando verificar credenciales...")
        resultado = database.verificar_usuario(email, password)
        logger.info(f"Resultado de verificar_usuario: {resultado}")
        
        if isinstance(resultado, dict) and resultado.get('exito'):
            # Login exitoso
            usuario = resultado.get('usuario', {})
            session['usuario_id'] = usuario.get('id')
            session['usuario_nombre'] = usuario.get('nombre')
            session['usuario_email'] = usuario.get('email')
            session['usuario_rol'] = usuario.get('rol', 'cliente')
            
            logger.info(f"Login exitoso - Usuario: {usuario.get('nombre')}, ID: {usuario.get('id')}")
            flash(f'¡Bienvenido, {usuario.get("nombre", "Usuario")}!', 'success')
            return redirect(url_for('index'))
        else:
            # Login fallido
            logger.warning(f"Login fallido - Email: {email}")
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    RUTA DE REGISTRO - Nueva página de registro con validación mejorada
    """
    if usuario_logueado():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmar_password = request.form.get('confirmar_password')
        telefono = request.form.get('telefono', '')
        direccion = request.form.get('direccion', '')
        terminos = request.form.get('terminos')
        
        # Debug logs
        logger.info(f"Intento de registro - Email: {email}, Nombre: {nombre}, Apellido: {apellido}")
        
        # Validaciones
        if not all([nombre, apellido, email, password, confirmar_password]):
            logger.warning("Registro fallido - Campos obligatorios incompletos")
            flash('Por favor completa todos los campos obligatorios', 'danger')
            return render_template('register.html')
        
        # Validar términos y condiciones
        if not terminos:
            logger.warning("Registro fallido - Términos y condiciones no aceptados")
            flash('Debes aceptar los términos y condiciones', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            logger.warning("Registro fallido - Contraseña muy corta")
            flash('La contraseña debe tener al menos 6 caracteres', 'danger')
            return render_template('register.html')
        
        if password != confirmar_password:
            logger.warning("Registro fallido - Contraseñas no coinciden")
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')
        
        # Validar email
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            logger.warning("Registro fallido - Email inválido")
            flash('Por favor ingresa un email válido', 'danger')
            return render_template('register.html')
        
        # Validar teléfono (opcional)
        if telefono and not re.match(r"^[\d\-\+\s]+$", telefono):
            logger.warning("Registro fallido - Teléfono inválido")
            flash('Por favor ingresa un teléfono válido', 'danger')
            return render_template('register.html')
        
        # Crear usuario
        if database is None:
            logger.error("Registro fallido - Database es None")
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template('register.html')
        
        logger.info("Intentando crear usuario en la base de datos...")
        resultado = database.crear_usuario(nombre, apellido, email, password, telefono, direccion)
        logger.info(f"Resultado de crear_usuario: {resultado}")
        
        if resultado['exito']:
            logger.info(f"Usuario creado exitosamente - ID: {resultado.get('usuario_id')}")
            flash('¡Registro exitoso! Ya puedes iniciar sesión', 'success')
            return redirect(url_for('index'))
        else:
            logger.error(f"Error al crear usuario: {resultado.get('mensaje')}")
            flash(f'Error al crear usuario: {resultado["mensaje"]}', 'danger')
    
    return render_template('register.html')

@app.route("/logout")
def logout():
    """
    RUTA DE LOGOUT - Cerrar sesión
    """
    session.clear()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('index'))

@app.route("/perfil")
def perfil():
    """
    RUTA DE PERFIL - Página del perfil del usuario
    
    MANTENIMIENTO:
    - Para agregar campos al perfil: modificar obtener_usuario_por_id en db.py
    - Para cambiar información mostrada: modificar template perfil.html
    - Para agregar validaciones: agregar verificaciones aquí
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver tu perfil', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Asegurar que el usuario tenga todos los campos necesarios
    usuario = {
        'id': usuario.get('id'),
        'nombre': usuario.get('nombre', 'Usuario'),
        'email': usuario.get('email', ''),
        'telefono': usuario.get('telefono', ''),
        'direccion': usuario.get('direccion', ''),
        'rol': usuario.get('rol', 'cliente'),
        'fecha_registro': usuario.get('fecha_registro')
    }
    
    # Obtener pedidos del usuario
    if database is None:
        pedidos = []
        total_gastado = 0
    else:
        usuario_id = usuario.get('id')
        if usuario_id:
            pedidos = database.obtener_pedidos_usuario(usuario_id)
            total_gastado = sum(pedido.get('total', 0) for pedido in pedidos)
        else:
            pedidos = []
            total_gastado = 0
    
    return render_template('perfil.html', 
                         usuario=usuario, 
                         pedidos=pedidos,
                         total_gastado=total_gastado,
                         sesiones=[])

@app.route("/editar-perfil", methods=['POST'])
def editar_perfil():
    """
    RUTA PARA EDITAR PERFIL - Procesar cambios del perfil
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para editar tu perfil', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono', '')
    direccion = request.form.get('direccion', '')
    
    if not nombre:
        flash('El nombre es obligatorio', 'danger')
        return redirect(url_for('perfil'))
    
    if database is None:
        flash('Error del sistema. Intenta más tarde.', 'danger')
        return redirect(url_for('perfil'))
    
    resultado = database.actualizar_usuario(usuario.get('id', 0), nombre, telefono, direccion)
    
    if resultado:
        session['usuario_nombre'] = nombre
        flash('Perfil actualizado exitosamente', 'success')
    else:
        flash('Error al actualizar el perfil', 'danger')
    
    return redirect(url_for('perfil'))

@app.route("/cambiar-password", methods=['POST'])
def cambiar_password():
    """
    RUTA PARA CAMBIAR CONTRASEÑA - Procesar cambio de contraseña
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para cambiar tu contraseña', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    password_actual = request.form.get('password_actual')
    password_nuevo = request.form.get('password_nuevo')
    confirmar_password = request.form.get('confirmar_password')
    
    if not all([password_actual, password_nuevo, confirmar_password]):
        flash('Por favor completa todos los campos', 'danger')
        return redirect(url_for('perfil'))
    
    if len(password_nuevo) < 6:
        flash('La nueva contraseña debe tener al menos 6 caracteres', 'danger')
        return redirect(url_for('perfil'))
    
    if password_nuevo != confirmar_password:
        flash('Las contraseñas no coinciden', 'danger')
        return redirect(url_for('perfil'))
    
    if database is None:
        flash('Error del sistema. Intenta más tarde.', 'danger')
        return redirect(url_for('perfil'))
    
    resultado = database.cambiar_password(usuario.get('id', 0), password_actual, password_nuevo)
    
    if resultado:
        flash('Contraseña cambiada exitosamente', 'success')
    else:
        flash('Contraseña actual incorrecta', 'danger')
    
    return redirect(url_for('perfil'))

# ==========================================
# RUTAS DE RECUPERACIÓN DE CONTRASEÑA
# ==========================================

@app.route("/recuperar-password", methods=['GET', 'POST'])
def recuperar_password():
    """
    RUTA PARA RECUPERAR CONTRASEÑA - Paso 1: Solicitar email
    """
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Sanitizar y validar email
        email_limpio, error = sanitizar_email(email)
        if error:
            flash(error, 'danger')
            return render_template("recuperar_password.html")
        
        # Verificar si el usuario existe
        if database is None:
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template("recuperar_password.html")
        
        usuario = database.buscar_usuario_por_email(email_limpio)
        if not usuario:
            # Por seguridad, no revelar si el email existe o no
            flash('Si el email está registrado, recibirás instrucciones de recuperación', 'info')
            return render_template("recuperar_password.html")
        
        # Generar token de recuperación
        token = generar_token_recuperacion()
        expiracion = datetime.now() + timedelta(hours=24)
        
        # Guardar token en la base de datos
        exito = database.guardar_token_recuperacion(usuario['id'], token, expiracion)
        
        if exito:
            # En una aplicación real, aquí enviarías un email
            # Por ahora, simulamos el envío
            flash(f'Se han enviado instrucciones de recuperación a {email_limpio}', 'success')
            logger.info(f"Token de recuperación generado para {email_limpio}: {token}")
        else:
            flash('Error al procesar la solicitud. Contacta soporte.', 'danger')
        
        return render_template("recuperar_password.html")
    
    return render_template("recuperar_password.html")

@app.route("/verificar-codigo", methods=['GET', 'POST'])
def verificar_codigo():
    """
    RUTA PARA VERIFICAR CÓDIGO - Paso 2: Verificar código enviado
    """
    if request.method == 'POST':
        email = request.form.get('email')
        codigo = request.form.get('codigo')
        
        # Sanitizar campos
        email_limpio, error_email = sanitizar_email(email)
        codigo_limpio, error_codigo = sanitizar_codigo(codigo)
        
        if error_email:
            flash(error_email, 'danger')
            return render_template("verificar_codigo.html")
        
        if error_codigo:
            flash(error_codigo, 'danger')
            return render_template("verificar_codigo.html")
        
        # Verificar token en la base de datos
        if database is None:
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template("verificar_codigo.html")
        
        token_valido = database.verificar_token_recuperacion(email_limpio, codigo_limpio)
        
        if token_valido and token_valido.get('exito'):
            # Generar token de sesión temporal para cambio de contraseña
            session['recuperacion_token'] = token_valido
            session['recuperacion_email'] = email_limpio
            return redirect(url_for('cambiar_password_recuperacion'))
        else:
            flash('Código inválido o expirado', 'danger')
            return render_template("verificar_codigo.html")
    
    return render_template("verificar_codigo.html")

@app.route("/cambiar-password-recuperacion", methods=['GET', 'POST'])
def cambiar_password_recuperacion():
    """
    RUTA PARA CAMBIAR CONTRASEÑA - Paso 3: Nueva contraseña
    """
    # Verificar que el usuario viene del proceso de recuperación
    if not session.get('recuperacion_token') or not session.get('recuperacion_email'):
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password_nuevo = request.form.get('password_nuevo')
        confirmar_password = request.form.get('confirmar_password')
        
        # Validaciones de contraseña
        if not password_nuevo or not confirmar_password:
            flash('Todos los campos son obligatorios', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        if password_nuevo != confirmar_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        if len(password_nuevo) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        # Validar fortaleza de contraseña
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password_nuevo):
            flash('La contraseña debe contener mayúsculas, minúsculas, números y caracteres especiales', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        # Cambiar contraseña
        if database is None:
            flash('Error del sistema. Intenta más tarde.', 'danger')
            return render_template("cambiar_password_recuperacion.html")
        
        exito = database.cambiar_password_por_token(
            session['recuperacion_email'],
            session['recuperacion_token']['token_id'],
        password_nuevo
    )
    
    if exito:
            # Limpiar sesión de recuperación
            session.pop('recuperacion_token', None)
            session.pop('recuperacion_email', None)
            
            flash('Contraseña cambiada exitosamente. Ya puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
    else:
            flash('Error al cambiar la contraseña. Contacta soporte', 'danger')
            return render_template("cambiar_password_recuperacion.html")
    
    return render_template("cambiar_password_recuperacion.html")

@app.route("/contacto-soporte")
def contacto_soporte():
    """
    RUTA PARA CONTACTO CON SOPORTE - Cuando falla la recuperación automática
    """
    return render_template("contacto_soporte.html")

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.route("/")
def index():
    """
    RUTA PRINCIPAL - Página de inicio con productos organizados por negocios
    """
    # Obtener parámetro de búsqueda
    busqueda = request.args.get('busqueda', '').strip()
    
    # Cargar datos completos
    datos = cargar_datos_completos()
    negocios = datos.get('negocios', {})
    categorias = datos.get('categorias', {})
    sucursales = datos.get('sucursales', {})
    ofertas_activas = obtener_ofertas_activas()
    productos_destacados = obtener_productos_destacados()
    
    # Obtener productos por negocio
    productos_por_negocio = {}
    for negocio_id in negocios.keys():
        productos_por_negocio[negocio_id] = obtener_productos_por_negocio(negocio_id)
    
    # Filtrar productos si hay búsqueda
    productos_filtrados = []
    if busqueda:
        todos_productos = datos.get('productos', [])
        productos_filtrados = [
            p for p in todos_productos 
            if busqueda.lower() in p['nombre'].lower() and p.get('activo', True)
        ]
    
    return render_template("index.html", 
                         negocios=negocios,
                         categorias=categorias,
                         sucursales=sucursales,
                         ofertas=ofertas_activas,
                         productos_destacados=productos_destacados,
                         productos_por_negocio=productos_por_negocio,
                         busqueda=busqueda,
                         productos_filtrados=productos_filtrados)

@app.route("/negocio/<negocio_id>")
def ver_negocio(negocio_id):
    """
    RUTA PARA VER PRODUCTOS DE UN NEGOCIO ESPECÍFICO
    
    PARÁMETROS:
    - negocio_id: ID del negocio a mostrar
    
    MANTENIMIENTO:
    - Para agregar nuevos negocios: editar productos.json sección "negocios"
    - Para cambiar información del negocio: modificar datos en productos.json
    - Para agregar productos al negocio: agregar en productos.json con negocio correcto
    """
    datos = cargar_datos_completos()
    negocios = datos.get('negocios', {})
    categorias = datos.get('categorias', {})
    sucursales = datos.get('sucursales', {})
    
    if negocio_id not in negocios:
        flash('Negocio no encontrado', 'danger')
        return redirect(url_for('index'))
    
    negocio = negocios[negocio_id]
    productos = obtener_productos_por_negocio(negocio_id)
    sucursales_negocio = sucursales.get(negocio_id, {})
    
    return render_template("negocio.html", 
                         negocio=negocio,
                         productos=productos,
                         categorias=categorias,
                         sucursales=sucursales_negocio)

@app.route("/categoria/<categoria_id>")
def ver_categoria(categoria_id):
    """
    RUTA PARA VER PRODUCTOS DE UNA CATEGORÍA ESPECÍFICA
    
    PARÁMETROS:
    - categoria_id: ID de la categoría a mostrar
    
    MANTENIMIENTO:
    - Para agregar categorías: editar productos.json sección "categorias"
    - Para cambiar iconos: modificar campo "icono" en la categoría
    - Para agregar productos a categoría: asignar categoria_id correcto en productos.json
    """
    datos = cargar_datos_completos()
    categorias = datos.get('categorias', {})
    negocios = datos.get('negocios', {})
    
    if categoria_id not in categorias:
        flash('Categoría no encontrada', 'danger')
        return redirect(url_for('index'))
    
    categoria = categorias[categoria_id]
    productos = datos.get('productos', [])
    productos_categoria = [p for p in productos if p.get('categoria') == categoria_id and p.get('activo', True)]
    
    return render_template("categoria.html", 
                         categoria=categoria,
                         productos=productos_categoria,
                         negocios=negocios)

@app.route("/agregar_al_carrito", methods=['POST'])
def agregar_al_carrito():
    """
    RUTA PARA AGREGAR PRODUCTOS AL CARRITO
    """
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    if not producto_id:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': 'Producto no especificado'}), 400
        flash('Producto no especificado', 'danger')
        return redirect(url_for('index'))
    
    # Inicializar carrito si no existe
    if 'carrito' not in session:
        session['carrito'] = {}
    
    # Agregar o actualizar cantidad
    if producto_id in session['carrito']:
        session['carrito'][producto_id] += cantidad
    else:
        session['carrito'][producto_id] = cantidad
    
    # Guardar cambios en la sesión
    session.modified = True
    
    logger.info(f"Producto agregado al carrito: {producto_id} x{cantidad}")
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        return jsonify({
            'success': True,
            'mensaje': f'¡Producto agregado al carrito!',
            'carrito_count': len(session['carrito']),
            'producto_id': producto_id,
            'cantidad': cantidad
        })
    
    # Si es una petición normal, redirigir
    flash(f'¡Producto agregado al carrito!', 'success')
    return redirect(url_for('index'))

@app.route("/carrito")
def carrito():
    """
    RUTA PARA VER EL CARRITO DE COMPRAS
    Muestra todos los productos en el carrito con sus cantidades
    """
    carrito_items = []
    total = 0
    
    if 'carrito' in session:
        for producto_id, cantidad in session['carrito'].items():
            producto = obtener_producto_por_id(producto_id)
            if producto:
                subtotal = producto['precio'] * cantidad
                carrito_items.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal
                })
                total += subtotal
    
    return render_template("carrito.html", carrito_items=carrito_items, total=total)

@app.route("/actualizar_cantidad", methods=['POST'])
def actualizar_cantidad():
    """
    RUTA PARA ACTUALIZAR CANTIDADES EN EL CARRITO
    """
    producto_id = request.form.get('producto_id')
    nueva_cantidad = int(request.form.get('cantidad', 0))
    
    if nueva_cantidad <= 0:
        # Eliminar producto del carrito
        if 'carrito' in session and producto_id in session['carrito']:
            del session['carrito'][producto_id]
            session.modified = True
            flash(f'{producto_id} eliminado del carrito', 'info')
    else:
        # Actualizar cantidad
        if 'carrito' in session:
            session['carrito'][producto_id] = nueva_cantidad
            session.modified = True
            flash(f'Cantidad de {producto_id} actualizada', 'success')
    
    return redirect(url_for('carrito'))

@app.route("/vaciar_carrito")
def vaciar_carrito():
    """
    RUTA PARA VACIAR EL CARRITO DE COMPRAS
    """
    session.pop('carrito', None)
    flash('Carrito vaciado', 'info')
    return redirect(url_for('carrito'))

# ==========================================
# RUTAS DEL SISTEMA DE PAGO
# ==========================================

@app.route("/checkout")
def checkout():
    """
    RUTA PARA EL PROCESO DE PAGO
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para realizar una compra', 'warning')
        return redirect(url_for('login'))
    
    if not session.get('carrito'):
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito'))
    
    carrito_items = []
    total = 0
    
    for producto_id, cantidad in session['carrito'].items():
        producto = obtener_producto_por_id(producto_id)
        if producto:
            subtotal = producto['precio'] * cantidad
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template("checkout.html", carrito_items=carrito_items, total=total)

@app.route("/procesar_pago", methods=['POST'])
def procesar_pago():
    """
    RUTA PARA PROCESAR EL PAGO
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para realizar una compra', 'warning')
        return redirect(url_for('login'))
    
    if not session.get('carrito'):
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('carrito'))
    
    # Obtener datos del formulario
    metodo_pago = request.form.get('metodo_pago')
    direccion = request.form.get('direccion')
    notas = request.form.get('notas')
    
    # Validaciones básicas
    if not direccion:
        flash('Por favor ingresa una dirección de entrega', 'danger')
        return redirect(url_for('checkout'))
    
    # Crear el pedido
    numero_pedido = generar_numero_pedido()
    usuario = obtener_usuario_actual()
    
    carrito_items = []
    total = 0
    
    for producto_id, cantidad in session['carrito'].items():
        producto = obtener_producto_por_id(producto_id)
        if producto:
            subtotal = producto['precio'] * cantidad
            carrito_items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
    
    # Guardar pedido en la base de datos
    pedido_id = database.guardar_pedido(
        usuario_id=usuario['id'],
        numero_pedido=numero_pedido,
        total=total,
        metodo_pago=metodo_pago,
        direccion_entrega=direccion,
        notas=notas
    )
    
    if pedido_id:
        # Guardar items del pedido
        items_db = []
        for item in carrito_items:
            items_db.append({
                'producto_id': item['producto']['id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['producto']['precio'],
                'subtotal': item['subtotal']
            })
        
        database.guardar_items_pedido(pedido_id, items_db)
    
    # Limpiar carrito
    session.pop('carrito', None)
    
    if pedido_id:
        # INTEGRACIÓN CON BELGRANO TICKETS
        try:
            from integracion_belgrano_tickets import BelgranoTicketsAPI
            
            # Preparar datos para enviar a Belgrano Tickets
            # Obtener nombre completo del usuario (manejar caso sin apellido)
            nombre_completo = usuario.get('nombre', 'Cliente')
            if usuario.get('apellido'):
                nombre_completo = f"{usuario['nombre']} {usuario['apellido']}"
            
            # Verificar si es un comerciante
            es_comerciante = usuario.get('rol') == 'comerciante'
            nombre_cliente = nombre_completo
            
            if es_comerciante:
                # Obtener información del comerciante
                comerciante = database.obtener_comerciante_por_usuario(usuario['id'])
                if comerciante:
                    nombre_cliente = f"{comerciante['nombre_negocio']} - {nombre_completo}"
                    # Agregar información comercial a las indicaciones
                    indicaciones_comerciales = f"COMERCIANTE - Negocio: {comerciante['nombre_negocio']}"
                    if comerciante.get('tipo_negocio'):
                        indicaciones_comerciales += f", Tipo: {comerciante['tipo_negocio']}"
                    if comerciante.get('cuit'):
                        indicaciones_comerciales += f", CUIT: {comerciante['cuit']}"
                    
                    notas_completas = f"{indicaciones_comerciales}. {notas or 'Sin indicaciones especiales'}"
                else:
                    notas_completas = f"COMERCIANTE - {notas or 'Sin indicaciones especiales'}"
            else:
                notas_completas = notas or 'Sin indicaciones especiales'
            
            # Preparar productos para el ticket
            productos_ticket = []
            for item in carrito_items:
                productos_ticket.append({
                    'nombre': item['producto']['nombre'],
                    'cantidad': item['cantidad'],
                    'precio': item['producto']['precio'],
                    'subtotal': item['subtotal']
                })
            
            ticket_data = {
                'numero': numero_pedido,
                'cliente_nombre': nombre_cliente,
                'direccion': direccion,
                'telefono': usuario.get('telefono', ''),
                'email': usuario['email'],
                'productos': productos_ticket,
                'total': total,
                'metodo_pago': metodo_pago,
                'fecha': datetime.now().isoformat(),
                'indicaciones': notas_completas,
                'tipo_cliente': 'comerciante' if es_comerciante else 'cliente'
            }
            
            # Enviar ticket a Belgrano Tickets
            api = BelgranoTicketsAPI()
            if api.verificar_conexion():
                resultado = api.enviar_ticket(ticket_data)
                if resultado:
                    tipo_cliente = "Comerciante" if es_comerciante else "Cliente"
                    print(f"✅ Ticket enviado a Belgrano Tickets: {numero_pedido} ({tipo_cliente})")
                    print(f"   Cliente: {nombre_cliente}")
                    print(f"   Total: ${total}")
                    print(f"   Productos: {len(productos_ticket)} items")
                else:
                    print(f"⚠️ No se pudo enviar ticket a Belgrano Tickets: {numero_pedido}")
            else:
                print(f"⚠️ Belgrano Tickets no está disponible")
                
        except ImportError:
            print("⚠️ Módulo de integración no disponible")
        except Exception as e:
            print(f"⚠️ Error en integración con Belgrano Tickets: {e}")
            import traceback
            traceback.print_exc()
        
        flash(f'¡Pedido confirmado! Número: {numero_pedido}', 'success')
        return redirect(url_for('confirmacion_pedido', numero_pedido=numero_pedido))
    else:
        flash('Error al procesar el pedido. Intenta nuevamente.', 'danger')
        return redirect(url_for('checkout'))

@app.route("/confirmacion/<numero_pedido>")
def confirmacion_pedido(numero_pedido):
    """
    RUTA PARA MOSTRAR LA CONFIRMACIÓN DEL PEDIDO
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver esta página', 'warning')
        return redirect(url_for('login'))
    
    # pedido = pedidos.get(numero_pedido)
    # if not pedido:
    #     flash('Pedido no encontrado', 'danger')
    #     return redirect(url_for('index'))
    
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    hora_actual = datetime.now().strftime("%H:%M")
    
    return render_template("confirmacion.html", 
                         numero_pedido=numero_pedido,
                         fecha_actual=fecha_actual,
                         hora_actual=hora_actual)

@app.route("/mis_pedidos")
def mis_pedidos():
    """
    RUTA PARA VER HISTORIAL DE PEDIDOS
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver tus pedidos', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Obtener pedidos del usuario desde la base de datos
    pedidos = database.obtener_pedidos_usuario(usuario['id'])
    
    return render_template("mis_pedidos.html", pedidos=pedidos, usuario=usuario)

@app.route("/repetir_pedido/<int:pedido_id>")
def repetir_pedido(pedido_id):
    """
    RUTA PARA REPETIR UN PEDIDO ANTERIOR
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para repetir pedidos', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Repetir pedido
    exito, resultado = database.repetir_pedido(pedido_id, usuario['id'])
    
    if exito:
        flash(f'Pedido repetido exitosamente. Nuevo número: {resultado}', 'success')
        return redirect(url_for('confirmacion_pedido', numero_pedido=resultado))
    else:
        flash(f'Error al repetir pedido: {resultado}', 'danger')
        return redirect(url_for('mis_pedidos'))

@app.route("/ver_pedido/<int:pedido_id>")
def ver_pedido(pedido_id):
    """
    RUTA PARA VER DETALLES DE UN PEDIDO ESPECÍFICO
    """
    if not usuario_logueado():
        flash('Debes iniciar sesión para ver pedidos', 'warning')
        return redirect(url_for('login'))
    
    usuario = obtener_usuario_actual()
    if not usuario:
        flash('Error al cargar información del usuario', 'danger')
        return redirect(url_for('login'))
    
    # Obtener pedido completo
    pedido = database.obtener_pedido_completo(pedido_id)
    
    if not pedido:
        flash('Pedido no encontrado', 'danger')
        return redirect(url_for('mis_pedidos'))
    
    # Asegurar que items sea una lista
    if 'items' not in pedido or not isinstance(pedido['items'], list):
        pedido['items'] = []
    
    return render_template("ver_pedido.html", pedido=pedido, usuario=usuario, pedido_id=pedido_id)

@app.route("/test")
def test():
    """
    RUTA DE PRUEBA - Para verificar que la app funciona
    Esta función se ejecuta cuando alguien visita http://localhost:5000/test
    """
    return "¡La aplicación funciona correctamente!"

@app.route("/contacto", methods=['GET', 'POST'])
def contacto():
    """
    RUTA DE CONTACTO - Página de contacto y formulario
    """
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        asunto = request.form.get('asunto')
        mensaje = request.form.get('mensaje')
        
        # Aquí podrías enviar el email o guardar en base de datos
        logger.info(f"Mensaje de contacto recibido de {nombre} ({email}): {asunto}")
        
        flash('¡Gracias por tu mensaje! Te responderemos pronto.', 'success')
        return redirect(url_for('contacto'))
    
    return render_template("contacto.html")

@app.route("/sobre-nosotros")
def sobre_nosotros():
    """
    RUTA SOBRE NOSOTROS - Página con información de la empresa
    """
    return render_template("sobre_nosotros.html")

# ==========================================
# SECCIÓN COMERCIANTES (RUTAS BÁSICAS)
# ==========================================

@app.route("/comerciantes")
def comerciantes_home():
    """
    Panel principal de Comerciantes con accesos rápidos.
    Usa los flujos existentes (carrito, checkout, pedidos) para asegurar funcionalidad.
    """
    datos = cargar_datos_completos()
    negocios = datos.get('negocios', {})
    categorias = datos.get('categorias', {})
    return render_template("comerciantes/dashboard.html", negocios=negocios, categorias=categorias)

@app.route("/comerciantes/pedidos")
def comerciantes_pedidos():
    """Atajo a los pedidos del usuario desde el panel de comerciantes."""
    return redirect(url_for('mis_pedidos'))

@app.route("/comerciantes/carrito")
def comerciantes_carrito():
    """Atajo al carrito normal desde el panel de comerciantes."""
    return redirect(url_for('carrito'))

@app.route("/comerciantes/checkout")
def comerciantes_checkout():
    """Atajo al checkout normal desde el panel de comerciantes."""
    return redirect(url_for('checkout'))

@app.route("/comerciantes/confirmacion/<numero_pedido>")
def comerciantes_confirmacion(numero_pedido):
    """Atajo a la confirmación de pedido normal desde el panel de comerciantes."""
    return redirect(url_for('confirmacion_pedido', numero_pedido=numero_pedido))

# ==========================================
# REGISTRO Y LOGIN DE COMERCIANTES
# ==========================================

@app.route("/comerciantes/registro", methods=['GET', 'POST'])
def registro_comerciante():
    """Registro específico para comerciantes"""
    if request.method == 'POST':
        # Datos personales
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        
        # Datos comerciales
        nombre_negocio = request.form.get('nombre_negocio')
        cuit = request.form.get('cuit')
        direccion_comercial = request.form.get('direccion_comercial')
        telefono_comercial = request.form.get('telefono_comercial')
        tipo_negocio = request.form.get('tipo_negocio')
        
        # Validaciones
        if not all([nombre, apellido, email, password, nombre_negocio]):
            flash('Por favor completa todos los campos obligatorios', 'danger')
            return render_template("comerciantes/registro.html")
        
        # Crear usuario con rol comerciante
        resultado = database.crear_usuario(nombre, apellido, email, password, telefono, direccion, 'comerciante')
        
        if resultado['exito']:
            # Crear perfil de comerciante
            comerciante_resultado = database.crear_comerciante(
                resultado['usuario_id'], 
                nombre_negocio, 
                cuit, 
                direccion_comercial, 
                telefono_comercial, 
                tipo_negocio
            )
            
            if comerciante_resultado['exito']:
                flash('¡Comerciante registrado exitosamente! Ya puedes iniciar sesión.', 'success')
                return redirect(url_for('login_comerciante'))
            else:
                flash(f'Error al crear perfil comercial: {comerciante_resultado["mensaje"]}', 'danger')
        else:
            flash(f'Error al crear usuario: {resultado["mensaje"]}', 'danger')
    
    return render_template("comerciantes/registro.html")

@app.route("/comerciantes/login", methods=['GET', 'POST'])
def login_comerciante():
    """Login específico para comerciantes"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Por favor ingresa email y contraseña', 'danger')
            return render_template("comerciantes/login.html")
        
        resultado = database.verificar_usuario(email, password)
        
        if resultado['exito']:
            usuario = resultado['usuario']
            
            # Verificar que sea comerciante
            if usuario.get('rol') != 'comerciante':
                flash('Esta cuenta no está registrada como comerciante', 'danger')
                return render_template("comerciantes/login.html")
            
            # Obtener información del comerciante
            comerciante = database.obtener_comerciante_por_usuario(usuario['id'])
            
            if comerciante:
                session['usuario_id'] = usuario['id']
                session['usuario_nombre'] = usuario['nombre']
                session['usuario_email'] = usuario['email']
                session['usuario_rol'] = 'comerciante'
                session['comerciante_id'] = comerciante['id']
                session['nombre_negocio'] = comerciante['nombre_negocio']
                
                flash(f'¡Bienvenido, {comerciante["nombre_negocio"]}!', 'success')
                return redirect(url_for('comerciantes_home'))
            else:
                flash('Error al cargar información del comerciante', 'danger')
        else:
            flash(resultado['mensaje'], 'danger')
    
    return render_template("comerciantes/login.html")

# ==========================================
# GESTIÓN DE PAQUETES DE COMERCIANTES
# ==========================================

@app.route("/comerciantes/paquetes")
def comerciantes_paquetes():
    """Gestión de paquetes de comerciantes"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    comerciante_id = session.get('comerciante_id')
    paquetes = database.obtener_paquetes_comerciante(comerciante_id)
    
    return render_template("comerciantes/paquetes.html", paquetes=paquetes)

@app.route("/comerciantes/paquetes/crear", methods=['GET', 'POST'])
def crear_paquete():
    """Crear nuevo paquete"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    if request.method == 'POST':
        nombre_paquete = request.form.get('nombre_paquete')
        descripcion = request.form.get('descripcion')
        frecuencia = request.form.get('frecuencia', 'mensual')
        
        if not nombre_paquete:
            flash('El nombre del paquete es obligatorio', 'danger')
            return render_template("comerciantes/crear_paquete.html")
        
        comerciante_id = session.get('comerciante_id')
        resultado = database.crear_paquete_comerciante(comerciante_id, nombre_paquete, descripcion, frecuencia)
        
        if resultado['exito']:
            flash(f'Paquete "{nombre_paquete}" creado exitosamente', 'success')
            return redirect(url_for('editar_paquete', paquete_id=resultado['paquete_id']))
        else:
            flash(f'Error al crear paquete: {resultado["mensaje"]}', 'danger')
    
    return render_template("comerciantes/crear_paquete.html")

@app.route("/comerciantes/paquetes/<int:paquete_id>/editar")
def editar_paquete(paquete_id):
    """Editar paquete existente"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    # Obtener datos completos
    datos = cargar_datos_completos()
    negocios = datos.get('negocios', {})
    sucursales = datos.get('sucursales', {})
    
    # Obtener paquete
    comerciante_id = session.get('comerciante_id')
    paquetes = database.obtener_paquetes_comerciante(comerciante_id)
    paquete = next((p for p in paquetes if p['id'] == paquete_id), None)
    
    if not paquete:
        flash('Paquete no encontrado', 'danger')
        return redirect(url_for('comerciantes_paquetes'))
    
    return render_template("comerciantes/editar_paquete.html", 
                         paquete=paquete, 
                         negocios=negocios,
                         sucursales=sucursales)

@app.route("/comerciantes/paquetes/<int:paquete_id>/agregar_producto", methods=['POST'])
def agregar_producto_paquete(paquete_id):
    """Agregar producto a un paquete"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        return jsonify({'exito': False, 'mensaje': 'No autorizado'})
    
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad', 1))
    
    if not producto_id or cantidad <= 0:
        return jsonify({'exito': False, 'mensaje': 'Datos inválidos'})
    
    resultado = database.agregar_producto_a_paquete(paquete_id, producto_id, cantidad)
    return jsonify(resultado)

@app.route("/api/productos_por_sucursal", methods=['POST'])
def api_productos_por_sucursal():
    """API para obtener productos de una sucursal específica"""
    if not usuario_logueado():
        return jsonify({'exito': False, 'mensaje': 'No autorizado'})
    
    data = request.get_json()
    negocio_id = data.get('negocio_id')
    sucursal_id = data.get('sucursal_id')
    
    if not negocio_id or not sucursal_id:
        return jsonify({'exito': False, 'mensaje': 'Datos incompletos'})
    
    productos = obtener_productos_por_sucursal(negocio_id, sucursal_id)
    
    return jsonify({
        'exito': True,
        'productos': productos
    })

@app.route("/comerciantes/paquetes/<int:paquete_id>/procesar", methods=['POST'])
def procesar_paquete(paquete_id):
    """Procesar pedido automático de un paquete"""
    if not usuario_logueado() or session.get('usuario_rol') != 'comerciante':
        flash('Debes iniciar sesión como comerciante', 'warning')
        return redirect(url_for('login_comerciante'))
    
    resultado = database.procesar_pedido_automatico_paquete(paquete_id)
    
    if resultado['exito']:
        flash(f'Pedido automático procesado: {resultado["numero_pedido"]}', 'success')
        return redirect(url_for('comerciantes_confirmacion', numero_pedido=resultado['numero_pedido']))
    else:
        flash(f'Error al procesar pedido: {resultado["mensaje"]}', 'danger')
        return redirect(url_for('comerciantes_paquetes'))

@app.route("/ticketera")
def ticketera():
    """
    RUTA PARA ACCEDER A LA TICKETERA
    Redirige a la aplicación de tickets
    """
    # En desarrollo usa localhost, en producción usa la URL de Render
    ticketera_url = os.environ.get('TICKETERA_URL', 'http://localhost:5001')
    return redirect(ticketera_url)

@app.route("/admin")
def admin():
    """
    RUTA PARA ACCEDER AL PANEL DE ADMINISTRACIÓN
    Redirige a la ticketera con credenciales de admin
    """
    # En desarrollo usa localhost, en producción usa la URL de Render
    ticketera_url = os.environ.get('TICKETERA_URL', 'http://localhost:5001')
    return redirect(ticketera_url)

# ==========================================
# MANEJADORES DE ERRORES
# ==========================================

@app.errorhandler(404)
def not_found(error):
    """
    MANEJADOR DE ERROR 404 - Página no encontrada
    Se ejecuta cuando alguien visita una URL que no existe
    """
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """
    MANEJADOR DE ERROR 500 - Error interno del servidor
    Se ejecuta cuando hay un error en el servidor
    """
    return render_template('500.html'), 500

# ==========================================
# INICIO DE LA APLICACIÓN
# ==========================================
if __name__ == "__main__":
    """
    PUNTO DE ENTRADA - Solo se ejecuta si corremos este archivo directamente
    Inicia el servidor Flask en modo debug
    """
    logger.info("Iniciando aplicación Flask...")
    print("🚀 Iniciando Belgrano Ahorro...")
    print("📱 Abre tu navegador en: http://localhost:5000")
    print("⏹️  Presiona Ctrl+C para detener")
    app.run(debug=True, host="0.0.0.0", port=5000)