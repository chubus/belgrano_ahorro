#!/usr/bin/env python3
"""
Script para configurar y ejecutar Belgrano Tickets
"""

import os
import sys
import subprocess

def configurar_belgrano_tickets():
    """Configurar Belgrano Tickets para ejecutarse en puerto 5001"""
    
    print("🎫 Configurando Belgrano Tickets...")
    
    # Cambiar al directorio de belgrano_tickets
    os.chdir("belgrano_tickets")
    
    # Verificar si existe app.py
    if not os.path.exists("app.py"):
        print("❌ No se encontró app.py en belgrano_tickets/")
        return False
    
    # Crear archivo de configuración para puerto 5001
    config_content = '''
# Configuración para ejecutar en puerto 5001
if __name__ == "__main__":
    print("🎫 Iniciando Belgrano Tickets en puerto 5001...")
    print("📱 Abre tu navegador en: http://localhost:5001")
    print("⏹️ Presiona Ctrl+C para detener")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
'''
    
    # Agregar configuración al final de app.py si no existe
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "socketio.run(app" not in content:
        with open("app.py", "a", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ Configuración agregada a app.py")
    
    return True

def ejecutar_belgrano_tickets():
    """Ejecutar Belgrano Tickets"""
    
    print("🚀 Ejecutando Belgrano Tickets...")
    
    try:
        # Cambiar al directorio
        os.chdir("belgrano_tickets")
        
        # Ejecutar la aplicación
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("⏹️ Belgrano Tickets detenido")
    except Exception as e:
        print(f"❌ Error al ejecutar Belgrano Tickets: {e}")
    finally:
        # Volver al directorio principal
        os.chdir("..")

if __name__ == "__main__":
    if configurar_belgrano_tickets():
        ejecutar_belgrano_tickets()
    else:
        print("❌ No se pudo configurar Belgrano Tickets")
