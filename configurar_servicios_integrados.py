#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de servicios integrados: Ticketera + DevOps
Para funcionamiento en post-deploy
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Configuración de puertos
PORT_BELGRANO_AHORRO = 5000
PORT_TICKETERA_DEVOPS = 5001  # Ticketera con DevOps integrado

# Variables de entorno para servicios integrados
ENV_VARS = {
    'FLASK_ENV': 'production',
    'FLASK_DEBUG': 'False',
    'TICKETERA_URL': f'http://localhost:{PORT_TICKETERA_DEVOPS}',
    'BELGRANO_AHORRO_URL': f'http://localhost:{PORT_BELGRANO_AHORRO}',
    'DEVOPS_URL': f'http://localhost:{PORT_TICKETERA_DEVOPS}/devops',  # DevOps integrado
    'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025'
}

def verificar_puertos():
    """Verificar que los puertos estén disponibles"""
    import socket
    
    puertos = [PORT_BELGRANO_AHORRO, PORT_TICKETERA_DEVOPS]
    disponibles = []
    
    for puerto in puertos:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', puerto))
            disponibles.append(puerto)
            print(f"✅ Puerto {puerto} disponible")
        except OSError:
            print(f"❌ Puerto {puerto} ocupado")
        finally:
            sock.close()
    
    return len(disponibles) == len(puertos)

def iniciar_belgrano_ahorro():
    """Iniciar Belgrano Ahorro en puerto 5000"""
    print(f"🚀 Iniciando Belgrano Ahorro en puerto {PORT_BELGRANO_AHORRO}...")
    
    env = os.environ.copy()
    env.update(ENV_VARS)
    env['FLASK_PORT'] = str(PORT_BELGRANO_AHORRO)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Belgrano Ahorro iniciado (PID: {proceso.pid})")
        return proceso
    except Exception as e:
        print(f"❌ Error iniciando Belgrano Ahorro: {e}")
        return None

def iniciar_ticketera_devops():
    """Iniciar Ticketera con DevOps integrado en puerto 5001"""
    print(f"🚀 Iniciando Ticketera + DevOps integrado en puerto {PORT_TICKETERA_DEVOPS}...")
    
    env = os.environ.copy()
    env.update(ENV_VARS)
    env['FLASK_PORT'] = str(PORT_TICKETERA_DEVOPS)
    env['TICKETERA_PORT'] = str(PORT_TICKETERA_DEVOPS)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Ticketera + DevOps iniciado (PID: {proceso.pid})")
        return proceso
    except Exception as e:
        print(f"❌ Error iniciando Ticketera + DevOps: {e}")
        return None

def verificar_servicios():
    """Verificar que los servicios estén funcionando"""
    import requests
    import time
    
    print("\n🔍 Verificando servicios...")
    time.sleep(5)  # Dar tiempo para que inicien
    
    servicios = [
        ("Belgrano Ahorro", f"http://localhost:{PORT_BELGRANO_AHORRO}"),
        ("Ticketera", f"http://localhost:{PORT_TICKETERA_DEVOPS}"),
        ("DevOps", f"http://localhost:{PORT_TICKETERA_DEVOPS}/devops")
    ]
    
    for nombre, url in servicios:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {nombre}: Funcionando")
            else:
                print(f"⚠️ {nombre}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {nombre}: {e}")

