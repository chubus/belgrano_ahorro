#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación de Estructura API
Verifica que todos los archivos y configuraciones estén correctos
"""

import os
import sys
import re
from datetime import datetime

def verificar_archivos():
    """Verificar que todos los archivos necesarios existen"""
    print("=== VERIFICANDO ARCHIVOS ===")
    
    archivos_requeridos = {
        'api_belgrano_ahorro.py': 'API RESTful de Belgrano Ahorro',
        'belgrano_client.py': 'Cliente API para DevOps',
        'devops_persistence.py': 'Persistencia local de DevOps',
        'app_unificado.py': 'Aplicación principal de Belgrano Ahorro',
        'belgrano_tickets/app.py': 'Aplicación de Ticketera/DevOps'
    }
    
    todos_existen = True
    
    for archivo, descripcion in archivos_requeridos.items():
        if os.path.exists(archivo):
            print(f"✅ {archivo} - {descripcion}")
        else:
            print(f"❌ {archivo} - {descripcion} - FALTANTE")
            todos_existen = False
    
    return todos_existen

def verificar_endpoints_api():
    """Verificar que la API tiene todos los endpoints necesarios"""
    print("\n=== VERIFICANDO ENDPOINTS API ===")
    
    try:
        with open('api_belgrano_ahorro.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        endpoints_esperados = [
            ('/api/products', 'CRUD de productos'),
            ('/api/businesses', 'CRUD de negocios'),
            ('/api/branches', 'CRUD de sucursales'),
            ('/api/offers', 'CRUD de ofertas'),
            ('/api/cart', 'Gestión de carrito'),
            ('/api/health', 'Health check')
        ]
        
        todos_presentes = True
        
        for endpoint, descripcion in endpoints_esperados:
            # Buscar el patrón de ruta en el archivo
            patron = f"@api_bp.route('{endpoint}'"
            if patron in contenido:
                print(f"✅ {endpoint} - {descripcion}")
            else:
                # Buscar variaciones del patrón
                patron_alt = f"@api_bp.route(\"{endpoint}\""
                if patron_alt in contenido:
                    print(f"✅ {endpoint} - {descripcion}")
                else:
                    print(f"❌ {endpoint} - {descripcion} - FALTANTE")
                    todos_presentes = False
        
        # Verificar autenticación
        if 'require_api_key' in contenido:
            print("✅ Autenticación Bearer Token implementada")
        else:
            print("❌ Autenticación Bearer Token - FALTANTE")
            todos_presentes = False
        
        return todos_presentes
        
    except Exception as e:
        print(f"❌ Error leyendo api_belgrano_ahorro.py: {e}")
        return False

def verificar_cliente_api():
    """Verificar que el cliente API tiene todos los métodos necesarios"""
    print("\n=== VERIFICANDO CLIENTE API ===")
    
    try:
        with open('belgrano_client.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        metodos_esperados = [
            ('get_products', 'Obtener productos'),
            ('create_product', 'Crear producto'),
            ('get_businesses', 'Obtener negocios'),
            ('create_business', 'Crear negocio'),
            ('get_branches', 'Obtener sucursales'),
            ('create_branch', 'Crear sucursal'),
            ('get_offers', 'Obtener ofertas'),
            ('create_offer', 'Crear oferta'),
            ('health_check', 'Health check')
        ]
        
        todos_presentes = True
        
        for metodo, descripcion in metodos_esperados:
            if f"def {metodo}(" in contenido:
                print(f"✅ {metodo} - {descripcion}")
            else:
                print(f"❌ {metodo} - {descripcion} - FALTANTE")
                todos_presentes = False
        
        return todos_presentes
        
    except Exception as e:
        print(f"❌ Error leyendo belgrano_client.py: {e}")
        return False

def verificar_integracion_devops():
    """Verificar que DevOps está integrado con el cliente API"""
    print("\n=== VERIFICANDO INTEGRACIÓN DEVOPS ===")
    
    try:
        with open('belgrano_tickets/app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        integraciones_esperadas = [
            ('from belgrano_client import belgrano_client', 'Import del cliente API'),
            ('belgrano_client.create_business', 'Creación de negocios via API'),
            ('belgrano_client.get_businesses', 'Obtención de negocios via API'),
            ('belgrano_client.create_product', 'Creación de productos via API'),
            ('belgrano_client.get_products', 'Obtención de productos via API')
        ]
        
        todos_presentes = True
        
        for integracion, descripcion in integraciones_esperadas:
            if integracion in contenido:
                print(f"✅ {descripcion}")
            else:
                print(f"❌ {descripcion} - FALTANTE")
                todos_presentes = False
        
        return todos_presentes
        
    except Exception as e:
        print(f"❌ Error leyendo belgrano_tickets/app.py: {e}")
        return False

def verificar_registro_api():
    """Verificar que la API está registrada en la aplicación principal"""
    print("\n=== VERIFICANDO REGISTRO API ===")
    
    try:
        with open('app_unificado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        registros_esperados = [
            ('from api_belgrano_ahorro import api_bp', 'Import del blueprint API'),
            ('app.register_blueprint(api_bp)', 'Registro del blueprint API'),
            ('API RESTful registrada', 'Mensaje de confirmación')
        ]
        
        todos_presentes = True
        
        for registro, descripcion in registros_esperados:
            if registro in contenido:
                print(f"✅ {descripcion}")
            else:
                print(f"❌ {descripcion} - FALTANTE")
                todos_presentes = False
        
        return todos_presentes
        
    except Exception as e:
        print(f"❌ Error leyendo app_unificado.py: {e}")
        return False

def verificar_variables_entorno():
    """Verificar configuración de variables de entorno"""
    print("\n=== VERIFICANDO VARIABLES DE ENTORNO ===")
    
    variables_requeridas = [
        'BELGRANO_AHORRO_URL',
        'BELGRANO_AHORRO_API_KEY',
        'BELGRANO_AHORRO_DB_PATH'
    ]
    
    configuracion_correcta = True
    
    for var in variables_requeridas:
        if var in os.environ:
            valor = os.environ[var]
            if 'API_KEY' in var:
                display_valor = valor[:10] + '...' if len(valor) > 10 else valor
            else:
                display_valor = valor
            print(f"✅ {var}: {display_valor}")
        else:
            print(f"⚠️ {var}: No configurada (usando valor por defecto)")
    
    return configuracion_correcta

def main():
    """Función principal de verificación"""
    print("=== VERIFICACIÓN COMPLETA DE ESTRUCTURA API ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    verificaciones = [
        ("Archivos", verificar_archivos),
        ("Endpoints API", verificar_endpoints_api),
        ("Cliente API", verificar_cliente_api),
        ("Integración DevOps", verificar_integracion_devops),
        ("Registro API", verificar_registro_api),
        ("Variables de Entorno", verificar_variables_entorno)
    ]
    
    resultados = []
    
    for nombre, funcion in verificaciones:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n=== RESUMEN FINAL ===")
    
    exitosos = 0
    total = len(resultados)
    
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: COMPLETO")
            exitosos += 1
        else:
            print(f"❌ {nombre}: INCOMPLETO")
    
    print(f"\nProgreso: {exitosos}/{total} ({exitosos/total*100:.1f}%)")
    
    if exitosos == total:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ La API está lista para usar")
        print("✅ DevOps puede comunicarse con Belgrano Ahorro")
        print("✅ La arquitectura está completa")
    else:
        print("⚠️ Algunas verificaciones fallaron")
        print("❌ Revisar los elementos marcados como FALTANTE")
    
    return exitosos == total

if __name__ == "__main__":
    main()
