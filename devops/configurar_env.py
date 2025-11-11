#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de ayuda para configurar variables de entorno de DevOps
Ejecutar: python devops/configurar_env.py
"""

import os
import sys

def main():
    print("=" * 60)
    print("🔧 Configurador de Variables de Entorno - DevOps")
    print("=" * 60)
    print()
    
    # Verificar si ya existe un archivo .env
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(current_dir, '.env')
    env_example = os.path.join(current_dir, 'env', 'env.example')
    
    if os.path.exists(env_file):
        print(f"⚠️  Ya existe un archivo .env en: {env_file}")
        respuesta = input("¿Desea sobrescribirlo? (s/N): ").strip().lower()
        if respuesta != 's':
            print("❌ Operación cancelada.")
            return
    else:
        print(f"📝 Creando nuevo archivo .env en: {env_file}")
    
    print()
    print("Por favor, ingrese los siguientes valores:")
    print("(Presione Enter para usar valores por defecto)")
    print()
    
    # Obtener valores
    belgrano_url = input("BELGRANO_AHORRO_URL [https://belgranoahorro-aliq.onrender.com]: ").strip()
    if not belgrano_url:
        belgrano_url = "https://belgranoahorro-aliq.onrender.com"
    
    belgrano_api_key = input("BELGRANO_AHORRO_API_KEY [OBLIGATORIO]: ").strip()
    if not belgrano_api_key:
        print("⚠️  ADVERTENCIA: BELGRANO_AHORRO_API_KEY es obligatorio para que funcione el dashboard")
        respuesta = input("¿Desea continuar sin API Key? (s/N): ").strip().lower()
        if respuesta != 's':
            print("❌ Operación cancelada. Configure la API Key e intente nuevamente.")
            return
    
    ticketera_url = input("TICKETERA_URL [https://ticketerabelgrano.onrender.com]: ").strip()
    if not ticketera_url:
        ticketera_url = "https://ticketerabelgrano.onrender.com"
    
    devops_username = input("DEVOPS_USERNAME [devops]: ").strip()
    if not devops_username:
        devops_username = "devops"
    
    devops_password = input("DEVOPS_PASSWORD [OBLIGATORIO para producción]: ").strip()
    if not devops_password:
        devops_password = "devops_password"
        print("⚠️  Usando contraseña por defecto. Cambie en producción.")
    
    # Escribir archivo .env
    env_content = f"""# ============================================================
# Variables de Entorno para DevOps
# Generado automáticamente por configurar_env.py
# ============================================================

# ============================================================
# BELGRANO AHORRO API (OBLIGATORIO)
# ============================================================
BELGRANO_AHORRO_URL={belgrano_url}
BELGRANO_AHORRO_API_KEY={belgrano_api_key}

# ============================================================
# CONFIGURACIÓN DE API (OPCIONAL)
# ============================================================
API_TIMEOUT_SECS=15
API_RETRY_TOTAL=3
API_RETRY_BACKOFF=0.5

# ============================================================
# TICKETERA / DEVOPS API (OPCIONAL)
# ============================================================
TICKETERA_URL={ticketera_url}
TICKETS_API_URL={ticketera_url}

# ============================================================
# SEGURIDAD DEVOPS
# ============================================================
DEVOPS_USERNAME={devops_username}
DEVOPS_PASSWORD={devops_password}

# ============================================================
# FLASK
# ============================================================
FLASK_ENV=production
SECRET_KEY=devops_secret_key_2025_prod_segura_cambiar_en_produccion
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print()
        print("✅ Archivo .env creado exitosamente!")
        print(f"   Ubicación: {env_file}")
        print()
        print("📋 Próximos pasos:")
        print("   1. Verifique que la API Key sea correcta")
        print("   2. En producción, cambie SECRET_KEY y DEVOPS_PASSWORD")
        print("   3. Reinicie la aplicación para que los cambios surtan efecto")
        print()
        
        if not belgrano_api_key:
            print("⚠️  IMPORTANTE: Configure BELGRANO_AHORRO_API_KEY en el archivo .env")
            print("   o como variable de entorno del sistema para que funcione el dashboard.")
        
    except Exception as e:
        print(f"❌ Error al crear archivo .env: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

