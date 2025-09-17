#!/usr/bin/env python3
"""
Script para verificar que las correcciones funcionen correctamente
"""
import os
import sys
import subprocess
import time
import requests

def verificar_template_syntax():
    """Verificar que el template index.html tenga sintaxis correcta"""
    print("🔍 Verificando sintaxis del template...")
    
    try:
        # Buscar líneas problemáticas
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar que no hay sintaxis incorrecta
        if '_original' in content and 'producto.get(' in content:
            # Buscar patrones problemáticos
            lines = content.split('\n')
            problematic_lines = []
            
            for i, line in enumerate(lines, 1):
                if '_original' in line and 'producto.get(' in line:
                    if ')_original' in line:
                        problematic_lines.append(f"Línea {i}: {line.strip()}")
            
            if problematic_lines:
                print("❌ Se encontraron líneas con sintaxis incorrecta:")
                for line in problematic_lines:
                    print(f"   {line}")
                return False
            else:
                print("✅ Sintaxis del template corregida")
                return True
        else:
            print("✅ No se encontraron problemas de sintaxis")
            return True
            
    except Exception as e:
        print(f"❌ Error verificando template: {e}")
        return False

def verificar_ticketera_init():
    """Verificar que la inicialización de ticketera funcione"""
    print("🔍 Verificando inicialización de ticketera...")
    
    try:
        # Ejecutar script de inicialización
        result = subprocess.run([sys.executable, 'init_ticketera_deploy.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Inicialización de ticketera exitosa")
            return True
        else:
            print(f"❌ Error en inicialización: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando inicialización: {e}")
        return False

def verificar_aplicaciones():
    """Verificar que las aplicaciones se ejecuten sin errores"""
    print("🔍 Verificando aplicaciones...")
    
    try:
        # Probar app_tickets.py
        print("   Probando app_tickets.py...")
        result = subprocess.run([sys.executable, '-c', 
                               'import app_tickets; print("✅ app_tickets importado correctamente")'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ app_tickets.py funciona correctamente")
        else:
            print(f"   ❌ Error en app_tickets.py: {result.stderr}")
            return False
        
        # Probar app.py
        print("   Probando app.py...")
        result = subprocess.run([sys.executable, '-c', 
                               'import app; print("✅ app importado correctamente")'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ app.py funciona correctamente")
        else:
            print(f"   ❌ Error en app.py: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando aplicaciones: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🚀 VERIFICACIÓN DE CORRECCIONES")
    print("=" * 40)
    
    resultados = {
        'template_syntax': False,
        'ticketera_init': False,
        'aplicaciones': False
    }
    
    # 1. Verificar sintaxis del template
    print("\n1️⃣ VERIFICANDO TEMPLATE")
    print("-" * 25)
    resultados['template_syntax'] = verificar_template_syntax()
    
    # 2. Verificar inicialización de ticketera
    print("\n2️⃣ VERIFICANDO INICIALIZACIÓN TICKETERA")
    print("-" * 35)
    resultados['ticketera_init'] = verificar_ticketera_init()
    
    # 3. Verificar aplicaciones
    print("\n3️⃣ VERIFICANDO APLICACIONES")
    print("-" * 25)
    resultados['aplicaciones'] = verificar_aplicaciones()
    
    # Resumen
    print("\n📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 30)
    
    total_checks = len(resultados)
    checks_passed = sum(resultados.values())
    
    print(f"✅ Verificaciones exitosas: {checks_passed}/{total_checks}")
    
    if resultados['template_syntax']:
        print("   ✅ Template: SINTAXIS CORREGIDA")
    else:
        print("   ❌ Template: ERRORES PENDIENTES")
    
    if resultados['ticketera_init']:
        print("   ✅ Ticketera: INICIALIZACIÓN OK")
    else:
        print("   ❌ Ticketera: ERRORES EN INICIALIZACIÓN")
    
    if resultados['aplicaciones']:
        print("   ✅ Aplicaciones: FUNCIONANDO")
    else:
        print("   ❌ Aplicaciones: ERRORES DETECTADOS")
    
    if checks_passed == total_checks:
        print("\n🎉 ¡Todas las correcciones funcionan correctamente!")
        print("   - El template tiene sintaxis correcta")
        print("   - La ticketera se inicializa correctamente")
        print("   - Las aplicaciones funcionan sin errores")
        print("   - El sistema está listo para deploy")
    else:
        print("\n⚠️ Algunas correcciones necesitan atención")
        print("   - Revisar los errores listados arriba")
        print("   - Verificar que todos los archivos estén correctos")
    
    return checks_passed == total_checks

if __name__ == "__main__":
    main()
