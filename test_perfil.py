#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DE PERFIL - BELGRANO AHORRO
================================

Script para probar que el perfil de usuario funcione correctamente
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import db as database
    print("✅ Módulo db importado correctamente")
except Exception as e:
    print(f"❌ Error importando db: {e}")
    sys.exit(1)

def test_obtener_usuario():
    """Probar obtener usuario por ID"""
    print("🔍 Probando obtener_usuario_por_id...")
    
    # Crear un usuario de prueba si no existe
    try:
        # Intentar obtener un usuario existente
        usuario = database.obtener_usuario_por_id(1)
        if usuario:
            print("✅ Usuario encontrado:")
            print(f"   ID: {usuario.get('id')}")
            print(f"   Nombre: {usuario.get('nombre')}")
            print(f"   Email: {usuario.get('email')}")
            print(f"   Teléfono: {usuario.get('telefono')}")
            print(f"   Dirección: {usuario.get('direccion')}")
            print(f"   Rol: {usuario.get('rol')}")
            print(f"   Fecha registro: {usuario.get('fecha_registro')}")
            
            # Verificar que todos los campos necesarios estén presentes
            campos_requeridos = ['id', 'nombre', 'email', 'telefono', 'direccion', 'rol', 'fecha_registro']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in usuario]
            
            if campos_faltantes:
                print(f"⚠️  Campos faltantes: {campos_faltantes}")
            else:
                print("✅ Todos los campos están presentes")
                
        else:
            print("⚠️  No se encontró usuario con ID 1")
            print("   Creando usuario de prueba...")
            
            # Crear usuario de prueba
            resultado = database.crear_usuario(
                nombre="Usuario",
                apellido="Prueba", 
                email="test@test.com",
                password="123456",
                telefono="123456789",
                direccion="Dirección de prueba"
            )
            
            if resultado:
                print("✅ Usuario de prueba creado")
                usuario = database.obtener_usuario_por_id(1)
                if usuario:
                    print("✅ Usuario de prueba obtenido correctamente")
                    print(f"   Fecha registro: {usuario.get('fecha_registro')}")
            else:
                print("❌ Error creando usuario de prueba")
                
    except Exception as e:
        print(f"❌ Error en test_obtener_usuario: {e}")

def test_campos_usuario():
    """Probar que todos los campos del usuario estén disponibles"""
    print("\n🔍 Probando campos del usuario...")
    
    usuario = database.obtener_usuario_por_id(1)
    if usuario:
        # Simular el procesamiento que hace la función perfil()
        usuario_procesado = {
            'id': usuario.get('id'),
            'nombre': usuario.get('nombre', 'Usuario'),
            'email': usuario.get('email', ''),
            'telefono': usuario.get('telefono', ''),
            'direccion': usuario.get('direccion', ''),
            'rol': usuario.get('rol', 'cliente'),
            'fecha_registro': usuario.get('fecha_registro')
        }
        
        print("✅ Usuario procesado correctamente:")
        for campo, valor in usuario_procesado.items():
            print(f"   {campo}: {valor}")
            
        # Verificar que fecha_registro se maneje correctamente
        if usuario_procesado['fecha_registro']:
            try:
                fecha_corta = usuario_procesado['fecha_registro'][:10]
                print(f"✅ Fecha registro procesada: {fecha_corta}")
            except Exception as e:
                print(f"❌ Error procesando fecha: {e}")
        else:
            print("⚠️  Fecha registro es None - se mostrará 'Fecha no disponible'")
    else:
        print("❌ No se pudo obtener usuario para prueba")

def main():
    """Función principal"""
    print("🧪 TEST DE PERFIL - BELGRANO AHORRO")
    print("=" * 40)
    
    test_obtener_usuario()
    test_campos_usuario()
    
    print("\n✅ Test completado")

if __name__ == "__main__":
    main() 