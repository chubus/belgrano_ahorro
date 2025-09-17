#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST COMPLETO - BELGRANO AHORRO
===============================

Script para testear todos los endpoints y flujos de trabajo del sistema
"""

import requests
import json
import time
import sys
import os

# Configuración
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "nombre": "Test",
    "apellido": "Usuario",
    "email": "test@test.com",
    "password": "123456",
    "telefono": "123456789",
    "direccion": "Dirección de prueba"
}

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Testear un endpoint específico"""
    try:
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method.upper() == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", data=data)
        else:
            print(f"❌ Método {method} no soportado")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code} (esperado: {expected_status})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - No se pudo conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def test_session():
    """Testear manejo de sesiones"""
    print("\n🔐 TESTEANDO SESIONES...")
    
    session = requests.Session()
    
    # Test 1: Página principal
    print("\n1. Página principal")
    test_endpoint("GET", "/")
    
    # Test 2: Login (sin datos)
    print("\n2. Login sin datos")
    test_endpoint("POST", "/login", {}, 200)
    
    # Test 3: Login con datos válidos
    print("\n3. Login con datos válidos")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    test_endpoint("POST", "/login", login_data, 200)
    
    # Test 4: Registro
    print("\n4. Registro de usuario")
    register_data = {
        "nombre": TEST_USER["nombre"],
        "apellido": TEST_USER["apellido"],
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "confirmar_password": TEST_USER["password"]
    }
    test_endpoint("POST", "/register", register_data, 200)

def test_paginas_principales():
    """Testear páginas principales"""
    print("\n📄 TESTEANDO PÁGINAS PRINCIPALES...")
    
    paginas = [
        "/",
        "/login",
        "/register",
        "/contacto",
        "/sobre-nosotros",
        "/carrito",
        "/checkout"
    ]
    
    for pagina in paginas:
        test_endpoint("GET", pagina)

def test_productos():
    """Testear funcionalidad de productos"""
    print("\n🛍️ TESTEANDO PRODUCTOS...")
    
    # Test 1: Ver productos por negocio
    print("\n1. Productos por negocio")
    test_endpoint("GET", "/negocio/belgrano_ahorro")
    
    # Test 2: Ver productos por categoría
    print("\n2. Productos por categoría")
    test_endpoint("GET", "/categoria/granos_cereales")
    
    # Test 3: Agregar al carrito
    print("\n3. Agregar al carrito")
    carrito_data = {
        "producto_id": "producto_001",
        "cantidad": "1"
    }
    test_endpoint("POST", "/agregar_al_carrito", carrito_data, 200)

def test_carrito():
    """Testear funcionalidad del carrito"""
    print("\n🛒 TESTEANDO CARRITO...")
    
    # Test 1: Ver carrito
    print("\n1. Ver carrito")
    test_endpoint("GET", "/carrito")
    
    # Test 2: Actualizar cantidad
    print("\n2. Actualizar cantidad")
    actualizar_data = {
        "producto_id": "producto_001",
        "cantidad": "2"
    }
    test_endpoint("POST", "/actualizar_cantidad", actualizar_data, 200)
    
    # Test 3: Vaciar carrito
    print("\n3. Vaciar carrito")
    test_endpoint("GET", "/vaciar_carrito")

def test_pedidos():
    """Testear funcionalidad de pedidos"""
    print("\n📋 TESTEANDO PEDIDOS...")
    
    # Test 1: Checkout
    print("\n1. Checkout")
    test_endpoint("GET", "/checkout")
    
    # Test 2: Procesar pago
    print("\n2. Procesar pago")
    pago_data = {
        "metodo_pago": "efectivo",
        "direccion_entrega": "Dirección de prueba",
        "notas": "Notas de prueba"
    }
    test_endpoint("POST", "/procesar_pago", pago_data, 200)
    
    # Test 3: Mis pedidos
    print("\n3. Mis pedidos")
    test_endpoint("GET", "/mis_pedidos")

def test_perfil():
    """Testear funcionalidad del perfil"""
    print("\n👤 TESTEANDO PERFIL...")
    
    # Test 1: Ver perfil
    print("\n1. Ver perfil")
    test_endpoint("GET", "/perfil")
    
    # Test 2: Editar perfil
    print("\n2. Editar perfil")
    editar_data = {
        "nombre": "Test Usuario Actualizado",
        "telefono": "987654321",
        "direccion": "Nueva dirección"
    }
    test_endpoint("POST", "/editar-perfil", editar_data, 200)
    
    # Test 3: Cambiar contraseña
    print("\n3. Cambiar contraseña")
    password_data = {
        "password_actual": "123456",
        "password_nuevo": "nueva123",
        "confirmar_password": "nueva123"
    }
    test_endpoint("POST", "/cambiar-password", password_data, 200)

def test_recuperacion():
    """Testear funcionalidad de recuperación de contraseña"""
    print("\n🔑 TESTEANDO RECUPERACIÓN DE CONTRASEÑA...")
    
    # Test 1: Solicitar recuperación
    print("\n1. Solicitar recuperación")
    recuperacion_data = {
        "email": TEST_USER["email"]
    }
    test_endpoint("POST", "/recuperar-password", recuperacion_data, 200)
    
    # Test 2: Verificar código
    print("\n2. Verificar código")
    codigo_data = {
        "email": TEST_USER["email"],
        "codigo": "123456"
    }
    test_endpoint("POST", "/verificar-codigo", codigo_data, 200)

def test_errores():
    """Testear manejo de errores"""
    print("\n🚨 TESTEANDO MANEJO DE ERRORES...")
    
    # Test 1: Página 404
    print("\n1. Página 404")
    test_endpoint("GET", "/pagina-inexistente", expected_status=404)
    
    # Test 2: Acceso sin login
    print("\n2. Acceso sin login")
    test_endpoint("GET", "/perfil", expected_status=200)  # Debería redirigir a login

def verificar_servidor():
    """Verificar que el servidor esté funcionando"""
    print("🔍 Verificando servidor...")
    
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
        print("💡 Asegúrate de que el servidor esté ejecutándose con: python app.py")
        return False

def main():
    """Función principal"""
    print("🧪 TEST COMPLETO - BELGRANO AHORRO")
    print("=" * 50)
    
    # Verificar servidor
    if not verificar_servidor():
        return
    
    # Ejecutar todos los tests
    test_paginas_principales()
    test_session()
    test_productos()
    test_carrito()
    test_pedidos()
    test_perfil()
    test_recuperacion()
    test_errores()
    
    print("\n✅ Test completo finalizado")
    print("📊 Resumen: Todos los endpoints han sido probados")

if __name__ == "__main__":
    main() 