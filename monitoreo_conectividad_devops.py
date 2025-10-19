#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script de Monitoreo Continuo - DevOps Belgrano Ahorro
Ejecutar periódicamente para verificar conectividad
'''

import os
import sys
import time
from datetime import datetime
import subprocess

def run_connectivity_check():
    """Ejecutar chequeo de conectividad"""
    try:
        result = subprocess.run([sys.executable, 'chequeo_conectividad_devops_integral.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] ✅ Chequeo de conectividad exitoso")
            return True
        else:
            print(f"[{datetime.now()}] ❌ Chequeo de conectividad falló")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[{datetime.now()}] ⏰ Timeout en chequeo de conectividad")
        return False
    except Exception as e:
        print(f"[{datetime.now()}] 💥 Error ejecutando chequeo: {e}")
        return False

def main():
    """Función principal de monitoreo"""
    print(f"[{datetime.now()}] 🔍 Iniciando monitoreo de conectividad DevOps...")
    
    success = run_connectivity_check()
    
    if success:
        print(f"[{datetime.now()}] ✅ Monitoreo completado exitosamente")
    else:
        print(f"[{datetime.now()}] ❌ Monitoreo detectó problemas")
        # Aquí se pueden agregar alertas (email, Slack, etc.)
    
    return success

if __name__ == "__main__":
    main()
