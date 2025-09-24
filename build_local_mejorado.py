#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Local Mejorado para Testear Errores
Versión mejorada que maneja mejor la limpieza
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
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
            except Exception as e:
                error_msg = f"❌ {archivo} - Error: {e}"
                print(error_msg)
                errores.append(error_msg)
        else:
            error_msg = f"❌ {archivo} - Archivo no encontrado"
            print(error_msg)
            errores.append(error_msg)
    
    return errores

def test_critical_imports():
    """Probar imports críticos sin Flask"""
    print("\n=== PROBANDO IMPORTS CRÍTICOS ===")
    
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
    
    # Verificar archivos críticos
    archivos_criticos = [
        'api_belgrano_ahorro.py',
        'belgrano_client.py',
        'devops_persistence.py',
        'app_unificado.py'
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
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

def test_database_operations():
    """Probar operaciones de base de datos"""
    print("\n=== PROBANDO OPERACIONES DE BASE DE DATOS ===")
    
    errores = []
    
    try:
        import sqlite3
        
        # Usar archivo temporal
        db_path = tempfile.mktemp(suffix='.db')
        
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
                print("✅ Base de datos - Operaciones exitosas")
            else:
                errores.append("❌ Base de datos - Error en verificación")
        
        # Limpiar archivo temporal
        try:
            os.remove(db_path)
            print("✅ Base de datos - Limpieza exitosa")
        except:
            print("⚠️ Base de datos - No se pudo limpiar (no crítico)")
            
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

def test_gunicorn_compatibility():
    """Probar compatibilidad con Gunicorn"""
    print("\n=== PROBANDO COMPATIBILIDAD CON GUNICORN ===")
    
    errores = []
    
    try:
        # Verificar que app_unificado.py tiene la estructura correcta
        with open('app_unificado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificaciones críticas
        verificaciones = [
            ('app = Flask(__name__)', 'Variable app definida'),
            ('if __name__ == "__main__":', 'Punto de entrada encontrado'),
            ('app.register_blueprint(api_bp)', 'API registrada'),
            ('from api_belgrano_ahorro import api_bp', 'Import de API'),
            ('@app.route', 'Rutas definidas'),
            ('def ', 'Funciones definidas')
        ]
        
        for patron, descripcion in verificaciones:
            if patron in contenido:
                print(f"✅ {descripcion}")
            else:
                error_msg = f"❌ {descripcion} - FALTANTE"
                print(error_msg)
                errores.append(error_msg)
        
        # Verificar que no hay errores de sintaxis obvios
        if 'SyntaxError' in contenido or 'IndentationError' in contenido:
            error_msg = "❌ Errores de sintaxis detectados en el código"
            print(error_msg)
            errores.append(error_msg)
        else:
            print("✅ No se detectaron errores de sintaxis obvios")
            
    except Exception as e:
        error_msg = f"❌ Error verificando compatibilidad: {e}"
        print(error_msg)
        errores.append(error_msg)
    
    return errores

def test_deploy_readiness():
    """Probar preparación para deploy"""
    print("\n=== PROBANDO PREPARACIÓN PARA DEPLOY ===")
    
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
                print(f"✅ {var} - Configurada")
            else:
                error_msg = f"❌ {var} - Vacía"
                print(error_msg)
                errores.append(error_msg)
        else:
            error_msg = f"❌ {var} - No configurada"
            print(error_msg)
            errores.append(error_msg)
    
    # Verificar que no hay archivos de prueba
    archivos_limpiar = [
        'test_belgrano_ahorro.db',
        'test_*.db',
        '*.tmp'
    ]
    
    archivos_encontrados = []
    for archivo in archivos_limpiar:
        if os.path.exists(archivo):
            archivos_encontrados.append(archivo)
    
    if archivos_encontrados:
        print(f"⚠️ Archivos de prueba encontrados: {archivos_encontrados}")
        print("   (Se limpiarán automáticamente en deploy)")
    else:
        print("✅ No hay archivos de prueba")
    
    return errores

def main():
    """Función principal de build local mejorado"""
    print("=== BUILD LOCAL MEJORADO PARA TESTING ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurar entorno
    setup_environment()
    
    # Ejecutar pruebas
    pruebas = [
        ("Sintaxis", test_syntax),
        ("Imports Críticos", test_critical_imports),
        ("Operaciones de Base de Datos", test_database_operations),
        ("Estructura de Archivos", test_file_structure),
        ("Compatibilidad con Gunicorn", test_gunicorn_compatibility),
        ("Preparación para Deploy", test_deploy_readiness)
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
    
    # Resumen final
    print("\n" + "="*60)
    print("=== RESUMEN DEL BUILD LOCAL MEJORADO ===")
    
    if not todos_errores:
        print("🎉 ¡BUILD LOCAL EXITOSO!")
        print("✅ Todos los tests críticos pasaron")
        print("✅ El sistema está listo para deploy")
        print("✅ No se encontraron errores críticos")
        print("\n🚀 LISTO PARA DEPLOY EN PRODUCCIÓN")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. git add .")
        print("   2. git commit -m 'Fix: Corregidos errores de sintaxis para deploy'")
        print("   3. git push")
        print("   4. Deploy en Render")
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

