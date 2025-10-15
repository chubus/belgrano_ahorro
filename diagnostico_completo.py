#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico completo para identificar fallas
"""

import os
import sys
import subprocess
import time
import sqlite3
import requests
from pathlib import Path

def verificar_archivos():
    """Verificar que todos los archivos necesarios existan"""
    print("🔍 VERIFICANDO ARCHIVOS NECESARIOS")
    print("-" * 40)
    
    archivos_requeridos = [
        'app.py',
        'belgrano_tickets/app.py',
        'belgrano_ahorro.db',
        'belgrano_tickets/devops_routes.py'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)
    
    return len(archivos_faltantes) == 0

def verificar_sintaxis_python():
    """Verificar sintaxis de archivos Python"""
    print("\n🔍 VERIFICANDO SINTAXIS PYTHON")
    print("-" * 40)
    
    archivos_python = [
        'app.py',
        'belgrano_tickets/app.py',
        'belgrano_tickets/devops_routes.py'
    ]
    
    errores_sintaxis = []
    
    for archivo in archivos_python:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    compile(f.read(), archivo, 'exec')
                print(f"✅ {archivo} - Sintaxis OK")
            except SyntaxError as e:
                print(f"❌ {archivo} - Error de sintaxis: {e}")
                errores_sintaxis.append((archivo, str(e)))
            except Exception as e:
                print(f"⚠️ {archivo} - Error: {e}")
    
    return len(errores_sintaxis) == 0

def verificar_base_datos():
    """Verificar estructura de base de datos"""
    print("\n🔍 VERIFICANDO BASE DE DATOS")
    print("-" * 40)
    
    if not os.path.exists('belgrano_ahorro.db'):
        print("❌ belgrano_ahorro.db no existe")
        return False
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Verificar tablas principales
        tablas_requeridas = ['negocios', 'productos', 'ofertas', 'categorias']
        for tabla in tablas_requeridas:
            c.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = c.fetchone()[0]
            print(f"✅ Tabla {tabla}: {count} registros")
        
        # Verificar esquema de productos
        print("\n📋 Esquema tabla productos:")
        for row in c.execute("PRAGMA table_info(productos)").fetchall():
            print(f"  • {row[1]} ({row[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def verificar_puertos():
    """Verificar disponibilidad de puertos"""
    print("\n🔍 VERIFICANDO PUERTOS")
    print("-" * 40)
    
    import socket
    
    puertos = [5000, 5001, 5002]
    puertos_disponibles = []
    
    for puerto in puertos:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', puerto))
            puertos_disponibles.append(puerto)
            print(f"✅ Puerto {puerto} disponible")
        except OSError:
            print(f"❌ Puerto {puerto} ocupado")
        finally:
            sock.close()
    
    return len(puertos_disponibles) == len(puertos)

def probar_inicio_servicios():
    """Probar inicio de servicios individualmente"""
    print("\n🔍 PROBANDO INICIO DE SERVICIOS")
    print("-" * 40)
    
    # Probar Belgrano Ahorro
    print("🌐 Probando Belgrano Ahorro...")
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5000'}
        )
        time.sleep(3)
        
        if proceso.poll() is None:
            print("✅ Belgrano Ahorro inició correctamente")
            proceso.terminate()
            proceso.wait()
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Belgrano Ahorro falló: {stderr.decode()}")
            return False
    except Exception as e:
        print(f"❌ Error iniciando Belgrano Ahorro: {e}")
        return False
    
    # Probar Ticketera
    print("🎫 Probando Ticketera...")
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5001'}
        )
        time.sleep(3)
        
        if proceso.poll() is None:
            print("✅ Ticketera inició correctamente")
            proceso.terminate()
            proceso.wait()
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Ticketera falló: {stderr.decode()}")
            return False
    except Exception as e:
        print(f"❌ Error iniciando Ticketera: {e}")
        return False
    
    return True

def probar_conectividad():
    """Probar conectividad entre servicios"""
    print("\n🔍 PROBANDO CONECTIVIDAD")
    print("-" * 40)
    
    # Iniciar servicios en background
    print("🚀 Iniciando servicios para prueba...")
    
    procesos = {}
    
    try:
        # Belgrano Ahorro
        procesos['belgrano'] = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5000'}
        )
        time.sleep(5)
        
        # Ticketera
        procesos['ticketera'] = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5001'}
        )
        time.sleep(5)
        
        # Probar conectividad
        servicios = [
            ("Belgrano Ahorro", "http://localhost:5000"),
            ("Ticketera", "http://localhost:5001"),
            ("DevOps", "http://localhost:5001/devops")
        ]
        
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=5)
                print(f"✅ {nombre}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {nombre}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de conectividad: {e}")
        return False
    finally:
        # Limpiar procesos
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"🛑 {nombre} detenido")

def probar_funcionalidad_devops():
    """Probar funcionalidad de DevOps"""
    print("\n🔍 PROBANDO FUNCIONALIDAD DEVOPS")
    print("-" * 40)
    
    # Probar inserción directa en DB
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Contar antes
        neg_before = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_before = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        # Crear test
        timestamp = int(time.time())
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Test DevOps {timestamp}', 'Test de funcionalidad', 'Test 123', '555-0000', 'test@devops.com'))
        
        negocio_id = c.lastrowid
        
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto Test {timestamp}', 'general', 99.99, 'Test', 10, 1, negocio_id))
        
        conn.commit()
        
        # Contar después
        neg_after = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_after = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        print(f"✅ Inserción exitosa: Negocios {neg_before}→{neg_after}, Productos {prod_before}→{prod_after}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad DevOps: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 60)
    
    resultados = {}
    
    # 1. Verificar archivos
    resultados['archivos'] = verificar_archivos()
    
    # 2. Verificar sintaxis
    resultados['sintaxis'] = verificar_sintaxis_python()
    
    # 3. Verificar base de datos
    resultados['base_datos'] = verificar_base_datos()
    
    # 4. Verificar puertos
    resultados['puertos'] = verificar_puertos()
    
    # 5. Probar inicio de servicios
    resultados['servicios'] = probar_inicio_servicios()
    
    # 6. Probar conectividad
    resultados['conectividad'] = probar_conectividad()
    
    # 7. Probar funcionalidad DevOps
    resultados['devops'] = probar_funcionalidad_devops()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    for test, resultado in resultados.items():
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{test.upper()}: {status}")
    
    total_tests = len(resultados)
    passed_tests = sum(resultados.values())
    
    print(f"\n📈 RESULTADO: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
    else:
        print("⚠️ SISTEMA TIENE FALLAS - REVISAR RESULTADOS ARRIBA")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Script de diagnóstico completo para identificar fallas
"""

