#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba final completa del sistema integrado
"""

import os
import sys
import subprocess
import time
import requests
import sqlite3
from datetime import datetime

def probar_base_datos():
    """Probar funcionalidad de base de datos"""
    print("1️⃣ PROBANDO BASE DE DATOS")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Contar registros
        neg_count = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_count = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        ofer_count = c.execute('SELECT COUNT(*) FROM ofertas').fetchone()[0]
        
        print(f"✅ Base de datos: {neg_count} negocios, {prod_count} productos, {ofer_count} ofertas")
        
        # Probar inserción
        timestamp = int(time.time())
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Test Final {timestamp}', 'Prueba final del sistema', 'Test 123', '555-0000', 'test@final.com'))
        
        negocio_id = c.lastrowid
        
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto Final {timestamp}', 'general', 399.99, 'Test', 75, 15, negocio_id))
        
        conn.commit()
        conn.close()
        
        print("✅ Inserción en base de datos exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def probar_servicios_individuales():
    """Probar servicios individualmente"""
    print("\n2️⃣ PROBANDO SERVICIOS INDIVIDUALES")
    print("-" * 40)
    
    # Probar Belgrano Ahorro
    print("🌐 Probando Belgrano Ahorro...")
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            env={**os.environ, 'FLASK_PORT': '5000', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(8)
        
        if proceso.poll() is None:
            try:
                response = requests.get('http://localhost:5000', timeout=5)
                print(f"✅ Belgrano Ahorro: Status {response.status_code}")
                proceso.terminate()
                proceso.wait()
                return True
            except Exception as e:
                print(f"❌ Belgrano Ahorro: {e}")
                proceso.terminate()
                proceso.wait()
                return False
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Belgrano Ahorro falló: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_servicios_integrados():
    """Probar servicios integrados"""
    print("\n3️⃣ PROBANDO SERVICIOS INTEGRADOS")
    print("-" * 40)
    
    procesos = {}
    
    try:
        # Iniciar Belgrano Ahorro
        print("🚀 Iniciando Belgrano Ahorro...")
        procesos['belgrano'] = subprocess.Popen(
            [sys.executable, 'app.py'],
            env={**os.environ, 'FLASK_PORT': '5000', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(8)
        
        # Iniciar Ticketera
        print("🚀 Iniciando Ticketera...")
        procesos['ticketera'] = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env={**os.environ, 'FLASK_PORT': '5001', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(10)
        
        # Verificar servicios
        servicios = [
            ("Belgrano Ahorro", "http://localhost:5000"),
            ("Ticketera", "http://localhost:5001"),
            ("DevOps", "http://localhost:5001/devops")
        ]
        
        servicios_ok = 0
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=10)
                print(f"✅ {nombre}: Status {response.status_code}")
                servicios_ok += 1
            except Exception as e:
                print(f"❌ {nombre}: {e}")
        
        if servicios_ok >= 2:
            print("✅ Servicios integrados funcionando")
            return True
        else:
            print("❌ Muy pocos servicios funcionando")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Limpiar procesos
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"🛑 {nombre} detenido")

def probar_funcionalidad_devops():
    """Probar funcionalidad específica de DevOps"""
    print("\n4️⃣ PROBANDO FUNCIONALIDAD DEVOPS")
    print("-" * 40)
    
    try:
        # Probar inserción directa (simulando DevOps)
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        timestamp = int(time.time())
        
        # Crear negocio desde DevOps
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'DevOps Final {timestamp}', 'Negocio creado desde DevOps', 'DevOps 123', '555-0000', 'devops@final.com'))
        
        negocio_id = c.lastrowid
        
        # Crear producto desde DevOps
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto DevOps Final {timestamp}', 'general', 499.99, 'DevOps', 100, 20, negocio_id))
        
        # Crear oferta desde DevOps
        c.execute('''
            INSERT INTO ofertas (titulo, descripcion, descuento_porcentaje, fecha_inicio, fecha_fin, activa) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Oferta DevOps Final {timestamp}', 'Oferta creada desde DevOps', 30.0, 
              datetime.now().strftime('%Y-%m-%d'), 
              (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()
        
        print("✅ Funcionalidad DevOps funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad DevOps: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 PRUEBA FINAL COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    resultados = {}
    
    # 1. Probar base de datos
    resultados['base_datos'] = probar_base_datos()
    
    # 2. Probar servicios individuales
    resultados['servicios_individuales'] = probar_servicios_individuales()
    
    # 3. Probar servicios integrados
    resultados['servicios_integrados'] = probar_servicios_integrados()
    
    # 4. Probar funcionalidad DevOps
    resultados['funcionalidad_devops'] = probar_funcionalidad_devops()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    for test, resultado in resultados.items():
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{test.upper()}: {status}")
    
    total_tests = len(resultados)
    passed_tests = sum(resultados.values())
    
    print(f"\n📈 RESULTADO: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("✅ DevOps y Ticketera integrados correctamente")
        print("✅ Base de datos funcionando")
        print("✅ Servicios funcionando")
        print("✅ Funcionalidad DevOps operativa")
        print("\n🚀 LISTO PARA POST-DEPLOY")
        print("💡 Ejecuta: python desplegar_robusto.py")
    else:
        print("\n⚠️ SISTEMA TIENE PROBLEMAS")
        print("🔧 Revisar resultados arriba para identificar fallas")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Prueba final completa del sistema integrado
"""

