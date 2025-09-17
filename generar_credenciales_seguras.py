#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar credenciales seguras para Render
"""

import secrets
import string
import hashlib
import base64

def generar_secret_key():
    """Generar una SECRET_KEY segura"""
    return secrets.token_urlsafe(32)

def generar_api_key():
    """Generar una API key segura"""
    return f"belgrano_ahorro_{secrets.token_urlsafe(24)}"

def generar_password_seguro():
    """Generar una contraseña segura"""
    # Combinar letras, números y símbolos
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(caracteres) for _ in range(16))

def generar_credenciales():
    """Generar todas las credenciales seguras"""
    print("🔐 Generando credenciales seguras para Render...")
    print("=" * 60)
    
    # Generar credenciales
    secret_key = generar_secret_key()
    api_key = generar_api_key()
    admin_password = generar_password_seguro()
    
    print("📋 NUEVAS VARIABLES DE ENTORNO PARA RENDER:")
    print("=" * 60)
    
    # Variables de entorno actualizadas
    variables = {
        "ADMIN_EMAIL": "admin@belgranoahorro.com",
        "ADMIN_PASSWORD": admin_password,
        "ADMIN_RESET": "0",  # Desactivar reset
        "BELGRANO_AHORRO_API_KEY": api_key,
        "BELGRANO_AHORRO_URL": "https://belgranoahorro-hp30.onrender.com",  # URL real
        "FLASK_ENV": "production",
        "PORT": "10000",
        "PYTHONPATH": "-",
        "REMEMBER_COOKIE_SECURE": "True",
        "SECRET_KEY": secret_key,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": "True"
    }
    
    for key, value in variables.items():
        print(f"{key}={value}")
    
    print("\n" + "=" * 60)
    print("🔑 CREDENCIALES DE ACCESO:")
    print("=" * 60)
    print(f"👑 Admin Email: admin@belgranoahorro.com")
    print(f"🔐 Admin Password: {admin_password}")
    print(f"🔑 API Key: {api_key}")
    print(f"🔒 Secret Key: {secret_key[:20]}...")
    
    print("\n" + "=" * 60)
    print("⚠️  INSTRUCCIONES IMPORTANTES:")
    print("=" * 60)
    print("1. Copia TODAS las variables de entorno mostradas arriba")
    print("2. Ve a tu proyecto en Render.com")
    print("3. Ve a Settings > Environment Variables")
    print("4. Actualiza cada variable con los nuevos valores")
    print("5. Guarda los cambios y redepleya la aplicación")
    print("6. Guarda estas credenciales en un lugar seguro")
    
    # Guardar en archivo para referencia
    with open('credenciales_render.txt', 'w') as f:
        f.write("CREDENCIALES SEGURAS PARA RENDER\n")
        f.write("=" * 40 + "\n\n")
        f.write("VARIABLES DE ENTORNO:\n")
        f.write("-" * 20 + "\n")
        for key, value in variables.items():
            f.write(f"{key}={value}\n")
        f.write(f"\nCREDENCIALES DE ACCESO:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Admin Email: admin@belgranoahorro.com\n")
        f.write(f"Admin Password: {admin_password}\n")
        f.write(f"API Key: {api_key}\n")
        f.write(f"Secret Key: {secret_key}\n")
    
    print(f"\n💾 Credenciales guardadas en: credenciales_render.txt")
    
    return variables

if __name__ == "__main__":
    generar_credenciales()
