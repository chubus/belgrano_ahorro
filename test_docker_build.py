#!/usr/bin/env python3
import subprocess
import sys
import os

def test_docker_build():
    """Probar el build de Docker localmente"""
    print("🐳 Probando build de Docker...")
    
    try:
        # Construir la imagen
        result = subprocess.run(
            ["docker", "build", "-t", "belgrano-ahorro-test", "."],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ Build de Docker exitoso!")
            print("📋 Log del build:")
            print(result.stdout)
            return True
        else:
            print("❌ Error en el build de Docker:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout en el build de Docker")
        return False
    except FileNotFoundError:
        print("❌ Docker no está instalado o no está en el PATH")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("🚀 VERIFICACIÓN DE BUILD DOCKER")
    print("=" * 50)
    
    success = test_docker_build()
    
    if success:
        print("\n✅ El Docker está listo para deploy!")
        print("📋 Próximos pasos:")
        print("   1. docker-compose up --build")
        print("   2. O deploy en Render")
    else:
        print("\n❌ Hay problemas con el Docker")
        print("🔧 Revisar los errores arriba")

if __name__ == "__main__":
    main()
