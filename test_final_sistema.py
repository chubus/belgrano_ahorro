#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba final del sistema de registro y login
Verifica que todo funcione correctamente
"""

import sqlite3
import hashlib
import secrets
import random
import string
from datetime import datetime

def generar_email_unico():
    """Generar un email único para pruebas"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
    return f"test_{timestamp}_{random_str}@test.com"

def test_sistema_completo():
    """Probar todo el sistema de registro y login"""
    print("="*60)
    print("🧪 PRUEBA FINAL DEL SISTEMA")
    print("="*60)
    
    # Generar datos únicos
    email = generar_email_unico()
    password = "TestPassword123!"
    
    print(f"📧 Email de prueba: {email}")
    print(f"🔑 Password: {password}")
    
    try:
        # 1. Importar módulo db
        print("\n1️⃣ Importando módulo db...")
        import db
        print("✅ Módulo db importado correctamente")
        
        # 2. Verificar base de datos
        print("\n2️⃣ Verificando base de datos...")
        db.crear_base_datos()
        print("✅ Base de datos verificada")
        
        # 3. Crear usuario
        print("\n3️⃣ Creando usuario...")
        resultado = db.crear_usuario(
            nombre="Usuario",
            apellido="Test",
            email=email,
            password=password,
            telefono="1234567890",
            direccion="Dirección de prueba 123"
        )
        
        if resultado['exito']:
            print("✅ Usuario creado exitosamente")
            usuario_id = resultado['usuario_id']
            print(f"📋 ID de usuario: {usuario_id}")
        else:
            print(f"❌ Error creando usuario: {resultado['mensaje']}")
            return False
        
        # 4. Verificar usuario
        print("\n4️⃣ Verificando usuario...")
        resultado = db.verificar_usuario(email, password)
        if resultado['exito']:
            print("✅ Usuario verificado correctamente")
            print(f"📋 Datos: {resultado['usuario']}")
        else:
            print(f"❌ Error verificando usuario: {resultado['mensaje']}")
            return False
        
        # 5. Buscar usuario por email
        print("\n5️⃣ Buscando usuario por email...")
        usuario = db.buscar_usuario_por_email(email)
        if usuario:
            print("✅ Usuario encontrado por email")
            print(f"📋 Datos: {usuario}")
        else:
            print("❌ Usuario no encontrado por email")
            return False
        
        # 6. Probar login con password incorrecto
        print("\n6️⃣ Probando login con password incorrecto...")
        resultado = db.verificar_usuario(email, "password_incorrecto")
        if not resultado['exito']:
            print("✅ Login con password incorrecto rechazado correctamente")
        else:
            print("❌ Login con password incorrecto fue aceptado")
            return False
        
        # 7. Probar login con email inexistente
        print("\n7️⃣ Probando login con email inexistente...")
        resultado = db.verificar_usuario("inexistente@test.com", password)
        if not resultado['exito']:
            print("✅ Login con email inexistente rechazado correctamente")
        else:
            print("❌ Login con email inexistente fue aceptado")
            return False
        
        # 8. Limpiar usuario de prueba
        print("\n8️⃣ Limpiando usuario de prueba...")
        conn = sqlite3.connect('belgrano_ahorro.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        print("✅ Usuario de prueba eliminado")
        
        print("\n" + "="*60)
        print("🎉 ¡SISTEMA FUNCIONANDO PERFECTAMENTE!")
        print("="*60)
        print("✅ Registro de usuarios: OK")
        print("✅ Verificación de usuarios: OK")
        print("✅ Búsqueda de usuarios: OK")
        print("✅ Seguridad de passwords: OK")
        print("✅ Base de datos: OK")
        print("\n🚀 El sistema está listo para usar")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_import():
    """Probar que app.py se puede importar"""
    print("\n" + "="*60)
    print("🌐 PRUEBA DE IMPORTACIÓN DE APP.PY")
    print("="*60)
    
    try:
        # Importar app
        from app import app
        print("✅ Aplicación Flask importada correctamente")
        
        # Verificar que las rutas principales existen
        with app.test_client() as client:
            # Probar ruta principal
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Ruta '/' responde correctamente")
            else:
                print(f"⚠️ Ruta '/' responde con código {response.status_code}")
            
            # Probar ruta de registro
            response = client.get('/register')
            if response.status_code == 200:
                print("✅ Ruta '/register' responde correctamente")
            else:
                print(f"⚠️ Ruta '/register' responde con código {response.status_code}")
            
            # Probar ruta de login
            response = client.get('/login')
            if response.status_code == 200:
                print("✅ Ruta '/login' responde correctamente")
            else:
                print(f"⚠️ Ruta '/login' responde con código {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando app.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print(f"🕐 Iniciando pruebas finales: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Prueba del sistema de base de datos
    test_sistema_completo()
    
    # Prueba de la aplicación Flask
    test_app_import()
    
    print(f"\n🕐 Pruebas finales completadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Para iniciar la aplicación:")
    print("   python app.py")
    print("\n💡 Para probar en el navegador:")
    print("   http://localhost:5000")

if __name__ == "__main__":
    main() 