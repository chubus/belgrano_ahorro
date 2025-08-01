#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba completa del sistema de registro de usuarios
Simula el proceso completo desde frontend hasta base de datos
"""

import requests
import json
import time
import random
import string
from datetime import datetime

def generar_email_unico():
    """Generar un email único para pruebas"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
    return f"test_{timestamp}_{random_str}@test.com"

def test_registro_completo():
    """Probar el registro completo de usuarios"""
    print("="*60)
    print("🧪 PRUEBA COMPLETA DE REGISTRO DE USUARIOS")
    print("="*60)
    
    # URL base de la aplicación
    base_url = "http://localhost:5000"
    
    # Generar datos únicos para la prueba
    email = generar_email_unico()
    password = "TestPassword123!"
    
    datos_registro = {
        'nombre': 'Usuario',
        'apellido': 'Test',
        'email': email,
        'password': password,
        'confirmar_password': password,
        'telefono': '1234567890',
        'direccion': 'Dirección de prueba 123',
        'terminos': 'aceptado'
    }
    
    print(f"📧 Email de prueba: {email}")
    print(f"🔑 Password: {password}")
    
    try:
        # 1. Verificar que la aplicación esté corriendo
        print("\n1️⃣ Verificando que la aplicación esté corriendo...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicación respondiendo correctamente")
        else:
            print(f"❌ Aplicación no responde correctamente: {response.status_code}")
            return False
        
        # 2. Obtener la página de registro
        print("\n2️⃣ Obteniendo página de registro...")
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code == 200:
            print("✅ Página de registro accesible")
        else:
            print(f"❌ Error accediendo a página de registro: {response.status_code}")
            return False
        
        # 3. Enviar formulario de registro
        print("\n3️⃣ Enviando formulario de registro...")
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(
            f"{base_url}/register",
            data=datos_registro,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )
        
        print(f"📊 Código de respuesta: {response.status_code}")
        print(f"📊 URL final: {response.url}")
        
        # Verificar si el registro fue exitoso
        if response.status_code == 200:
            if "login" in response.url or "index" in response.url:
                print("✅ Registro exitoso - redirigido correctamente")
            else:
                print("⚠️ Registro puede haber fallado - revisar contenido")
                print(f"Contenido de respuesta: {response.text[:500]}...")
        elif response.status_code == 302:
            print("✅ Registro exitoso - redirección 302")
        else:
            print(f"❌ Error en registro: {response.status_code}")
            print(f"Contenido de respuesta: {response.text[:500]}...")
            return False
        
        # 4. Probar login con el usuario creado
        print("\n4️⃣ Probando login con usuario creado...")
        datos_login = {
            'email': email,
            'password': password
        }
        
        response = requests.post(
            f"{base_url}/login",
            data=datos_login,
            headers=headers,
            allow_redirects=True,
            timeout=10
        )
        
        print(f"📊 Código de respuesta login: {response.status_code}")
        print(f"📊 URL final login: {response.url}")
        
        if response.status_code in [200, 302]:
            if "perfil" in response.url or "index" in response.url:
                print("✅ Login exitoso")
            else:
                print("⚠️ Login puede haber fallado")
        else:
            print(f"❌ Error en login: {response.status_code}")
        
        # 5. Probar acceso al perfil
        print("\n5️⃣ Probando acceso al perfil...")
        response = requests.get(f"{base_url}/perfil", timeout=5)
        if response.status_code == 200:
            print("✅ Perfil accesible")
        else:
            print(f"⚠️ Perfil no accesible: {response.status_code}")
        
        print("\n" + "="*60)
        print("🎉 PRUEBA COMPLETADA")
        print("="*60)
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - La aplicación no está corriendo")
        print("💡 Ejecuta: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_database_directo():
    """Probar funciones de base de datos directamente"""
    print("\n" + "="*60)
    print("🗄️ PRUEBA DIRECTA DE BASE DE DATOS")
    print("="*60)
    
    try:
        import db
        
        # Generar datos únicos
        email = generar_email_unico()
        password = "TestPassword123!"
        
        print(f"📧 Email de prueba BD: {email}")
        
        # 1. Crear usuario
        print("\n1️⃣ Creando usuario en BD...")
        resultado = db.crear_usuario(
            nombre="Usuario",
            apellido="Test",
            email=email,
            password=password,
            telefono="1234567890",
            direccion="Dirección de prueba 123"
        )
        
        if resultado['exito']:
            print("✅ Usuario creado en BD correctamente")
            usuario_id = resultado['usuario_id']
            print(f"📋 ID de usuario: {usuario_id}")
        else:
            print(f"❌ Error creando usuario: {resultado['mensaje']}")
            return False
        
        # 2. Verificar usuario
        print("\n2️⃣ Verificando usuario en BD...")
        resultado = db.verificar_usuario(email, password)
        if resultado['exito']:
            print("✅ Usuario verificado correctamente")
            print(f"📋 Usuario: {resultado['usuario']}")
        else:
            print(f"❌ Error verificando usuario: {resultado['mensaje']}")
            return False
        
        # 3. Buscar usuario por email
        print("\n3️⃣ Buscando usuario por email...")
        usuario = db.buscar_usuario_por_email(email)
        if usuario:
            print("✅ Usuario encontrado por email")
            print(f"📋 Datos: {usuario}")
        else:
            print("❌ Usuario no encontrado por email")
            return False
        
        # 4. Limpiar usuario de prueba
        print("\n4️⃣ Limpiando usuario de prueba...")
        import sqlite3
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        print("✅ Usuario de prueba eliminado")
        
        print("\n" + "="*60)
        print("🎉 PRUEBA DE BD COMPLETADA")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de BD: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print(f"🕐 Iniciando pruebas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Prueba directa de base de datos
    test_database_directo()
    
    # Prueba completa del sistema
    test_registro_completo()
    
    print(f"\n🕐 Pruebas completadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Si las pruebas fallan, verifica que:")
    print("   1. La aplicación esté corriendo (python app.py)")
    print("   2. No haya errores en la consola")
    print("   3. El puerto 5000 esté disponible")

if __name__ == "__main__":
    main() 