#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación Final para Deploy
Verifica que todos los archivos estén listos para producción
"""

import os
import sys
import subprocess
from datetime import datetime

def verificar_sintaxis():
    """Verificar que todos los archivos Python tengan sintaxis correcta"""
    print("=== VERIFICANDO SINTAXIS ===")
    
    archivos_python = [
        'app_unificado.py',
        'api_belgrano_ahorro.py', 
        'belgrano_client.py',
        'devops_persistence.py',
        'belgrano_tickets/app.py'
    ]
    
    todos_correctos = True
    
    for archivo in archivos_python:
        if os.path.exists(archivo):
            try:
                result = subprocess.run([sys.executable, '-m', 'py_compile', archivo], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {archivo} - Sintaxis correcta")
                else:
                    print(f"❌ {archivo} - Error de sintaxis: {result.stderr}")
                    todos_correctos = False
            except Exception as e:
                print(f"❌ {archivo} - Error verificando: {e}")
                todos_correctos = False
        else:
            print(f"⚠️ {archivo} - Archivo no encontrado")
            todos_correctos = False
    
    return todos_correctos

def verificar_archivos_requeridos():
    """Verificar que todos los archivos requeridos existen"""
    print("\n=== VERIFICANDO ARCHIVOS REQUERIDOS ===")
    
    archivos_requeridos = [
        'app_unificado.py',
        'api_belgrano_ahorro.py',
        'belgrano_client.py', 
        'devops_persistence.py',
        'belgrano_tickets/app.py',
        'belgrano_tickets/templates/devops/negocios.html',
        'belgrano_tickets/templates/devops/productos.html',
        'belgrano_tickets/templates/devops/ofertas.html',
        'belgrano_tickets/templates/devops/precios.html'
    ]
    
    todos_existen = True
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
            todos_existen = False
    
    return todos_existen

def verificar_imports():
    """Verificar que los imports críticos funcionan"""
    print("\n=== VERIFICANDO IMPORTS ===")
    
    try:
        # Verificar que se pueden importar los módulos principales
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Verificar API
        try:
            from api_belgrano_ahorro import api_bp
            print("✅ api_belgrano_ahorro - Import exitoso")
        except Exception as e:
            print(f"❌ api_belgrano_ahorro - Error: {e}")
            return False
        
        # Verificar cliente
        try:
            from belgrano_client import belgrano_client
            print("✅ belgrano_client - Import exitoso")
        except Exception as e:
            print(f"❌ belgrano_client - Error: {e}")
            return False
        
        # Verificar persistencia
        try:
            from devops_persistence import get_devops_db
            print("✅ devops_persistence - Import exitoso")
        except Exception as e:
            print(f"❌ devops_persistence - Error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error general en imports: {e}")
        return False

def verificar_configuracion():
    """Verificar configuración de variables de entorno"""
    print("\n=== VERIFICANDO CONFIGURACIÓN ===")
    
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

def verificar_estructura_deploy():
    """Verificar estructura para deploy"""
    print("\n=== VERIFICANDO ESTRUCTURA DEPLOY ===")
    
    # Verificar que app_unificado.py tiene el registro de API
    try:
        with open('app_unificado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'app.register_blueprint(api_bp)' in contenido:
            print("✅ API registrada en app_unificado.py")
        else:
            print("❌ API no registrada en app_unificado.py")
            return False
        
        if 'from api_belgrano_ahorro import api_bp' in contenido:
            print("✅ Import de API en app_unificado.py")
        else:
            print("❌ Import de API faltante en app_unificado.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("=== VERIFICACIÓN FINAL PARA DEPLOY ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    verificaciones = [
        ("Sintaxis", verificar_sintaxis),
        ("Archivos Requeridos", verificar_archivos_requeridos),
        ("Imports", verificar_imports),
        ("Configuración", verificar_configuracion),
        ("Estructura Deploy", verificar_estructura_deploy)
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
    print("\n" + "="*60)
    print("=== RESUMEN FINAL ===")
    
    exitosos = 0
    total = len(resultados)
    
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: LISTO")
            exitosos += 1
        else:
            print(f"❌ {nombre}: FALLA")
    
    print(f"\nProgreso: {exitosos}/{total} ({exitosos/total*100:.1f}%)")
    
    if exitosos == total:
        print("\n🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ El sistema está listo para deploy")
        print("✅ La comunicación API está implementada")
        print("✅ Todos los archivos tienen sintaxis correcta")
        print("✅ La estructura está completa")
        print("\n🚀 LISTO PARA DEPLOY EN PRODUCCIÓN")
        return True
    else:
        print("\n⚠️ Algunas verificaciones fallaron")
        print("❌ Revisar los elementos marcados como FALLA")
        print("❌ No proceder con deploy hasta corregir errores")
        return False

if __name__ == "__main__":
    main()

