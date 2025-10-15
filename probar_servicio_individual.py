#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba individual de cada servicio
"""

import os
import sys
import subprocess
import time
import requests

def probar_belgrano_ahorro():
    """Probar Belgrano Ahorro individualmente"""
    print("🌐 PROBANDO BELGRANO AHORRO")
    print("-" * 40)
    
    env = os.environ.copy()
    env['FLASK_PORT'] = '5000'
    env['FLASK_ENV'] = 'development'
    env['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    
    try:
        print("🚀 Iniciando Belgrano Ahorro...")
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Esperando 10 segundos...")
        time.sleep(10)
        
        if proceso.poll() is None:
            print("✅ Belgrano Ahorro está corriendo")
            
            # Probar conectividad
            try:
                response = requests.get('http://localhost:5000', timeout=5)
                print(f"✅ Conectividad: Status {response.status_code}")
            except Exception as e:
                print(f"❌ Conectividad: {e}")
            
            proceso.terminate()
            proceso.wait()
            print("✅ Belgrano Ahorro funcionó correctamente")
            return True
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Belgrano Ahorro falló:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_ticketera():
    """Probar Ticketera individualmente"""
    print("\n🎫 PROBANDO TICKETERA")
    print("-" * 40)
    
    env = os.environ.copy()
    env['FLASK_PORT'] = '5001'
    env['FLASK_ENV'] = 'development'
    env['TICKETERA_URL'] = 'http://localhost:5001'
    env['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    
    try:
        print("🚀 Iniciando Ticketera...")
        proceso = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Esperando 10 segundos...")
        time.sleep(10)
        
        if proceso.poll() is None:
            print("✅ Ticketera está corriendo")
            
            # Probar conectividad
            try:
                response = requests.get('http://localhost:5001', timeout=5)
                print(f"✅ Conectividad: Status {response.status_code}")
            except Exception as e:
                print(f"❌ Conectividad: {e}")
            
            # Probar DevOps
            try:
                response = requests.get('http://localhost:5001/devops', timeout=5)
                print(f"✅ DevOps: Status {response.status_code}")
            except Exception as e:
                print(f"❌ DevOps: {e}")
            
            proceso.terminate()
            proceso.wait()
            print("✅ Ticketera funcionó correctamente")
            return True
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Ticketera falló:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_ambos_servicios():
    """Probar ambos servicios juntos"""
    print("\n🔄 PROBANDO AMBOS SERVICIOS JUNTOS")
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
        
        time.sleep(5)
        
        # Iniciar Ticketera
        print("🚀 Iniciando Ticketera...")
        procesos['ticketera'] = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env={**os.environ, 'FLASK_PORT': '5001', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(10)
        
        # Verificar ambos
        servicios = [
            ("Belgrano Ahorro", "http://localhost:5000"),
            ("Ticketera", "http://localhost:5001"),
            ("DevOps", "http://localhost:5001/devops")
        ]
        
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=5)
                print(f"✅ {nombre}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {nombre}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Limpiar
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"🛑 {nombre} detenido")

def main():
    print("=" * 60)
    print("🧪 PRUEBAS INDIVIDUALES DE SERVICIOS")
    print("=" * 60)
    
    # Probar Belgrano Ahorro
    belgrano_ok = probar_belgrano_ahorro()
    
    # Probar Ticketera
    ticketera_ok = probar_ticketera()
    
    # Probar ambos juntos
    ambos_ok = probar_ambos_servicios()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Belgrano Ahorro: {'✅ PASS' if belgrano_ok else '❌ FAIL'}")
    print(f"Ticketera: {'✅ PASS' if ticketera_ok else '❌ FAIL'}")
    print(f"Ambos juntos: {'✅ PASS' if ambos_ok else '❌ FAIL'}")
    
    if belgrano_ok and ticketera_ok and ambos_ok:
        print("\n🎉 TODOS LOS SERVICIOS FUNCIONAN CORRECTAMENTE")
    else:
        print("\n⚠️ ALGUNOS SERVICIOS TIENEN PROBLEMAS")
        print("🔧 Revisar logs arriba para identificar fallas específicas")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Prueba individual de cada servicio
"""

import os
import sys
import subprocess
import time
import requests

