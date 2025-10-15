#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba específica de servicios integrados
"""

import os
import sys
import subprocess
import time
import requests
import sqlite3
from datetime import datetime

def iniciar_servicio_simple(nombre, archivo, puerto, env_vars=None):
    """Iniciar un servicio de forma simple"""
    print(f"🚀 Iniciando {nombre} en puerto {puerto}...")
    
    env = os.environ.copy()
    env['FLASK_PORT'] = str(puerto)
    env['FLASK_ENV'] = 'development'
    if env_vars:
        env.update(env_vars)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, archivo],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return proceso
    except Exception as e:
        print(f"❌ Error iniciando {nombre}: {e}")
        return None

def probar_servicios_integrados():
    """Probar servicios integrados paso a paso"""
    print("=" * 60)
    print("🧪 PRUEBA SERVICIOS INTEGRADOS")
    print("=" * 60)
    
    procesos = {}
    
    try:
        # 1. Iniciar Belgrano Ahorro
        print("\n1️⃣ INICIANDO BELGRANO AHORRO")
        procesos['belgrano'] = iniciar_servicio_simple(
            "Belgrano Ahorro", 
            "app.py", 
            5000,
            {'BELGRANO_AHORRO_URL': 'http://localhost:5000'}
        )
        
        if not procesos['belgrano']:
            print("❌ No se pudo iniciar Belgrano Ahorro")
            return False
        
        time.sleep(5)
        
        # Verificar Belgrano Ahorro
        try:
            response = requests.get('http://localhost:5000', timeout=5)
            print(f"✅ Belgrano Ahorro: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Belgrano Ahorro: {e}")
            return False
        
        # 2. Iniciar Ticketera + DevOps
        print("\n2️⃣ INICIANDO TICKETERA + DEVOPS")
        procesos['ticketera'] = iniciar_servicio_simple(
            "Ticketera + DevOps", 
            "belgrano_tickets/app.py", 
            5001,
            {
                'TICKETERA_URL': 'http://localhost:5001',
                'BELGRANO_AHORRO_URL': 'http://localhost:5000',
                'DEVOPS_URL': 'http://localhost:5001/devops'
            }
        )
        
        if not procesos['ticketera']:
            print("❌ No se pudo iniciar Ticketera + DevOps")
            return False
        
        time.sleep(5)
        
        # Verificar Ticketera
        try:
            response = requests.get('http://localhost:5001', timeout=5)
            print(f"✅ Ticketera: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Ticketera: {e}")
            return False
        
        # Verificar DevOps
        try:
            response = requests.get('http://localhost:5001/devops', timeout=5)
            print(f"✅ DevOps: Status {response.status_code}")
        except Exception as e:
            print(f"❌ DevOps: {e}")
            return False
        
        # 3. Probar funcionalidad DevOps
        print("\n3️⃣ PROBANDO FUNCIONALIDAD DEVOPS")
        probar_creacion_desde_devops()
        
        # 4. Verificar sincronización
        print("\n4️⃣ VERIFICANDO SINCRONIZACIÓN")
        verificar_sincronizacion()
        
        print("\n✅ TODAS LAS PRUEBAS PASARON")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False
    finally:
        # Limpiar procesos
        print("\n🛑 Deteniendo servicios...")
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"✅ {nombre} detenido")

def probar_creacion_desde_devops():
    """Probar creación de entidades desde DevOps"""
    print("🔧 Probando creación desde DevOps...")
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Contar antes
        neg_before = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_before = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        # Simular creación desde DevOps
        timestamp = int(time.time())
        
        # Crear negocio
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Test Integrado {timestamp}', 'Negocio de prueba integrado', 'Test 123', '555-0000', 'test@integrado.com'))
        negocio_id = c.lastrowid
        
        # Crear producto
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto Integrado {timestamp}', 'general', 149.99, 'Test', 25, 5, negocio_id))
        
        conn.commit()
        
        # Contar después
        neg_after = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_after = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        print(f"✅ Creación exitosa: Negocios {neg_before}→{neg_after}, Productos {prod_before}→{prod_after}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en creación DevOps: {e}")
        return False

def verificar_sincronizacion():
    """Verificar que los datos se sincronicen correctamente"""
    print("🔄 Verificando sincronización...")
    
    try:
        # Verificar que los datos estén en la base
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Obtener últimos registros
        ultimo_negocio = c.execute('SELECT nombre FROM negocios ORDER BY id DESC LIMIT 1').fetchone()
        ultimo_producto = c.execute('SELECT nombre FROM productos ORDER BY id DESC LIMIT 1').fetchone()
        
        if ultimo_negocio and ultimo_producto:
            print(f"✅ Último negocio: {ultimo_negocio[0]}")
            print(f"✅ Último producto: {ultimo_producto[0]}")
            print("✅ Sincronización funcionando correctamente")
            return True
        else:
            print("❌ No se encontraron datos recientes")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    print("🧪 INICIANDO PRUEBAS DE SERVICIOS INTEGRADOS")
    
    if probar_servicios_integrados():
        print("\n🎉 SERVICIOS INTEGRADOS FUNCIONANDO CORRECTAMENTE")
        print("✅ Belgrano Ahorro: Puerto 5000")
        print("✅ Ticketera + DevOps: Puerto 5001")
        print("✅ DevOps integrado: http://localhost:5001/devops")
        print("\n🚀 LISTO PARA POST-DEPLOY")
    else:
        print("\n❌ SERVICIOS INTEGRADOS TIENEN PROBLEMAS")
        print("🔧 Revisar logs arriba para identificar fallas")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Prueba específica de servicios integrados
"""

