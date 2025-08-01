#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo del sistema Belgrano Ahorro
Verifica todos los componentes y reporta problemas
"""

import sys
import os
import json
import sqlite3
import traceback
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warning(msg):
    print(f"⚠️ {msg}")

def print_info(msg):
    print(f"ℹ️ {msg}")

def test_imports():
    """Verificar que todos los módulos necesarios estén disponibles"""
    print_header("VERIFICACIÓN DE IMPORTS")
    
    required_modules = [
        'flask',
        'sqlite3',
        'json',
        'logging',
        'datetime',
        'uuid',
        're',
        'secrets',
        'hashlib'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print_success(f"Módulo {module} disponible")
        except ImportError as e:
            print_error(f"Módulo {module} no disponible: {e}")

def test_database():
    """Verificar la base de datos"""
    print_header("VERIFICACIÓN DE BASE DE DATOS")
    
    try:
        # Verificar que el archivo existe
        if os.path.exists('belgrano_ahorro.db'):
            print_success("Archivo de base de datos existe")
        else:
            print_warning("Archivo de base de datos no existe")
        
        # Importar y probar db.py
        import db
        print_success("Módulo db.py importado correctamente")
        
        # Crear/verificar base de datos
        db.crear_base_datos()
        print_success("Base de datos inicializada correctamente")
        
        # Verificar tablas
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        
        required_tables = ['usuarios', 'productos', 'carrito', 'pedidos', 'pedido_items', 'tokens_recuperacion']
        
        for table in required_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print_success(f"Tabla {table} existe")
            else:
                print_error(f"Tabla {table} no existe")
        
        conn.close()
        
    except Exception as e:
        print_error(f"Error en base de datos: {e}")
        traceback.print_exc()

def test_productos_json():
    """Verificar el archivo productos.json"""
    print_header("VERIFICACIÓN DE PRODUCTOS.JSON")
    
    try:
        if not os.path.exists('productos.json'):
            print_error("Archivo productos.json no existe")
            return
        
        with open('productos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print_success("Archivo productos.json cargado correctamente")
        
        # Verificar estructura
        required_keys = ['productos', 'negocios', 'categorias', 'ofertas']
        for key in required_keys:
            if key in data:
                print_success(f"Clave '{key}' presente en productos.json")
            else:
                print_warning(f"Clave '{key}' ausente en productos.json")
        
        # Verificar productos
        productos = data.get('productos', [])
        print_info(f"Total de productos: {len(productos)}")
        
        if productos:
            # Verificar estructura del primer producto
            primer_producto = productos[0]
            required_product_fields = ['id', 'nombre', 'precio', 'negocio']
            for field in required_product_fields:
                if field in primer_producto:
                    print_success(f"Campo '{field}' presente en productos")
                else:
                    print_warning(f"Campo '{field}' ausente en productos")
        
    except Exception as e:
        print_error(f"Error en productos.json: {e}")
        traceback.print_exc()

def test_templates():
    """Verificar templates HTML"""
    print_header("VERIFICACIÓN DE TEMPLATES")
    
    required_templates = [
        'base.html',
        'index.html',
        'login.html',
        'register.html',
        'perfil.html',
        'carrito.html',
        'checkout.html',
        'mis_pedidos.html',
        'error_sistema.html'
    ]
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        print_error(f"Directorio {templates_dir} no existe")
        return
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            print_success(f"Template {template} existe")
        else:
            print_error(f"Template {template} no existe")

def test_static_files():
    """Verificar archivos estáticos"""
    print_header("VERIFICACIÓN DE ARCHIVOS ESTÁTICOS")
    
    static_dir = 'static'
    if not os.path.exists(static_dir):
        print_warning(f"Directorio {static_dir} no existe")
        return
    
    # Verificar subdirectorios comunes
    subdirs = ['css', 'js', 'images', 'img']
    for subdir in subdirs:
        subdir_path = os.path.join(static_dir, subdir)
        if os.path.exists(subdir_path):
            print_success(f"Directorio {subdir} existe")
        else:
            print_warning(f"Directorio {subdir} no existe")

def test_app_import():
    """Verificar que app.py se puede importar"""
    print_header("VERIFICACIÓN DE APP.PY")
    
    try:
        # Verificar que app.py existe
        if not os.path.exists('app.py'):
            print_error("Archivo app.py no existe")
            return
        
        print_success("Archivo app.py existe")
        
        # Intentar importar (sin ejecutar)
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        
        # Solo cargar el módulo para verificar sintaxis
        spec.loader.exec_module(app_module)
        print_success("app.py se puede importar correctamente")
        
    except Exception as e:
        print_error(f"Error importando app.py: {e}")
        traceback.print_exc()

def test_database_functions():
    """Probar funciones específicas de la base de datos"""
    print_header("PRUEBA DE FUNCIONES DE BASE DE DATOS")
    
    try:
        import db
        
        # Probar crear_usuario
        resultado = db.crear_usuario(
            nombre="Test",
            apellido="Usuario",
            email="test@test.com",
            password="test123",
            telefono="123456789",
            direccion="Test Address"
        )
        
        if resultado['exito']:
            print_success("Función crear_usuario funciona correctamente")
        else:
            print_warning(f"crear_usuario falló: {resultado['mensaje']}")
        
        # Probar verificar_usuario
        resultado = db.verificar_usuario("test@test.com", "test123")
        if resultado['exito']:
            print_success("Función verificar_usuario funciona correctamente")
        else:
            print_warning(f"verificar_usuario falló: {resultado['mensaje']}")
        
        # Probar buscar_usuario_por_email
        usuario = db.buscar_usuario_por_email("test@test.com")
        if usuario:
            print_success("Función buscar_usuario_por_email funciona correctamente")
        else:
            print_warning("buscar_usuario_por_email no encontró usuario")
        
        # Limpiar usuario de prueba
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE email = ?", ("test@test.com",))
        conn.commit()
        conn.close()
        print_info("Usuario de prueba eliminado")
        
    except Exception as e:
        print_error(f"Error probando funciones de BD: {e}")
        traceback.print_exc()

def test_flask_app():
    """Probar que la aplicación Flask se puede iniciar"""
    print_header("PRUEBA DE APLICACIÓN FLASK")
    
    try:
        # Importar app
        from app import app
        
        print_success("Aplicación Flask importada correctamente")
        
        # Verificar rutas principales
        with app.test_client() as client:
            # Probar ruta principal
            response = client.get('/')
            if response.status_code == 200:
                print_success("Ruta '/' responde correctamente")
            else:
                print_warning(f"Ruta '/' responde con código {response.status_code}")
            
            # Probar ruta de login
            response = client.get('/login')
            if response.status_code == 200:
                print_success("Ruta '/login' responde correctamente")
            else:
                print_warning(f"Ruta '/login' responde con código {response.status_code}")
            
            # Probar ruta de registro
            response = client.get('/register')
            if response.status_code == 200:
                print_success("Ruta '/register' responde correctamente")
            else:
                print_warning(f"Ruta '/register' responde con código {response.status_code}")
        
    except Exception as e:
        print_error(f"Error probando Flask app: {e}")
        traceback.print_exc()

def main():
    """Ejecutar diagnóstico completo"""
    print_header("DIAGNÓSTICO COMPLETO - BELGRANO AHORRO")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Directorio: {os.getcwd()}")
    
    # Ejecutar todas las pruebas
    test_imports()
    test_database()
    test_productos_json()
    test_templates()
    test_static_files()
    test_app_import()
    test_database_functions()
    test_flask_app()
    
    print_header("DIAGNÓSTICO COMPLETADO")
    print_info("Revisa los resultados arriba para identificar problemas")
    print_info("Si hay errores, corrígelos antes de ejecutar la aplicación")

if __name__ == "__main__":
    main() 