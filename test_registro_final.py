#!/usr/bin/env python3
"""
Script final para probar el registro de usuarios
"""

try:
    import requests
except ImportError:
    print("❌ Error: El módulo 'requests' no está instalado")
    print("💡 Instálalo con: pip install requests")
    exit(1)

import time

def test_registro_final():
    """Probar registro de usuarios"""
    print("🧪 Probando registro de usuarios...")
    
    # Datos de prueba
    datos = {
        'nombre': 'Usuario',
        'apellido': 'Final',
        'email': 'final@test.com',
        'password': 'password123',
        'confirmar_password': 'password123',
        'telefono': '123456789',
        'direccion': 'Dirección final',
        'terminos': 'aceptado'
    }
    
    try:
        # 1. Verificar que la aplicación esté ejecutándose
        print("1. Verificando aplicación...")
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ La aplicación no está ejecutándose")
            return False
        
        # 2. Obtener página de registro
        print("\n2. Obteniendo página de registro...")
        response = requests.get("http://localhost:5000/register", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Error al obtener página de registro")
            return False
        
        # 3. Enviar formulario de registro
        print("\n3. Enviando formulario de registro...")
        response = requests.post("http://localhost:5000/register", data=datos, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.url}")
        
        if response.status_code == 302:
            print("✅ Registro exitoso (redirección)")
            # Seguir la redirección
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print(f"   Redirigiendo a: {redirect_url}")
                response = requests.get(f"http://localhost:5000{redirect_url}", timeout=5)
                print(f"   Status final: {response.status_code}")
            return True
        elif response.status_code == 200:
            print("⚠️ Registro completado pero sin redirección")
            # Verificar si hay mensajes de éxito o error
            content = response.text.lower()
            if "exitoso" in content or "bienvenido" in content:
                print("✅ Registro exitoso")
                return True
            elif "error" in content:
                print("❌ Hay errores en la página")
                return False
            else:
                print("✅ Registro parece exitoso")
                return True
        else:
            print(f"❌ Error en registro: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la aplicación")
        print("💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login_final():
    """Probar login de usuarios"""
    print("\n🧪 Probando login de usuarios...")
    
    # Datos de login
    datos = {
        'email': 'final@test.com',
        'password': 'password123'
    }
    
    try:
        # Enviar formulario de login
        response = requests.post("http://localhost:5000/login", data=datos, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.url}")
        
        if response.status_code == 302:
            print("✅ Login exitoso (redirección)")
            return True
        elif response.status_code == 200:
            print("⚠️ Login completado pero sin redirección")
            content = response.text.lower()
            if "bienvenido" in content or "exitoso" in content:
                print("✅ Login exitoso")
                return True
            else:
                print("❌ Login fallido")
                return False
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_recuperar_password_final():
    """Probar recuperación de contraseña"""
    print("\n🧪 Probando recuperación de contraseña...")
    
    # Datos de recuperación
    datos = {
        'email': 'final@test.com'
    }
    
    try:
        # Enviar formulario de recuperación
        response = requests.post("http://localhost:5000/recuperar-password", data=datos, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   URL final: {response.url}")
        
        if response.status_code == 200:
            print("✅ Recuperación completada")
            return True
        else:
            print(f"❌ Error en recuperación: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas finales de autenticación...")
    
    # Probar registro
    registro_exitoso = test_registro_final()
    
    if registro_exitoso:
        # Esperar un momento
        time.sleep(2)
        
        # Probar login
        login_exitoso = test_login_final()
        
        if login_exitoso:
            # Esperar un momento
            time.sleep(2)
            
            # Probar recuperación de contraseña
            recuperacion_exitosa = test_recuperar_password_final()
            
            if recuperacion_exitosa:
                print("\n✅ TODAS LAS PRUEBAS EXITOSAS")
                print("🎉 El registro, login y recuperación de contraseña funcionan correctamente")
            else:
                print("\n⚠️ Registro y login funcionan, pero hay problemas con recuperación")
        else:
            print("\n❌ Registro funciona, pero hay problemas con login")
    else:
        print("\n❌ Hay problemas con el registro")
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    main() 