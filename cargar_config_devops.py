#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para cargar configuración DevOps
"""

import os
from dotenv import load_dotenv

def cargar_config_devops():
    """Cargar configuración DevOps desde archivo .env"""
    try:
        # Cargar desde archivo de configuración
        if os.path.exists('config_devops.env'):
            load_dotenv('config_devops.env')
            print("✅ Configuración DevOps cargada desde config_devops.env")
        else:
            print("⚠️ Archivo config_devops.env no encontrado, usando valores por defecto")
        
        # Verificar variables críticas
        variables_criticas = [
            'DEVOPS_USERNAME',
            'DEVOPS_PASSWORD',
            'BELGRANO_AHORRO_URL',
            'BELGRANO_AHORRO_API_KEY'
        ]
        
        configuradas = 0
        for var in variables_criticas:
            if os.environ.get(var):
                configuradas += 1
                print(f"✅ {var} = {os.environ.get(var)[:10]}...")
            else:
                print(f"❌ {var} - NO CONFIGURADA")
        
        print(f"\nVariables configuradas: {configuradas}/{len(variables_criticas)}")
        return configuradas == len(variables_criticas)
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False

if __name__ == "__main__":
    cargar_config_devops()
<<<<<<< HEAD

=======
>>>>>>> 4f153f9df9e6f05c23230eeb299bb9ad39dc2deb
