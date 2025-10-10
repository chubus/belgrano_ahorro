#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la solución del problema de creación de negocios
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def probar_creacion_negocio_sin_config():
    """Probar creación de negocio sin configuración (modo fallback)"""
    print("🧪 PROBANDO CREACIÓN DE NEGOCIO SIN CONFIGURACIÓN...")
    
    try:
        from devops_belgrano_manager_enhanced import devops_manager
        
        # Datos de prueba
        negocio_data = {
            'nombre': 'Negocio de Prueba Sin Config',
            'descripcion': 'Negocio creado para probar modo fallback',
            'telefono': '+54 11 1234-5678',
            'direccion': 'Calle de Prueba 123',
            'email': 'prueba@test.com',
            'activo': True
        }
        
        print("   Enviando datos de prueba...")
        success, message = devops_manager.create_negocio(negocio_data)
        
        if success:
            print(f"   ✅ Creación exitosa: {message}")
            return True
        else:
            print(f"   ❌ Error en creación: {message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en prueba: {e}")
        return False

def probar_creacion_negocio_con_config():
    """Probar creación de negocio con configuración simulada"""
    print("\n🧪 PROBANDO CREACIÓN DE NEGOCIO CON CONFIGURACIÓN...")
    
    # Configurar variables de entorno temporalmente
    os.environ['BELGRANO_AHORRO_URL'] = 'http://localhost:5000'
    os.environ['BELGRANO_AHORRO_API_KEY'] = 'test_key_123'
    
    try:
        # Reimportar el gestor para que tome las nuevas variables
        import importlib
        import devops_belgrano_manager_enhanced
        importlib.reload(devops_belgrano_manager_enhanced)
        
        devops_manager = devops_belgrano_manager_enhanced.devops_manager
        
        # Datos de prueba
        negocio_data = {
            'nombre': 'Negocio de Prueba Con Config',
            'descripcion': 'Negocio creado para probar con configuración',
            'telefono': '+54 11 9876-5432',
            'direccion': 'Calle Configurada 456',
            'email': 'config@test.com',
            'activo': True
        }
        
        print("   Enviando datos de prueba...")
        success, message = devops_manager.create_negocio(negocio_data)
        
        if success:
            print(f"   ✅ Creación exitosa: {message}")
            return True
        else:
            print(f"   ❌ Error en creación: {message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en prueba: {e}")
        return False
    finally:
        # Limpiar variables de entorno
        if 'BELGRANO_AHORRO_URL' in os.environ:
            del os.environ['BELGRANO_AHORRO_URL']
        if 'BELGRANO_AHORRO_API_KEY' in os.environ:
            del os.environ['BELGRANO_AHORRO_API_KEY']

def probar_mensajes_error():
    """Probar que los mensajes de error son más informativos"""
    print("\n🧪 PROBANDO MENSAJES DE ERROR MEJORADOS...")
    
    try:
        from devops_belgrano_manager_enhanced import devops_manager
        
        # Verificar que el gestor está en modo fallback
        if devops_manager.fallback_mode:
            print("   ✅ Gestor en modo fallback (esperado sin configuración)")
        else:
            print("   ⚠️ Gestor no en modo fallback (inesperado)")
        
        # Probar creación
        negocio_data = {
            'nombre': 'Test Error Messages',
            'descripcion': 'Test',
            'activo': True
        }
        
        success, message = devops_manager.create_negocio(negocio_data)
        
        if success and "modo fallback" in message:
            print("   ✅ Mensaje de error informativo: Modo fallback detectado")
            return True
        else:
            print(f"   ⚠️ Mensaje inesperado: {message}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en prueba: {e}")
        return False

def generar_reporte_pruebas():
    """Generar reporte de las pruebas"""
    print("=" * 60)
    print("🧪 REPORTE DE PRUEBAS: SOLUCIÓN CREACIÓN DE NEGOCIOS")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar pruebas
    test1 = probar_creacion_negocio_sin_config()
    test2 = probar_creacion_negocio_con_config()
    test3 = probar_mensajes_error()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE LAS PRUEBAS")
    print("=" * 60)
    
    print(f"Creación sin configuración: {'✅ OK' if test1 else '❌ FALLO'}")
    print(f"Creación con configuración: {'✅ OK' if test2 else '❌ FALLO'}")
    print(f"Mensajes de error mejorados: {'✅ OK' if test3 else '❌ FALLO'}")
    
    if test1 and test2 and test3:
        print("\n✅ TODAS LAS PRUEBAS PASARON - SOLUCIÓN FUNCIONANDO")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON - REVISAR IMPLEMENTACIÓN")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    generar_reporte_pruebas()