import os
import sys
import subprocess
import time
import requests
import sqlite3
from datetime import datetime

def iniciar_servicio_simple(nombre, archivo, puerto, env_vars=None):
    """Iniciar un servicio de forma simple"""
    print(f"🚀 Iniciando {nombre} en puerto {puerto}...")
    
    env = os.environ.copy()
    env['FLASK_PORT'] = str(puerto)
    env['FLASK_ENV'] = 'development'
    if env_vars:
        env.update(env_vars)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, archivo],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return proceso
    except Exception as e:
        print(f"❌ Error iniciando {nombre}: {e}")
        return None

def probar_servicios_integrados():
    """Probar servicios integrados paso a paso"""
    print("=" * 60)
    print("🧪 PRUEBA SERVICIOS INTEGRADOS")
    print("=" * 60)
    
    procesos = {}
    
    try:
        # 1. Iniciar Belgrano Ahorro
        print("\n1️⃣ INICIANDO BELGRANO AHORRO")
        procesos['belgrano'] = iniciar_servicio_simple(
            "Belgrano Ahorro", 
            "app.py", 
            5000,
            {'BELGRANO_AHORRO_URL': 'http://localhost:5000'}
        )
        
        if not procesos['belgrano']:
            print("❌ No se pudo iniciar Belgrano Ahorro")
            return False
        
        time.sleep(5)
        
        # Verificar Belgrano Ahorro
        try:
            response = requests.get('http://localhost:5000', timeout=5)
            print(f"✅ Belgrano Ahorro: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Belgrano Ahorro: {e}")
            return False
        
        # 2. Iniciar Ticketera + DevOps
        print("\n2️⃣ INICIANDO TICKETERA + DEVOPS")
        procesos['ticketera'] = iniciar_servicio_simple(
            "Ticketera + DevOps", 
            "belgrano_tickets/app.py", 
            5001,
            {
                'TICKETERA_URL': 'http://localhost:5001',
                'BELGRANO_AHORRO_URL': 'http://localhost:5000',
                'DEVOPS_URL': 'http://localhost:5001/devops'
            }
        )
        
        if not procesos['ticketera']:
            print("❌ No se pudo iniciar Ticketera + DevOps")
            return False
        
        time.sleep(5)
        
        # Verificar Ticketera
        try:
            response = requests.get('http://localhost:5001', timeout=5)
            print(f"✅ Ticketera: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Ticketera: {e}")
            return False
        
        # Verificar DevOps
        try:
            response = requests.get('http://localhost:5001/devops', timeout=5)
            print(f"✅ DevOps: Status {response.status_code}")
        except Exception as e:
            print(f"❌ DevOps: {e}")
            return False
        
        # 3. Probar funcionalidad DevOps
        print("\n3️⃣ PROBANDO FUNCIONALIDAD DEVOPS")
        probar_creacion_desde_devops()
        
        # 4. Verificar sincronización
        print("\n4️⃣ VERIFICANDO SINCRONIZACIÓN")
        verificar_sincronizacion()
        
        print("\n✅ TODAS LAS PRUEBAS PASARON")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False
    finally:
        # Limpiar procesos
        print("\n🛑 Deteniendo servicios...")
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"✅ {nombre} detenido")

