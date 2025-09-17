#!/usr/bin/env python3
"""
Script de prueba para verificar la base de datos
"""

import db as database
import sys

def test_database():
    print("🧪 Probando base de datos...")
    
    try:
        # Probar crear usuario
        print("1. Probando crear usuario...")
        exito, mensaje = database.crear_usuario(
            nombre="Usuario Test",
            email="test@test.com",
            password="123456",
            telefono="11-1234-5678",
            direccion="Test Address"
        )
        print(f"   Resultado: {exito} - {mensaje}")
        
        # Probar verificar usuario
        print("2. Probando verificar usuario...")
        exito, resultado = database.verificar_usuario("test@test.com", "123456")
        print(f"   Resultado: {exito} - {resultado}")
        
        # Probar obtener usuario
        if exito and isinstance(resultado, dict):
            print("3. Probando obtener usuario...")
            usuario = database.obtener_usuario_por_id(resultado['id'])
            print(f"   Usuario: {usuario}")
        
        # Probar historial de sesiones
        if exito and isinstance(resultado, dict):
            print("4. Probando historial de sesiones...")
            sesiones = database.obtener_historial_sesiones(resultado['id'], 5)
            print(f"   Sesiones: {len(sesiones)} encontradas")
        
        print("✅ Todas las pruebas pasaron correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1) 