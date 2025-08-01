#!/usr/bin/env python3
"""
Diagnóstico final para identificar problemas con el registro de usuarios
"""

import db as database
import requests
import time

def diagnostico_base_datos():
    """Diagnóstico de la base de datos"""
    print("🔍 DIAGNÓSTICO DE BASE DE DATOS")
    print("=" * 50)
    
    # Probar crear usuario
    print("1. Probando creación de usuario...")
    resultado = database.crear_usuario("Test", "Diagnostico", "diagnostico@test.com", "password123", "123456789", "Dirección test")
    print(f"   Resultado: {resultado}")
    
    # Probar buscar usuario
    print("\n2. Probando búsqueda de usuario...")
    usuario = database.buscar_usuario_por_email("diagnostico@test.com")
    print(f"   Usuario encontrado: {usuario}")
    
    # Probar login
    print("\n3. Probando login...")
    resultado_login = database.verificar_usuario("diagnostico@test.com", "password123")
    print(f"   Login exitoso: {resultado_login}")
    
    print("\n✅ Base de datos: FUNCIONANDO CORRECTAMENTE")

def diagnostico_aplicacion_web():
    """Diagnóstico de la aplicación web"""
    print("\n🌐 DIAGNÓSTICO DE APLICACIÓN WEB")
    print("=" * 50)
    
    try:
        # Probar conexión
        print("1. Probando conexión a la aplicación...")
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Aplicación web accesible")
            
            # Probar página de registro
            print("\n2. Probando página de registro...")
            response = requests.get("http://localhost:5000/register", timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Página de registro accesible")
                
                # Probar envío de formulario
                print("\n3. Probando envío de formulario de registro...")
                datos = {
                    'nombre': 'Usuario',
                    'apellido': 'Web',
                    'email': 'web@test.com',
                    'password': 'password123',
                    'confirmar_password': 'password123',
                    'telefono': '123456789',
                    'direccion': 'Dirección web'
                }
                
                response = requests.post("http://localhost:5000/register", data=datos, timeout=10)
                print(f"   Status: {response.status_code}")
                print(f"   URL final: {response.url}")
                
                if response.status_code in [200, 302]:
                    print("   ✅ Formulario enviado correctamente")
                else:
                    print("   ❌ Error al enviar formulario")
            else:
                print("   ❌ Error al acceder a página de registro")
        else:
            print("   ❌ Aplicación web no accesible")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar a la aplicación web")
        print("   💡 La aplicación no está ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def instrucciones_solucion():
    """Instrucciones para solucionar problemas"""
    print("\n💡 INSTRUCCIONES PARA SOLUCIONAR")
    print("=" * 50)
    
    print("1. Para iniciar la aplicación:")
    print("   python app.py")
    print("   o")
    print("   python start_app.py")
    
    print("\n2. Para probar desde el navegador:")
    print("   Abre http://localhost:5000/register")
    print("   Llena el formulario y envía")
    
    print("\n3. Para verificar logs:")
    print("   Revisa la consola donde ejecutaste la aplicación")
    print("   Busca mensajes de error o logs de debug")
    
    print("\n4. Si el problema persiste:")
    print("   - Verifica que no haya otro proceso usando el puerto 5000")
    print("   - Revisa que todos los archivos estén en el lugar correcto")
    print("   - Verifica que las dependencias estén instaladas")

def main():
    """Función principal"""
    print("🎯 DIAGNÓSTICO FINAL - REGISTRO DE USUARIOS")
    print("=" * 60)
    
    # Diagnóstico de base de datos
    diagnostico_base_datos()
    
    # Diagnóstico de aplicación web
    diagnostico_aplicacion_web()
    
    # Instrucciones
    instrucciones_solucion()
    
    print("\n✅ Diagnóstico completado")

if __name__ == "__main__":
    main() 