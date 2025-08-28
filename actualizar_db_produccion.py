#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la base de datos de Belgrano Ahorro en producción
"""

import requests
import json
from datetime import datetime

# Configuración
BELGRANO_AHORRO_URL = "https://belgranoahorro-hp30.onrender.com"
API_KEY = "belgrano_ahorro_api_key_2025"

def actualizar_db_produccion():
    """Actualizar la base de datos en producción"""
    print("🔧 Actualizando base de datos en producción...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    try:
        response = requests.post(
            f"{BELGRANO_AHORRO_URL}/api/actualizar-db",
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Base de datos actualizada exitosamente")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = actualizar_db_produccion()
    if success:
        print("🎉 ¡Actualización completada!")
    else:
        print("💥 Error en la actualización")