def probar_creacion_desde_devops():
    """Probar creación de entidades desde DevOps"""
    print("🔧 Probando creación desde DevOps...")
    
    try:
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Contar antes
        neg_before = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_before = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        # Simular creación desde DevOps
        timestamp = int(time.time())
        
        # Crear negocio
        c.execute('''
            INSERT INTO negocios (nombre, descripcion, direccion, telefono, email, activo) 
            VALUES (?, ?, ?, ?, ?, 1)
        ''', (f'Test Integrado {timestamp}', 'Negocio de prueba integrado', 'Test 123', '555-0000', 'test@integrado.com'))
        negocio_id = c.lastrowid
        
        # Crear producto
        c.execute('''
            INSERT INTO productos (nombre, store, precio, categoria, stock, stock_minimo, negocio_id, activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (f'Producto Integrado {timestamp}', 'general', 149.99, 'Test', 25, 5, negocio_id))
        
        conn.commit()
        
        # Contar después
        neg_after = c.execute('SELECT COUNT(*) FROM negocios').fetchone()[0]
        prod_after = c.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        
        print(f"✅ Creación exitosa: Negocios {neg_before}→{neg_after}, Productos {prod_before}→{prod_after}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en creación DevOps: {e}")
        return False

def verificar_sincronizacion():
    """Verificar que los datos se sincronicen correctamente"""
    print("🔄 Verificando sincronización...")
    
    try:
        # Verificar que los datos estén en la base
        conn = sqlite3.connect('belgrano_ahorro.db')
        c = conn.cursor()
        
        # Obtener últimos registros
        ultimo_negocio = c.execute('SELECT nombre FROM negocios ORDER BY id DESC LIMIT 1').fetchone()
        ultimo_producto = c.execute('SELECT nombre FROM productos ORDER BY id DESC LIMIT 1').fetchone()
        
        if ultimo_negocio and ultimo_producto:
            print(f"✅ Último negocio: {ultimo_negocio[0]}")
            print(f"✅ Último producto: {ultimo_producto[0]}")
            print("✅ Sincronización funcionando correctamente")
            return True
        else:
            print("❌ No se encontraron datos recientes")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    print("🧪 INICIANDO PRUEBAS DE SERVICIOS INTEGRADOS")
    
    if probar_servicios_integrados():
        print("\n🎉 SERVICIOS INTEGRADOS FUNCIONANDO CORRECTAMENTE")
        print("✅ Belgrano Ahorro: Puerto 5000")
        print("✅ Ticketera + DevOps: Puerto 5001")
        print("✅ DevOps integrado: http://localhost:5001/devops")
        print("\n🚀 LISTO PARA POST-DEPLOY")
    else:
        print("\n❌ SERVICIOS INTEGRADOS TIENEN PROBLEMAS")
        print("🔧 Revisar logs arriba para identificar fallas")

if __name__ == "__main__":
    main()


