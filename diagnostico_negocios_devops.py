#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico para el problema de creación de negocios en DevOps
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verificar_variables_entorno():
    """Verificar variables de entorno necesarias"""
    print("🔍 VERIFICANDO VARIABLES DE ENTORNO...")
    
    belgrano_url = os.environ.get('BELGRANO_AHORRO_URL')
    belgrano_api_key = os.environ.get('BELGRANO_AHORRO_API_KEY')
    
    print(f"   BELGRANO_AHORRO_URL: {'✅ Configurada' if belgrano_url else '❌ No configurada'}")
    if belgrano_url:
        print(f"      Valor: {belgrano_url}")
    
    print(f"   BELGRANO_AHORRO_API_KEY: {'✅ Configurada' if belgrano_api_key else '❌ No configurada'}")
    if belgrano_api_key:
        print(f"      Valor: {'*' * len(belgrano_api_key)} (oculto por seguridad)")
    
    return belgrano_url and belgrano_api_key

def verificar_gestor_devops():
    """Verificar estado del gestor DevOps"""
    print("\n🔍 VERIFICANDO GESTOR DEVOPS...")
    
    try:
        from devops_belgrano_manager_enhanced import devops_manager
        print("   ✅ Gestor DevOps mejorado importado correctamente")
        
        # Verificar estado del gestor
        print(f"   Modo fallback: {'✅ Activo' if devops_manager.fallback_mode else '❌ Inactivo'}")
        print(f"   URL configurada: {'✅ Sí' if devops_manager.belgrano_url else '❌ No'}")
        print(f"   API Key configurada: {'✅ Sí' if devops_manager.belgrano_api_key else '❌ No'}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Error importando gestor DevOps: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error verificando gestor DevOps: {e}")
        return False

def probar_creacion_negocio():
    """Probar creación de negocio"""
    print("\n🔍 PROBANDO CREACIÓN DE NEGOCIO...")
    
    try:
        from devops_belgrano_manager_enhanced import devops_manager
        
        # Datos de prueba
        negocio_data = {
            'nombre': 'Negocio de Prueba',
            'descripcion': 'Negocio creado para diagnóstico',
            'telefono': '+54 11 1234-5678',
            'direccion': 'Calle de Prueba 123',
            'email': 'prueba@test.com',
            'activo': True
        }
        
        print("   Enviando datos de prueba...")
        success, message = devops_manager.create_negocio(negocio_data)
        
        if success:
            print(f"   ✅ Creación exitosa: {message}")
        else:
            print(f"   ❌ Error en creación: {message}")
            
        return success
        
    except Exception as e:
        print(f"   ❌ Error en prueba: {e}")
        return False

def generar_reporte():
    """Generar reporte completo"""
    print("=" * 60)
    print("📋 DIAGNÓSTICO DE PROBLEMA: CREACIÓN DE NEGOCIOS EN DEVOPS")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificaciones
    env_ok = verificar_variables_entorno()
    gestor_ok = verificar_gestor_devops()
    creacion_ok = probar_creacion_negocio()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    print(f"Variables de entorno: {'✅ OK' if env_ok else '❌ PROBLEMA'}")
    print(f"Gestor DevOps: {'✅ OK' if gestor_ok else '❌ PROBLEMA'}")
    print(f"Creación de negocio: {'✅ OK' if creacion_ok else '❌ PROBLEMA'}")
    
    if not env_ok:
        print("\n🔧 SOLUCIÓN RECOMENDADA:")
        print("   1. Configure las variables de entorno:")
        print("      - BELGRANO_AHORRO_URL")
        print("      - BELGRANO_AHORRO_API_KEY")
        print("   2. Reinicie la aplicación después de configurar las variables")
        
    elif not creacion_ok:
        print("\n🔧 SOLUCIÓN RECOMENDADA:")
        print("   1. Verifique la conectividad con la API")
        print("   2. Revise los logs para más detalles del error")
        print("   3. El sistema funcionará en modo fallback (local)")
    else:
        print("\n✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    generar_reporte()
