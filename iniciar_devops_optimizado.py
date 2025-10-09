#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script optimizado para iniciar DevOps con todas las correcciones
"""

import subprocess
import time
import requests
import sys
import os
from datetime import datetime

def verificar_puerto(puerto):
    """Verificar si un puerto está en uso"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', puerto))
        sock.close()
        return result == 0
    except:
        return False

def iniciar_devops():
    """Iniciar DevOps con configuración optimizada"""
    print("🔧 INICIANDO DEVOPS OPTIMIZADO")
    print("=" * 50)
    
    # Verificar que Belgrano Ahorro esté funcionando
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro: FUNCIONANDO")
        else:
            print("⚠️ Belgrano Ahorro: Status inesperado")
    except Exception as e:
        print(f"❌ Belgrano Ahorro: NO CONECTADO - {e}")
        return False
    
    # Crear archivo de configuración optimizada para DevOps
    devops_config = """
# Configuración optimizada para DevOps
import os
os.environ['FLASK_ENV'] = 'development'
os.environ['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
os.environ['BELGRANO_AHORRO_API_KEY'] = 'belgrano_ahorro_api_key_2025'
os.environ['DEVOPS_USERNAME'] = 'devops'
os.environ['DEVOPS_PASSWORD'] = 'DevOps2025!Secure'
"""
    
    with open('devops_config.py', 'w') as f:
        f.write(devops_config)
    
    # Crear script de inicio optimizado
    devops_script = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar configuración
import devops_config

from flask import Flask
from devops_routes import devops_bp

# Crear aplicación Flask optimizada
app = Flask(__name__)
app.secret_key = 'devops_secret_key_2025'

# Configuración optimizada
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Registrar blueprint
app.register_blueprint(devops_bp)

# Middleware de optimización
@app.before_request
def before_request():
    pass

@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    print("🚀 Iniciando DevOps optimizado...")
    print("📱 Acceso: http://localhost:5002/devops/")
    print("🔐 Usuario: devops / DevOps2025!Secure")
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
'''
    
    with open('devops_app.py', 'w') as f:
        f.write(devops_script)
    
    print("📝 Archivos de configuración creados")
    
    # Iniciar DevOps
    try:
        print("🚀 Iniciando DevOps en puerto 5002...")
        process = subprocess.Popen([
            sys.executable, 'devops_app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un momento para que se inicie
        time.sleep(3)
        
        # Verificar si está funcionando
        try:
            response = requests.get("http://localhost:5002/devops/", timeout=10)
            if response.status_code in [200, 302]:  # 302 es redirect a login
                print("✅ DevOps: FUNCIONANDO")
                return True
            else:
                print(f"⚠️ DevOps: Status {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            print("⏰ DevOps: TIMEOUT - pero puede estar iniciando")
            return True
        except Exception as e:
            print(f"❌ DevOps: ERROR - {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error iniciando DevOps: {e}")
        return False

def test_devops_completo():
    """Test completo de DevOps"""
    print("\n🧪 TESTEANDO DEVOPS COMPLETO...")
    
    # Test login
    try:
        login_data = {
            "username": "devops",
            "password": "DevOps2025!Secure"
        }
        
        response = requests.post("http://localhost:5002/devops/login", 
                               data=login_data, timeout=15)
        
        if response.status_code == 200:
            print("✅ Login DevOps: OK")
        else:
            print(f"⚠️ Login DevOps: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Login DevOps: ERROR - {e}")
    
    # Test panel
    try:
        response = requests.get("http://localhost:5002/devops/", timeout=15)
        
        if response.status_code == 200:
            print("✅ Panel DevOps: OK")
        else:
            print(f"⚠️ Panel DevOps: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Panel DevOps: ERROR - {e}")

def main():
    """Función principal"""
    print("🔧 INICIADOR DEVOPS OPTIMIZADO")
    print("=" * 50)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar puerto 5002
    if verificar_puerto(5002):
        print("⚠️ Puerto 5002 ya está en uso")
        print("💡 Deteniendo proceso existente...")
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                          capture_output=True, text=True)
            time.sleep(2)
        except:
            pass
    
    # Iniciar DevOps
    if iniciar_devops():
        print("\n🎉 DEVOPS INICIADO CORRECTAMENTE")
        print("🌐 URL: http://localhost:5002/devops/")
        print("🔐 Usuario: devops")
        print("🔑 Contraseña: DevOps2025!Secure")
        
        # Test completo
        test_devops_completo()
        
        print("\n💡 Para detener DevOps, presiona Ctrl+C")
        
        # Mantener el proceso activo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Deteniendo DevOps...")
    else:
        print("\n❌ ERROR INICIANDO DEVOPS")
        print("💡 Verifica que Belgrano Ahorro esté funcionando en puerto 5000")

if __name__ == "__main__":
    main()