def crear_script_despliegue():
    """Crear script de despliegue para producción"""
    script_content = f'''#!/bin/bash
# Script de despliegue para servicios integrados

echo "🚀 Iniciando servicios integrados..."

# Variables de entorno
export FLASK_ENV=production
export FLASK_DEBUG=False
export TICKETERA_URL=http://localhost:{PORT_TICKETERA_DEVOPS}
export BELGRANO_AHORRO_URL=http://localhost:{PORT_BELGRANO_AHORRO}
export DEVOPS_URL=http://localhost:{PORT_TICKETERA_DEVOPS}/devops
export BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Iniciar Belgrano Ahorro
echo "🌐 Iniciando Belgrano Ahorro..."
python app.py &
BELGRANO_PID=$!

# Esperar un momento
sleep 3

# Iniciar Ticketera + DevOps
echo "🎫 Iniciando Ticketera + DevOps..."
python belgrano_tickets/app.py &
TICKETERA_PID=$!

echo "✅ Servicios iniciados:"
echo "   🌐 Belgrano Ahorro: http://localhost:{PORT_BELGRANO_AHORRO}"
echo "   🎫 Ticketera:      http://localhost:{PORT_TICKETERA_DEVOPS}"
echo "   🔧 DevOps:         http://localhost:{PORT_TICKETERA_DEVOPS}/devops"

# Función para detener servicios
cleanup() {{
    echo "🛑 Deteniendo servicios..."
    kill $BELGRANO_PID $TICKETERA_PID 2>/dev/null
    exit 0
}}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Mantener script corriendo
wait
'''
    
    with open('desplegar_servicios_integrados.sh', 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable en sistemas Unix
    try:
        os.chmod('desplegar_servicios_integrados.sh', 0o755)
    except:
        pass
    
    print("✅ Script de despliegue creado: desplegar_servicios_integrados.sh")

def main():
    print("=" * 60)
    print("🔧 CONFIGURACIÓN SERVICIOS INTEGRADOS")
    print("   Ticketera + DevOps en un solo servidor")
    print("=" * 60)
    
    # Verificar puertos
    if not verificar_puertos():
        print("❌ Algunos puertos no están disponibles")
        return
    
    # Crear script de despliegue
    crear_script_despliegue()
    
    print("\n📋 CONFIGURACIÓN COMPLETADA:")
    print(f"🌐 Belgrano Ahorro: Puerto {PORT_BELGRANO_AHORRO}")
    print(f"🎫 Ticketera:      Puerto {PORT_TICKETERA_DEVOPS}")
    print(f"🔧 DevOps:         Puerto {PORT_TICKETERA_DEVOPS}/devops (integrado)")
    
    print("\n💡 Para iniciar los servicios:")
    print("   python configurar_servicios_integrados.py --start")
    print("   o ejecuta: ./desplegar_servicios_integrados.sh")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--start':
        # Iniciar servicios
        print("🚀 Iniciando servicios integrados...")
        
        proceso_ahorro = iniciar_belgrano_ahorro()
        if not proceso_ahorro:
            print("❌ No se pudo iniciar Belgrano Ahorro")
            sys.exit(1)
        
        time.sleep(3)
        
        proceso_ticketera = iniciar_ticketera_devops()
        if not proceso_ticketera:
            print("❌ No se pudo iniciar Ticketera + DevOps")
            proceso_ahorro.terminate()
            sys.exit(1)
        
        verificar_servicios()
        
        print("\n✅ Servicios integrados iniciados correctamente")
        print("💡 Para detener, presiona Ctrl+C")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servicios...")
            proceso_ahorro.terminate()
            proceso_ticketera.terminate()
            print("✅ Servicios detenidos")
    else:
        main()

# -*- coding: utf-8 -*-
"""
Configuración de servicios integrados: Ticketera + DevOps
Para funcionamiento en post-deploy
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Configuración de puertos
PORT_BELGRANO_AHORRO = 5000
PORT_TICKETERA_DEVOPS = 5001  # Ticketera con DevOps integrado

# Variables de entorno para servicios integrados
ENV_VARS = {
    'FLASK_ENV': 'production',
    'FLASK_DEBUG': 'False',
    'TICKETERA_URL': f'http://localhost:{PORT_TICKETERA_DEVOPS}',
    'BELGRANO_AHORRO_URL': f'http://localhost:{PORT_BELGRANO_AHORRO}',
    'DEVOPS_URL': f'http://localhost:{PORT_TICKETERA_DEVOPS}/devops',  # DevOps integrado
    'BELGRANO_AHORRO_API_KEY': 'belgrano_ahorro_api_key_2025'
}

def verificar_puertos():
    """Verificar que los puertos estén disponibles"""
    import socket
    
    puertos = [PORT_BELGRANO_AHORRO, PORT_TICKETERA_DEVOPS]
    disponibles = []
    
    for puerto in puertos:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', puerto))
            disponibles.append(puerto)
            print(f"✅ Puerto {puerto} disponible")
        except OSError:
            print(f"❌ Puerto {puerto} ocupado")
        finally:
            sock.close()
    
    return len(disponibles) == len(puertos)

def iniciar_belgrano_ahorro():
    """Iniciar Belgrano Ahorro en puerto 5000"""
    print(f"🚀 Iniciando Belgrano Ahorro en puerto {PORT_BELGRANO_AHORRO}...")
    
    env = os.environ.copy()
    env.update(ENV_VARS)
    env['FLASK_PORT'] = str(PORT_BELGRANO_AHORRO)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Belgrano Ahorro iniciado (PID: {proceso.pid})")
        return proceso
    except Exception as e:
        print(f"❌ Error iniciando Belgrano Ahorro: {e}")
        return None

def iniciar_ticketera_devops():
    """Iniciar Ticketera con DevOps integrado en puerto 5001"""
    print(f"🚀 Iniciando Ticketera + DevOps integrado en puerto {PORT_TICKETERA_DEVOPS}...")
    
    env = os.environ.copy()
    env.update(ENV_VARS)
    env['FLASK_PORT'] = str(PORT_TICKETERA_DEVOPS)
    env['TICKETERA_PORT'] = str(PORT_TICKETERA_DEVOPS)
    
    try:
        proceso = subprocess.Popen(
            [sys.executable, 'belgrano_tickets/app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"✅ Ticketera + DevOps iniciado (PID: {proceso.pid})")
        return proceso
    except Exception as e:
        print(f"❌ Error iniciando Ticketera + DevOps: {e}")
        return None

def verificar_servicios():
    """Verificar que los servicios estén funcionando"""
    import requests
    import time
    
    print("\n🔍 Verificando servicios...")
    time.sleep(5)  # Dar tiempo para que inicien
    
    servicios = [
        ("Belgrano Ahorro", f"http://localhost:{PORT_BELGRANO_AHORRO}"),
        ("Ticketera", f"http://localhost:{PORT_TICKETERA_DEVOPS}"),
        ("DevOps", f"http://localhost:{PORT_TICKETERA_DEVOPS}/devops")
    ]
    
    for nombre, url in servicios:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {nombre}: Funcionando")
            else:
                print(f"⚠️ {nombre}: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {nombre}: {e}")

def crear_script_despliegue():
    """Crear script de despliegue para producción"""
    script_content = f'''#!/bin/bash
# Script de despliegue para servicios integrados

echo "🚀 Iniciando servicios integrados..."

# Variables de entorno
export FLASK_ENV=production
export FLASK_DEBUG=False
export TICKETERA_URL=http://localhost:{PORT_TICKETERA_DEVOPS}
export BELGRANO_AHORRO_URL=http://localhost:{PORT_BELGRANO_AHORRO}
export DEVOPS_URL=http://localhost:{PORT_TICKETERA_DEVOPS}/devops
export BELGRANO_AHORRO_API_KEY=belgrano_ahorro_api_key_2025

# Iniciar Belgrano Ahorro
echo "🌐 Iniciando Belgrano Ahorro..."
python app.py &
BELGRANO_PID=$!

# Esperar un momento
sleep 3

# Iniciar Ticketera + DevOps
echo "🎫 Iniciando Ticketera + DevOps..."
python belgrano_tickets/app.py &
TICKETERA_PID=$!

echo "✅ Servicios iniciados:"
echo "   🌐 Belgrano Ahorro: http://localhost:{PORT_BELGRANO_AHORRO}"
echo "   🎫 Ticketera:      http://localhost:{PORT_TICKETERA_DEVOPS}"
echo "   🔧 DevOps:         http://localhost:{PORT_TICKETERA_DEVOPS}/devops"

# Función para detener servicios
cleanup() {{
    echo "🛑 Deteniendo servicios..."
    kill $BELGRANO_PID $TICKETERA_PID 2>/dev/null
    exit 0
}}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Mantener script corriendo
wait
'''
    
    with open('desplegar_servicios_integrados.sh', 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable en sistemas Unix
    try:
        os.chmod('desplegar_servicios_integrados.sh', 0o755)
    except:
        pass
    
    print("✅ Script de despliegue creado: desplegar_servicios_integrados.sh")

def main():
    print("=" * 60)
    print("🔧 CONFIGURACIÓN SERVICIOS INTEGRADOS")
    print("   Ticketera + DevOps en un solo servidor")
    print("=" * 60)
    
    # Verificar puertos
    if not verificar_puertos():
        print("❌ Algunos puertos no están disponibles")
        return
    
    # Crear script de despliegue
    crear_script_despliegue()
    
    print("\n📋 CONFIGURACIÓN COMPLETADA:")
    print(f"🌐 Belgrano Ahorro: Puerto {PORT_BELGRANO_AHORRO}")
    print(f"🎫 Ticketera:      Puerto {PORT_TICKETERA_DEVOPS}")
    print(f"🔧 DevOps:         Puerto {PORT_TICKETERA_DEVOPS}/devops (integrado)")
    
    print("\n💡 Para iniciar los servicios:")
    print("   python configurar_servicios_integrados.py --start")
    print("   o ejecuta: ./desplegar_servicios_integrados.sh")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--start':
        # Iniciar servicios
        print("🚀 Iniciando servicios integrados...")
        
        proceso_ahorro = iniciar_belgrano_ahorro()
        if not proceso_ahorro:
            print("❌ No se pudo iniciar Belgrano Ahorro")
            sys.exit(1)
        
        time.sleep(3)
        
        proceso_ticketera = iniciar_ticketera_devops()
        if not proceso_ticketera:
            print("❌ No se pudo iniciar Ticketera + DevOps")
            proceso_ahorro.terminate()
            sys.exit(1)
        
        verificar_servicios()
        
        print("\n✅ Servicios integrados iniciados correctamente")
        print("💡 Para detener, presiona Ctrl+C")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servicios...")
            proceso_ahorro.terminate()
            proceso_ticketera.terminate()
            print("✅ Servicios detenidos")
    else:
        main()