def probar_belgrano_ahorro():
    """Probar Belgrano Ahorro individualmente"""
    print("🌐 PROBANDO BELGRANO AHORRO")
    print("-" * 40)
    
    env = os.environ.copy()
    env['FLASK_PORT'] = '5000'
    env['FLASK_ENV'] = 'development'
    env['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    
    try:
        print("🚀 Iniciando Belgrano Ahorro...")
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Esperando 10 segundos...")
        time.sleep(10)
        
        if proceso.poll() is None:
            print("✅ Belgrano Ahorro está corriendo")
            
            # Probar conectividad
            try:
                response = requests.get('http://localhost:5000', timeout=5)
                print(f"✅ Conectividad: Status {response.status_code}")
            except Exception as e:
                print(f"❌ Conectividad: {e}")
            
            proceso.terminate()
            proceso.wait()
            print("✅ Belgrano Ahorro funcionó correctamente")
            return True
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Belgrano Ahorro falló:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_ticketera():
    """Probar Ticketera individualmente"""
    print("\n🎫 PROBANDO TICKETERA")
    print("-" * 40)
    
    env = os.environ.copy()
    env['FLASK_PORT'] = '5001'
    env['FLASK_ENV'] = 'development'
    env['TICKETERA_URL'] = 'http://localhost:5001'
    env['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    
    try:
        print("🚀 Iniciando Ticketera...")
        proceso = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Esperando 10 segundos...")
        time.sleep(10)
        
        if proceso.poll() is None:
            print("✅ Ticketera está corriendo")
            
            # Probar conectividad
            try:
                response = requests.get('http://localhost:5001', timeout=5)
                print(f"✅ Conectividad: Status {response.status_code}")
            except Exception as e:
                print(f"❌ Conectividad: {e}")
            
            # Probar DevOps
            try:
                response = requests.get('http://localhost:5001/devops', timeout=5)
                print(f"✅ DevOps: Status {response.status_code}")
            except Exception as e:
                print(f"❌ DevOps: {e}")
            
            proceso.terminate()
            proceso.wait()
            print("✅ Ticketera funcionó correctamente")
            return True
        else:
            stdout, stderr = proceso.communicate()
            print(f"❌ Ticketera falló:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_ambos_servicios():
    """Probar ambos servicios juntos"""
    print("\n🔄 PROBANDO AMBOS SERVICIOS JUNTOS")
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
        
        time.sleep(5)
        
        # Iniciar Ticketera
        print("🚀 Iniciando Ticketera...")
        procesos['ticketera'] = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env={**os.environ, 'FLASK_PORT': '5001', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(10)
        
        # Verificar ambos
        servicios = [
            ("Belgrano Ahorro", "http://localhost:5000"),
            ("Ticketera", "http://localhost:5001"),
            ("DevOps", "http://localhost:5001/devops")
        ]
        
        for nombre, url in servicios:
            try:
                response = requests.get(url, timeout=5)
                print(f"✅ {nombre}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {nombre}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Limpiar
        for nombre, proceso in procesos.items():
            if proceso and proceso.poll() is None:
                proceso.terminate()
                proceso.wait()
                print(f"🛑 {nombre} detenido")

def main():
    print("=" * 60)
    print("🧪 PRUEBAS INDIVIDUALES DE SERVICIOS")
    print("=" * 60)
    
    # Probar Belgrano Ahorro
    belgrano_ok = probar_belgrano_ahorro()
    
    # Probar Ticketera
    ticketera_ok = probar_ticketera()
    
    # Probar ambos juntos
    ambos_ok = probar_ambos_servicios()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Belgrano Ahorro: {'✅ PASS' if belgrano_ok else '❌ FAIL'}")
    print(f"Ticketera: {'✅ PASS' if ticketera_ok else '❌ FAIL'}")
    print(f"Ambos juntos: {'✅ PASS' if ambos_ok else '❌ FAIL'}")
    
    if belgrano_ok and ticketera_ok and ambos_ok:
        print("\n🎉 TODOS LOS SERVICIOS FUNCIONAN CORRECTAMENTE")
    else:
        print("\n⚠️ ALGUNOS SERVICIOS TIENEN PROBLEMAS")
        print("🔧 Revisar logs arriba para identificar fallas específicas")

if __name__ == "__main__":
    main()


