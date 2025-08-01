#!/usr/bin/env python3
"""
Script de prueba directa con la base de datos
"""

import db as database
import hashlib
import secrets

def test_registro_directo():
    """Probar registro directamente con la base de datos"""
    print("🧪 Probando registro directo con la base de datos...")
    
    # Datos de prueba
    nombre = "Usuario"
    apellido = "Prueba"
    email = "prueba3@test.com"
    password = "password123"
    telefono = "123456789"
    direccion = "Dirección de prueba"
    
    try:
        # Intentar crear usuario
        resultado = database.crear_usuario(nombre, apellido, email, password, telefono, direccion)
        print(f"Resultado: {resultado}")
        
        if resultado['exito']:
            print("✅ Usuario creado exitosamente")
            
            # Verificar que se puede buscar
            usuario = database.buscar_usuario_por_email(email)
            print(f"Usuario encontrado: {usuario}")
            
            # Verificar login
            resultado_login = database.verificar_usuario(email, password)
            print(f"Login exitoso: {resultado_login}")
            
        else:
            print(f"❌ Error al crear usuario: {resultado['mensaje']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_login_directo():
    """Probar login directamente con la base de datos"""
    print("\n🧪 Probando login directo con la base de datos...")
    
    email = "prueba3@test.com"
    password = "password123"
    
    try:
        resultado = database.verificar_usuario(email, password)
        print(f"Resultado login: {resultado}")
        
        if resultado['exito']:
            print("✅ Login exitoso")
        else:
            print("❌ Login fallido")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_recuperar_password_directo():
    """Probar recuperación de contraseña directamente"""
    print("\n🧪 Probando recuperación de contraseña directa...")
    
    email = "prueba3@test.com"
    
    try:
        usuario = database.buscar_usuario_por_email(email)
        print(f"Usuario encontrado: {usuario}")
        
        if usuario:
            # Generar token
            import datetime
            token = "TEST123"
            expiracion = datetime.datetime.now() + datetime.timedelta(hours=24)
            
            exito = database.guardar_token_recuperacion(usuario['id'], token, expiracion)
            print(f"Token guardado: {exito}")
            
            # Verificar token
            token_valido = database.verificar_token_recuperacion(email, token)
            print(f"Token verificado: {token_valido}")
            
        else:
            print("❌ Usuario no encontrado")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas directas con la base de datos...")
    
    # Probar registro
    test_registro_directo()
    
    # Probar login
    test_login_directo()
    
    # Probar recuperación de contraseña
    test_recuperar_password_directo()
    
    print("\n✅ Pruebas completadas") 