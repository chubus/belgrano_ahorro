#!/usr/bin/env python3
"""
Script simple para verificar el estado de la aplicación
"""

import socket
import subprocess
import time

def check_port():
    """Verificar si el puerto 5000 está en uso"""
    print("🔍 Verificando puerto 5000...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("✅ Puerto 5000 está en uso")
            return True
        else:
            print("❌ Puerto 5000 no está en uso")
            return False
    except Exception as e:
        print(f"❌ Error al verificar puerto: {e}")
        return False

def check_python_processes():
    """Verificar procesos de Python ejecutándose"""
    print("\n🔍 Verificando procesos de Python...")
    
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        
        if 'python.exe' in result.stdout:
            print("✅ Hay procesos de Python ejecutándose")
            print("   Procesos encontrados:")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'python.exe' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ No hay procesos de Python ejecutándose")
            
    except Exception as e:
        print(f"❌ Error al verificar procesos: {e}")

def start_app():
    """Iniciar la aplicación"""
    print("\n🚀 Iniciando aplicación...")
    
    try:
        # Iniciar la aplicación en segundo plano
        process = subprocess.Popen(['python', 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Esperar un momento
        time.sleep(3)
        
        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("✅ Aplicación iniciada correctamente")
            return process
        else:
            print("❌ La aplicación se detuvo inmediatamente")
            stdout, stderr = process.communicate()
            print(f"   Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error al iniciar aplicación: {e}")
        return None

def main():
    """Función principal"""
    print("🎯 Verificando estado de la aplicación...")
    
    # Verificar puerto
    port_in_use = check_port()
    
    # Verificar procesos
    check_python_processes()
    
    if not port_in_use:
        print("\n💡 Iniciando aplicación...")
        process = start_app()
        
        if process:
            print("\n✅ Aplicación iniciada. Puedes acceder a:")
            print("   http://localhost:5000")
            print("   http://localhost:5000/register")
            print("   http://localhost:5000/login")
            
            print("\n🛑 Para detener la aplicación, presiona Ctrl+C")
            
            try:
                # Mantener la aplicación ejecutándose
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo aplicación...")
                process.terminate()
                process.wait()
                print("✅ Aplicación detenida")
        else:
            print("\n❌ No se pudo iniciar la aplicación")
    else:
        print("\n✅ La aplicación ya está ejecutándose")
        print("   Puedes acceder a http://localhost:5000")

if __name__ == "__main__":
    main() 