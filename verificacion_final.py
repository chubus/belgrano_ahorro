#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICACIÓN FINAL - BELGRANO AHORRO
====================================

Script de verificación final para confirmar que todo funciona correctamente
"""

import requests
import json
import db as database

BASE_URL = "http://localhost:5000"

def verificar_base_datos():
    """Verificar que la base de datos funcione correctamente"""
    print("🗄️ Verificando base de datos...")
    
    try:
        # Verificar usuario
        usuario = database.obtener_usuario_por_id(1)
        if usuario and usuario.get('fecha_registro'):
            print("✅ Base de datos funcionando correctamente")
            print(f"   Usuario: {usuario.get('nombre')}")
            print(f"   Fecha registro: {usuario.get('fecha_registro')}")
            return True
        else:
            print("❌ Problema con la base de datos")
            return False
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def verificar_servidor():
    """Verificar que el servidor esté funcionando"""
    print("\n🌐 Verificando servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Servidor respondió con status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        return False

def verificar_perfil():
    """Verificar que el perfil funcione correctamente"""
    print("\n👤 Verificando perfil...")
    
    try:
        # Login
        session = requests.Session()
        login_data = {
            "email": "test@test.com",
            "password": "123456"
        }
        response = session.post(f"{BASE_URL}/login", data=login_data)
        
        if response.status_code == 200:
            # Acceder al perfil
            response = session.get(f"{BASE_URL}/perfil")
            
            if response.status_code == 200:
                if "Mi Perfil" in response.text and "fecha_registro" not in response.text.lower():
                    print("✅ Perfil funcionando correctamente")
                    return True
                else:
                    print("❌ Error en el contenido del perfil")
                    return False
            else:
                print(f"❌ Error accediendo al perfil: {response.status_code}")
                return False
        else:
            print("❌ Error en login")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando perfil: {e}")
        return False

def verificar_endpoints_principales():
    """Verificar endpoints principales"""
    print("\n🔗 Verificando endpoints principales...")
    
    endpoints = [
        "/",
        "/login",
        "/register",
        "/carrito",
        "/checkout",
        "/negocio/belgrano_ahorro",
        "/categoria/granos_cereales"
    ]
    
    errores = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                errores += 1
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            errores += 1
    
    if errores == 0:
        print("✅ Todos los endpoints principales funcionando")
        return True
    else:
        print(f"❌ {errores} endpoints con problemas")
        return False

def verificar_funcionalidades():
    """Verificar funcionalidades específicas"""
    print("\n⚙️ Verificando funcionalidades...")
    
    try:
        session = requests.Session()
        
        # Login
        login_data = {
            "email": "test@test.com",
            "password": "123456"
        }
        session.post(f"{BASE_URL}/login", data=login_data)
        
        # Verificar carrito
        response = session.get(f"{BASE_URL}/carrito")
        if response.status_code == 200:
            print("✅ Carrito accesible")
        else:
            print("❌ Problema con carrito")
        
        # Verificar checkout
        response = session.get(f"{BASE_URL}/checkout")
        if response.status_code == 200:
            print("✅ Checkout accesible")
        else:
            print("❌ Problema con checkout")
        
        # Verificar mis pedidos
        response = session.get(f"{BASE_URL}/mis_pedidos")
        if response.status_code == 200:
            print("✅ Mis pedidos accesible")
        else:
            print("❌ Problema con mis pedidos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando funcionalidades: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN FINAL - BELGRANO AHORRO")
    print("=" * 50)
    
    resultados = []
    
    # Ejecutar verificaciones
    resultados.append(("Base de datos", verificar_base_datos()))
    resultados.append(("Servidor", verificar_servidor()))
    resultados.append(("Perfil", verificar_perfil()))
    resultados.append(("Endpoints principales", verificar_endpoints_principales()))
    resultados.append(("Funcionalidades", verificar_funcionalidades()))
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 30)
    
    exitos = 0
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}")
            exitos += 1
        else:
            print(f"❌ {nombre}")
    
    print(f"\n🎯 Resultado: {exitos}/{len(resultados)} verificaciones exitosas")
    
    if exitos == len(resultados):
        print("🎉 ¡TODAS LAS VERIFICACIONES EXITOSAS!")
        print("✅ El sistema está funcionando correctamente")
    else:
        print("⚠️ Algunas verificaciones fallaron")
        print("🔧 Revisa los errores indicados arriba")

if __name__ == "__main__":
    main() 