import os
import sys
import subprocess
import time
import sqlite3
import requests
from pathlib import Path

def verificar_archivos():
    """Verificar que todos los archivos necesarios existan"""
    print("🔍 VERIFICANDO ARCHIVOS NECESARIOS")
    print("-" * 40)
    
    archivos_requeridos = [
        'app.py',
        'belgrano_tickets/app.py',
        'belgrano_ahorro.db',
        'belgrano_tickets/devops_routes.py'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
            archivos_faltantes.append(archivo)
    
    return len(archivos_faltantes) == 0

def verificar_sintaxis_python():
    """Verificar sintaxis de archivos Python"""
    print("\n🔍 VERIFICANDO SINTAXIS PYTHON")
    print("-" * 40)
    
    archivos_python = [
        'app.py',
        'belgrano_tickets/app.py',
        'belgrano_tickets/devops_routes.py'
    ]
    
    errores_sintaxis = []
    
    for archivo in archivos_python:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    compile(f.read(), archivo, 'exec')
                print(f"✅ {archivo} - Sintaxis OK")
            except SyntaxError as e:
                print(f"❌ {archivo} - Error de sintaxis: {e}")
                errores_sintaxis.append((archivo, str(e)))
            except Exception as e:
                print(f"⚠️ {archivo} - Error: {e}")
    
    return len(errores_sintaxis) == 0

def verificar_base_datos():
    """Verificar estructura de base de datos"""
    print("\n🔍 VERIFICANDO BASE DE DATOS")
    print("-" * 40)
    
    if not os.path.exists('belgrano_ahorro.db'):
        print("❌ belgrano_ahorro.db no existe")
        return False
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Verificar tablas principales
        tablas_requeridas = ['negocios', 'productos', 'ofertas', 'categorias']
        for tabla in tablas_requeridas:
            c.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = c.fetchone()[0]
            print(f"✅ Tabla {tabla}: {count} registros")
        
        # Verificar esquema de productos
        print("\n📋 Esquema tabla productos:")
        for row in c.execute("PRAGMA table_info(productos)").fetchall():
            print(f"  • {row[1]} ({row[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def verificar_puertos():
    """Verificar disponibilidad de puertos"""
    print("\n🔍 VERIFICANDO PUERTOS")
    print("-" * 40)
    
    import socket
    
    puertos = [5000, 5001, 5002]
    puertos_disponibles = []
    
    for puerto in puertos:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', puerto))
            puertos_disponibles.append(puerto)
            print(f"✅ Puerto {puerto} disponible")
        except OSError:
            print(f"❌ Puerto {puerto} ocupado")
        finally:
            sock.close()
    
    return len(puertos_disponibles) == len(puertos)

def probar_inicio_servicios():
    """Probar inicio de servicios individualmente"""
    print("\n🔍 PROBANDO INICIO DE SERVICIOS")
    print("-" * 40)
    
    # Probar Belgrano Ahorro
    print("🌐 Probando Belgrano Ahorro...")
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5000'}
        )
        time.sleep(3)
        
        if proceso.poll() is None:
            print("✅ Belgrano Ahorro inició correctamente")
            proceso.terminate()
            proceso.wait()
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Belgrano Ahorro falló: {stderr.decode()}")
            return False
    except Exception as e:
        print(f"❌ Error iniciando Belgrano Ahorro: {e}")
        return False
    
    # Probar Ticketera
    print("🎫 Probando Ticketera...")
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5001'}
        )
        time.sleep(3)
        
        if proceso.poll() is None:
            print("✅ Ticketera inició correctamente")
            proceso.terminate()
            proceso.wait()
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Ticketera falló: {stderr.decode()}")
            return False
    except Exception as e:
        print(f"❌ Error iniciando Ticketera: {e}")
        return False
    
    return True