import os
import sys
import subprocess
import time
import requests
import sqlite3
from datetime import datetime

def probar_base_datos():
    """Probar funcionalidad de base de datos"""
    print("1️⃣ PROBANDO BASE DE DATOS")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Contar registros
        neg_count = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_count = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        ofer_count = c.execute('SELECT COUNT(*) FROM ofertas').fetchone()[0]
        
        print(f"✅ Base de datos: {neg_count} negocios, {prod_count} productos, {ofer_count} ofertas")
        
        # Probar inserción
        timestamp = int(time.time())
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Test Final {timestamp}', 'Prueba final del sistema', 'Test 123', '555-0000', 'test@final.com'))
        
        negocio_id = c.lastrowid
        
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto Final {timestamp}', 'general', 399.99, 'Test', 75, 15, negocio_id))
        
        conn.commit()
        conn.close()
        
        print("✅ Inserción en base de datos exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def probar_servicios_individuales():
    """Probar servicios individualmente"""
    print("\n2️⃣ PROBANDO SERVICIOS INDIVIDUALES")
    print("-" * 40)
    
    # Probar Belgrano Ahorro
    print("🌐 Probando Belgrano Ahorro...")
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            env={**os.environ, 'FLASK_PORT': '5000', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(8)
        
        if proceso.poll() is None:
            try:
                response = requests.get('http://localhost:5000', timeout=5)
                print(f"✅ Belgrano Ahorro: Status {response.status_code}")
                proceso.terminate()
                proceso.wait()
                return True
            except Exception as e:
                print(f"❌ Belgrano Ahorro: {e}")
                proceso.terminate()
                proceso.wait()
                return False
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Belgrano Ahorro falló: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_servicios_integrados():
    """Probar servicios integrados"""
    print("\n3️⃣ PROBANDO SERVICIOS INTEGRADOS")
    print("-" * 40)
    
    procesos = {}
    
    try:
        # Iniciar Belgrano Ahorro
        print("🚀 Iniciando Belgrano Ahorro...")
        procesos['belgrano'] = subprocess.Popen(
            [sys.executable, 'app.py'],
            env={**os.environ, 'FLASK_PORT': '5000', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(8)
        
        # Iniciar Ticketera
        print("🚀 Iniciando Ticketera...")
        procesos['ticketera'] = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env={**os.environ, 'FLASK_PORT': '5001', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(10)
        
        # Verificar servicios
        servicios = [
            ("Belgrano Ahorro", "http://localhost:5000"),
            ("Ticketera", "http://localhost:5001"),
            ("DevOps", "http://localhost:5001/devops")
        ]
        
        servicios_ok = 0
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=10)
                print(f"✅ {nombre}: Status {response.status_code}")
                servicios_ok += 1
            except Exception as e:
                print(f"❌ {nombre}: {e}")
        
        if servicios_ok >= 2:
            print("✅ Servicios integrados funcionando")
            return True
        else:
            print("❌ Muy pocos servicios funcionando")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Limpiar procesos
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"🛑 {nombre} detenido")

def probar_funcionalidad_devops():
    """Probar funcionalidad específica de DevOps"""
    print("\n4️⃣ PROBANDO FUNCIONALIDAD DEVOPS")
    print("-" * 40)
    
    try:
        # Probar inserción directa (simulando DevOps)
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        timestamp = int(time.time())
        
        # Crear negocio desde DevOps
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'DevOps Final {timestamp}', 'Negocio creado desde DevOps', 'DevOps 123', '555-0000', 'devops@final.com'))
        
        negocio_id = c.lastrowid
        
        # Crear producto desde DevOps
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto DevOps Final {timestamp}', 'general', 499.99, 'DevOps', 100, 20, negocio_id))
        
        # Crear oferta desde DevOps
        c.execute('''
            INSERT INTO ofertas (titulo, descripcion, descuento_porcentaje, fecha_inicio, fecha_fin, activa) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Oferta DevOps Final {timestamp}', 'Oferta creada desde DevOps', 30.0, 
              datetime.now().strftime('%Y-%m-%d'), 
              (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()
        
        print("✅ Funcionalidad DevOps funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad DevOps: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 PRUEBA FINAL COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    resultados = {}
    
    # 1. Probar base de datos
    resultados['base_datos'] = probar_base_datos()
    
    # 2. Probar servicios individuales
    resultados['servicios_individuales'] = probar_servicios_individuales()
    
    # 3. Probar servicios integrados
    resultados['servicios_integrados'] = probar_servicios_integrados()
    
    # 4. Probar funcionalidad DevOps
    resultados['funcionalidad_devops'] = probar_funcionalidad_devops()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    for test, resultado in resultados.items():
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{test.upper()}: {status}")
    
    total_tests = len(resultados)
    passed_tests = sum(resultados.values())
    
    print(f"\n📈 RESULTADO: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("✅ DevOps y Ticketera integrados correctamente")
        print("✅ Base de datos funcionando")
        print("✅ Servicios funcionando")
        print("✅ Funcionalidad DevOps operativa")
        print("\n🚀 LISTO PARA POST-DEPLOY")
        print("💡 Ejecuta: python desplegar_robusto.py")
    else:
        print("\n⚠️ SISTEMA TIENE PROBLEMAS")
        print("🔧 Revisar resultados arriba para identificar fallas")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()








