#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Local para Testear Errores
Simula el entorno de producción antes del deploy
"""

import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime

def setup_environment():
    """Configurar variables de entorno para testing"""
    print("=== CONFIGURANDO ENTORNO ===")
    
    # Variables de entorno para testing
    os.environ['FLASK_ENV'] = 'production'
    os.environ['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'test_api_key_123'
    os.environ['BELGRANO_AHORRO_DB_PATH'] = 'test_belgrano_ahorro.db'
    os.environ['TICKETERA_URL'] = 'http://localhost:5001'
    os.environ['TICKETERA_API_KEY'] = 'test_ticketera_key_123'
    
    print("✅ Variables de entorno configuradas")
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"   BELGRANO_AHORRO_URL: {os.environ.get('BELGRANO_AHORRO_URL')}")
    print(f"   BELGRANO_AHORRO_API_KEY: {os.environ.get('BELGRANO_AHORRO_API_KEY')[:10]}...")

def test_syntax():
    """Probar sintaxis de todos los archivos Python"""
    print("\n=== PROBANDO SINTAXIS ===")
    
    archivos_python = [
        'app_unificado.py',
        'api_belgrano_ahorro.py',
        'belgrano_client.py', 
        'devops_persistence.py',
        'belgrano_tickets/app.py'
    ]
    
    errores = []
    
    for archivo in archivos_python:
        if os.path.exists(archivo):
            try:
                result = subprocess.run([sys.executable, '-m', 'py_compile', archivo], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"✅ {archivo} - Sintaxis correcta")
                else:
                    error_msg = f"❌ {archivo} - Error: {result.stderr.strip()}"
                    print(error_msg)
                    errores.append(error_msg)
            except subprocess.TimeoutExpired:
                error_msg = f"❌ {archivo} - Timeout compilando"
                print(error_msg)
                errores.append(error_msg)
            except Exception as e:
                error_msg = f"❌ {archivo} - Error: {e}"
                print(error_msg)
                errores.append(error_msg)
        else:
            error_msg = f"❌ {archivo} - Archivo no encontrado"
            print(error_msg)
            errores.append(error_msg)
    
    return errores

def test_imports():
    """Probar imports críticos"""
    print("\n=== PROBANDO IMPORTS ===")
    
    errores = []
    
    # Probar imports básicos
    try:
        import json
        import sqlite3
        import logging
        from datetime import datetime
        print("✅ Imports básicos - OK")
    except Exception as e:
        error_msg = f"❌ Imports básicos - Error: {e}"
        print(error_msg)
        errores.append(error_msg)
    
    # Probar imports de Flask (simulados)
    try:
        # Simular imports de Flask para testing
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Verificar que los archivos existen
        if os.path.exists('api_belgrano_ahorro.py'):
            print("✅ api_belgrano_ahorro.py - Archivo existe")
        else:
            errores.append("❌ api_belgrano_ahorro.py - Archivo faltante")
        
        if os.path.exists('belgrano_client.py'):
            print("✅ belgrano_client.py - Archivo existe")
        else:
            errores.append("❌ belgrano_client.py - Archivo faltante")
        
        if os.path.exists('devops_persistence.py'):
            print("✅ devops_persistence.py - Archivo existe")
        else:
            errores.append("❌ devops_persistence.py - Archivo faltante")
            
    except Exception as e:
        error_msg = f"❌ Error verificando archivos: {e}"
        print(error_msg)
        errores.append(error_msg)
    
    return errores

def test_database_creation():
    """Probar creación de base de datos"""
    print("\n=== PROBANDO CREACIÓN DE BASE DE DATOS ===")
    
    errores = []
    
    try:
        # Crear base de datos de prueba
        import sqlite3
        
        db_path = 'test_belgrano_ahorro.db'
        
        # Crear base de datos
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Crear tabla de prueba
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            ''')
            
            # Insertar dato de prueba
            cursor.execute('INSERT INTO test_table (name) VALUES (?)', ('test',))
            conn.commit()
            
            # Verificar inserción
            cursor.execute('SELECT * FROM test_table WHERE name = ?', ('test',))
            row = cursor.fetchone()
            
            if row:
                print("✅ Base de datos - Creación exitosa")
            else:
                errores.append("❌ Base de datos - Error en inserción")
        
        # Limpiar archivo de prueba
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Base de datos - Limpieza exitosa")
            
    except Exception as e:
        error_msg = f"❌ Base de datos - Error: {e}"
        print(error_msg)
        errores.append(error_msg)
    
    return errores

def test_file_structure():
    """Probar estructura de archivos"""
    print("\n=== PROBANDO ESTRUCTURA DE ARCHIVOS ===")
    
    errores = []
    
    archivos_requeridos = [
        'app_unificado.py',
        'api_belgrano_ahorro.py',
        'belgrano_client.py',
        'devops_persistence.py',
        'belgrano_tickets/app.py',
        'belgrano_tickets/templates/devops/negocios.html',
        'belgrano_tickets/templates/devops/productos.html',
        'belgrano_tickets/templates/devops/ofertas.html',
        'belgrano_tickets/templates/devops/precios.html'
    ]
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            # Verificar que el archivo no esté vacío
            if os.path.getsize(archivo) > 0:
                print(f"✅ {archivo} - Existe y no está vacío")
            else:
                error_msg = f"❌ {archivo} - Archivo vacío"
                print(error_msg)
                errores.append(error_msg)
        else:
            error_msg = f"❌ {archivo} - Archivo faltante"
            print(error_msg)
            errores.append(error_msg)
    
    return errores

def test_configuration():
    """Probar configuración"""
    print("\n=== PROBANDO CONFIGURACIÓN ===")
    
    errores = []
    
    # Verificar variables de entorno
    variables_requeridas = [
        'FLASK_ENV',
        'BELGRANO_AHORRO_URL',
        'BELGRANO_AHORRO_API_KEY',
        'BELGRANO_AHORRO_DB_PATH'
    ]
    
    for var in variables_requeridas:
        if var in os.environ:
            valor = os.environ[var]
            if valor:
                print(f"✅ {var} - Configurada: {valor[:20]}...")
            else:
                error_msg = f"❌ {var} - Vacía"
                print(error_msg)
                errores.append(error_msg)
        else:
            error_msg = f"❌ {var} - No configurada"
            print(error_msg)
            errores.append(error_msg)
    
    return errores

def test_gunicorn_simulation():
    """Simular comando gunicorn"""
    print("\n=== SIMULANDO GUNICORN ===")
    
    errores = []
    
    try:
        # Verificar que app_unificado.py tiene la variable app
        with open('app_unificado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'app = Flask(__name__)' in contenido:
            print("✅ app_unificado.py - Variable app definida")
        else:
            error_msg = "❌ app_unificado.py - Variable app no encontrada"
            print(error_msg)
            errores.append(error_msg)
        
        if 'if __name__ == "__main__":' in contenido:
            print("✅ app_unificado.py - Punto de entrada encontrado")
        else:
            error_msg = "❌ app_unificado.py - Punto de entrada no encontrado"
            print(error_msg)
            errores.append(error_msg)
        
        # Verificar que la API está registrada
        if 'app.register_blueprint(api_bp)' in contenido:
            print("✅ app_unificado.py - API registrada")
        else:
            error_msg = "❌ app_unificado.py - API no registrada"
            print(error_msg)
            errores.append(error_msg)
            
    except Exception as e:
        error_msg = f"❌ Error verificando gunicorn: {e}"
        print(error_msg)
        errores.append(error_msg)
    
    return errores

def cleanup():
    """Limpiar archivos de prueba"""
    print("\n=== LIMPIANDO ARCHIVOS DE PRUEBA ===")
    
    archivos_limpiar = [
        'test_belgrano_ahorro.db',
        '__pycache__',
        '*.pyc'
    ]
    
    for archivo in archivos_limpiar:
        if os.path.exists(archivo):
            if os.path.isdir(archivo):
                shutil.rmtree(archivo)
            else:
                os.remove(archivo)
            print(f"✅ {archivo} - Eliminado")

def main():
    """Función principal de build local"""
    print("=== BUILD LOCAL PARA TESTING ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurar entorno
    setup_environment()
    
    # Ejecutar pruebas
    pruebas = [
        ("Sintaxis", test_syntax),
        ("Imports", test_imports),
        ("Base de Datos", test_database_creation),
        ("Estructura de Archivos", test_file_structure),
        ("Configuración", test_configuration),
        ("Simulación Gunicorn", test_gunicorn_simulation)
    ]
    
    todos_errores = []
    
    for nombre, funcion in pruebas:
        try:
            errores = funcion()
            todos_errores.extend(errores)
        except Exception as e:
            error_msg = f"❌ Error en {nombre}: {e}"
            print(error_msg)
            todos_errores.append(error_msg)
    
    # Limpiar
    cleanup()
    
    # Resumen final
    print("\n" + "="*60)
    print("=== RESUMEN DEL BUILD LOCAL ===")
    
    if not todos_errores:
        print("🎉 ¡BUILD LOCAL EXITOSO!")
        print("✅ Todos los tests pasaron")
        print("✅ El sistema está listo para deploy")
        print("✅ No se encontraron errores críticos")
        print("\n🚀 LISTO PARA DEPLOY EN PRODUCCIÓN")
        return True
    else:
        print("⚠️ BUILD LOCAL CON ERRORES:")
        for error in todos_errores:
            print(f"   {error}")
        print("\n❌ NO PROCEDER CON DEPLOY")
        print("❌ Corregir errores antes de continuar")
        return False

if __name__ == "__main__":
    main()