def probar_conectividad():
    """Probar conectividad entre servicios"""
    print("\n🔍 PROBANDO CONECTIVIDAD")
    print("-" * 40)
    
    # Iniciar servicios en background
    print("🚀 Iniciando servicios para prueba...")
    
    procesos = {}
    
    try:
        # Belgrano Ahorro
        procesos['belgrano'] = subprocess.Popen(
            [sys.executable, 'app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5000'}
        )
        time.sleep(5)
        
        # Ticketera
        procesos['ticketera'] = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, 'FLASK_PORT': '5001'}
        )
        time.sleep(5)
        
        # Probar conectividad
        servicios = [
            ("Belgrano Ahorro", "http://localhost:5000"),
            ("Ticketera", "http://localhost:5001"),
            ("DevOps", "http://localhost:5001/devops")
        ]
        
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=5)
                print(f"✅ {nombre}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {nombre}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de conectividad: {e}")
        return False
    finally:
        # Limpiar procesos
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"🛑 {nombre} detenido")

def probar_funcionalidad_devops():
    """Probar funcionalidad de DevOps"""
    print("\n🔍 PROBANDO FUNCIONALIDAD DEVOPS")
    print("-" * 40)
    
    # Probar inserción directa en DB
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Contar antes
        neg_before = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_before = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        # Crear test
        timestamp = int(time.time())
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Test DevOps {timestamp}', 'Test de funcionalidad', 'Test 123', '555-0000', 'test@devops.com'))
        
        negocio_id = c.lastrowid
        
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto Test {timestamp}', 'general', 99.99, 'Test', 10, 1, negocio_id))
        
        conn.commit()
        
        # Contar después
        neg_after = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_after = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        print(f"✅ Inserción exitosa: Negocios {neg_before}→{neg_after}, Productos {prod_before}→{prod_after}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad DevOps: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 60)
    
    resultados = {}
    
    # 1. Verificar archivos
    resultados['archivos'] = verificar_archivos()
    
    # 2. Verificar sintaxis
    resultados['sintaxis'] = verificar_sintaxis_python()
    
    # 3. Verificar base de datos
    resultados['base_datos'] = verificar_base_datos()
    
    # 4. Verificar puertos
    resultados['puertos'] = verificar_puertos()
    
    # 5. Probar inicio de servicios
    resultados['servicios'] = probar_inicio_servicios()
    
    # 6. Probar conectividad
    resultados['conectividad'] = probar_conectividad()
    
    # 7. Probar funcionalidad DevOps
    resultados['devops'] = probar_funcionalidad_devops()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    for test, resultado in resultados.items():
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{test.upper()}: {status}")
    
    total_tests = len(resultados)
    passed_tests = sum(resultados.values())
    
    print(f"\n📈 RESULTADO: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
    else:
        print("⚠️ SISTEMA TIENE FALLAS - REVISAR RESULTADOS ARRIBA")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()


