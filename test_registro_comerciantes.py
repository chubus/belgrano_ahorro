#!/usr/bin/env python3
"""
Script de prueba para verificar el registro de comerciantes
"""

import requests
import json

def test_registro_comerciantes():
    """Probar el registro de comerciantes"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Probando registro de comerciantes...")
    
    # Test 1: Verificar que la página de registro carga
    print("\n📋 Test 1: Verificar página de registro")
    try:
        response = requests.get(f"{base_url}/comerciantes/registro")
        if response.status_code == 200:
            print("✅ Página de registro accesible")
            if "Registro de Comerciante" in response.text:
                print("✅ Template cargado correctamente")
            else:
                print("⚠️ Template no contiene el título esperado")
        else:
            print(f"❌ Error al acceder a la página: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 2: Probar registro de comerciante
    print("\n🏪 Test 2: Probar registro de comerciante")
    data = {
        'nombre': 'Juan',
        'apellido': 'Comerciante',
        'email': 'juan.comerciante@test.com',
        'password': 'test123',
        'confirmar_password': 'test123',
        'telefono': '11-1234-5678',
        'direccion': 'Av. Test 123',
        'nombre_negocio': 'Supermercado Test',
        'cuit': '20-12345678-9',
        'tipo_negocio': 'Supermercado',
        'direccion_comercial': 'Av. Comercial 456',
        'telefono_comercial': '11-9876-5432'
    }
    
    try:
        response = requests.post(f"{base_url}/comerciantes/registro", data=data)
        if response.status_code == 302:  # Redirect después del registro exitoso
            print("✅ Registro exitoso - redirección detectada")
            # Verificar si redirige al login
            if 'login_comerciante' in response.headers.get('Location', ''):
                print("✅ Redirección correcta al login")
            else:
                print("⚠️ Redirección inesperada")
        elif response.status_code == 200:
            # Verificar si hay mensajes de error
            if "error" in response.text.lower() or "ya está registrado" in response.text.lower():
                print("⚠️ Usuario ya existe o error en el registro")
            else:
                print("⚠️ Respuesta inesperada")
        else:
            print(f"❌ Error en el registro: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 3: Verificar login del comerciante
    print("\n🔐 Test 3: Verificar login del comerciante")
    login_data = {
        'email': 'juan.comerciante@test.com',
        'password': 'test123'
    }
    
    try:
        response = requests.post(f"{base_url}/comerciantes/login", data=login_data)
        if response.status_code == 302:  # Redirect después del login exitoso
            print("✅ Login exitoso - redirección detectada")
            if 'comerciantes_home' in response.headers.get('Location', ''):
                print("✅ Redirección correcta al dashboard")
            else:
                print("⚠️ Redirección inesperada")
        elif response.status_code == 200:
            if "incorrecta" in response.text.lower() or "no encontrado" in response.text.lower():
                print("⚠️ Credenciales incorrectas o usuario no existe")
            else:
                print("⚠️ Respuesta inesperada en login")
        else:
            print(f"❌ Error en el login: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_verificar_servicio():
    """Verificar que el servicio esté funcionando"""
    print("\n🔍 Verificando servicio...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Belgrano Ahorro está funcionando")
            return True
        else:
            print(f"⚠️ Belgrano Ahorro responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar con Belgrano Ahorro: {e}")
        print("   Asegúrate de que esté ejecutándose en http://localhost:5000")
        return False

if __name__ == "__main__":
    print("🎯 PRUEBA DE REGISTRO DE COMERCIANTES")
    print("=" * 60)
    
    if test_verificar_servicio():
        test_registro_comerciantes()
    
    print("\n🎯 Pruebas completadas")
