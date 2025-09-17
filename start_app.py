#!/usr/bin/env python3
"""
Script de inicio para la aplicación Belgrano Ahorro
"""

import os
import sys
import subprocess
import time

def verificar_dependencias():
    """Verificar que todas las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    dependencias = [
        'flask',
        'werkzeug'
    ]
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - NO INSTALADO")
            print(f"   💡 Instala con: pip install {dep}")
            return False
    
    return True

def verificar_archivos():
    """Verificar que todos los archivos necesarios existan"""
    print("\n📁 Verificando archivos...")
    
    archivos = [
        'app.py',
        'database.py',
        'productos.json',
        'templates/base.html',
        'templates/perfil.html',
        'templates/login.html',
        'templates/registro.html'
    ]
    
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - NO EXISTE")
            return False
    
    return True

def inicializar_base_datos():
    """Inicializar la base de datos si no existe"""
    print("\n🗄️ Verificando base de datos...")
    
    if not os.path.exists('belgrano_ahorro.db'):
        print("   📊 Creando base de datos...")
        try:
            import db as database
            database.crear_base_datos()
            database.insertar_datos_iniciales()
            print("   ✅ Base de datos creada exitosamente")
        except Exception as e:
            print(f"   ❌ Error creando base de datos: {e}")
            return False
    else:
        print("   ✅ Base de datos ya existe")
    
    return True

def iniciar_aplicacion():
    """Iniciar la aplicación Flask"""
    print("\n🚀 Iniciando aplicación...")
    print("📱 Abre tu navegador en: http://localhost:5000")
    print("⏹️  Presiona Ctrl+C para detener")
    
    try:
        # Ejecutar la aplicación
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error ejecutando la aplicación: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🎯 Iniciando Belgrano Ahorro...")
    print("=" * 50)
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("\n❌ Faltan dependencias. Instálalas y vuelve a intentar.")
        return False
    
    # Verificar archivos
    if not verificar_archivos():
        print("\n❌ Faltan archivos necesarios.")
        return False
    
    # Inicializar base de datos
    if not inicializar_base_datos():
        print("\n❌ Error inicializando base de datos.")
        return False
    
    print("\n✅ Todo listo!")
    print("=" * 50)
    
    # Iniciar aplicación
    return iniciar_aplicacion()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 