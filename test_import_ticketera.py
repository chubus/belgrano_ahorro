#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que la importación del gestor DevOps funciona desde Ticketera
"""

import os
import sys
import traceback
from datetime import datetime

def test_import_desde_ticketera():
    """Probar importación desde el directorio belgrano_tickets"""
    print("🔍 PROBANDO IMPORTACIÓN DESDE TICKETERA...")
    
    try:
        # Simular el entorno de Ticketera
        original_cwd = os.getcwd()
        ticketera_dir = os.path.join(original_cwd, 'belgrano_tickets')
        
        if not os.path.exists(ticketera_dir):
            print(f"   ❌ ERROR: Directorio belgrano_tickets no encontrado")
            return False
        
        # Cambiar al directorio de Ticketera
        os.chdir(ticketera_dir)
        print(f"   📁 Cambiado a directorio: {ticketera_dir}")
        
        # Ajustar sys.path como lo hace el código
        project_root = os.path.dirname(os.path.abspath('.'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            print(f"   📁 Agregado al sys.path: {project_root}")
        
        # Intentar importar el gestor
        try:
            from devops_belgrano_manager_unified import devops_manager_unified as devops_manager
            print("   ✅ Importación exitosa: devops_belgrano_manager_unified")
            
            # Verificar que el gestor funciona
            if devops_manager:
                print(f"   ✅ Gestor inicializado: {type(devops_manager).__name__}")
                print(f"   ✅ Fallback mode: {getattr(devops_manager, 'fallback_mode', 'N/A')}")
                return True
            else:
                print("   ❌ ERROR: Gestor es None")
                return False
                
        except ImportError as e:
            print(f"   ❌ ERROR: No se pudo importar devops_belgrano_manager_unified: {e}")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: Error inesperado: {e}")
            print(f"   📋 Traceback: {traceback.format_exc()}")
            return False
        
    except Exception as e:
        print(f"   ❌ ERROR: Error en test: {e}")
        return False
    finally:
        # Restaurar directorio original
        os.chdir(original_cwd)

def test_import_desde_raiz():
    """Probar importación desde la raíz del proyecto"""
    print("\n🔍 PROBANDO IMPORTACIÓN DESDE RAÍZ...")
    
    try:
        # Asegurar que estamos en la raíz
        if not os.path.exists('devops_belgrano_manager_unified.py'):
            print("   ❌ ERROR: devops_belgrano_manager_unified.py no encontrado en raíz")
            return False
        
        # Intentar importar directamente
        from devops_belgrano_manager_unified import devops_manager_unified as devops_manager
        print("   ✅ Importación exitosa desde raíz")
        
        # Verificar que funciona
        if devops_manager:
            print(f"   ✅ Gestor inicializado: {type(devops_manager).__name__}")
            return True
        else:
            print("   ❌ ERROR: Gestor es None")
            return False
            
    except ImportError as e:
        print(f"   ❌ ERROR: No se pudo importar desde raíz: {e}")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: Error inesperado: {e}")
        return False

def test_estructura_archivos():
    """Verificar estructura de archivos necesarios"""
    print("\n🔍 VERIFICANDO ESTRUCTURA DE ARCHIVOS...")
    
    archivos_requeridos = [
        'devops_belgrano_manager_unified.py',
        'belgrano_tickets/devops_routes.py',
        'belgrano_tickets/app.py'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
        else:
            print(f"   ✅ {archivo} existe")
    
    if archivos_faltantes:
        print(f"   ❌ ERROR: Archivos faltantes: {archivos_faltantes}")
        return False
    else:
        print(f"   ✅ Todos los archivos requeridos existen")
        return True

def test_sys_path_ajuste():
    """Probar ajuste de sys.path como en el código real"""
    print("\n🔍 PROBANDO AJUSTE DE SYS.PATH...")
    
    try:
        import sys
        import os
        
        # Simular el código de belgrano_tickets/devops_routes.py
        project_root = os.path.dirname(os.path.abspath('.'))
        print(f"   📁 Project root calculado: {project_root}")
        
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            print(f"   ✅ Project root agregado a sys.path")
        else:
            print(f"   ✅ Project root ya estaba en sys.path")
        
        # Verificar que el módulo es importable
        try:
            from devops_belgrano_manager_unified import devops_manager_unified
            print("   ✅ Módulo importable después del ajuste de sys.path")
            return True
        except ImportError as e:
            print(f"   ❌ ERROR: Módulo no importable: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: Error en ajuste de sys.path: {e}")
        return False

def main():
    """Función principal del test"""
    print("=" * 80)
    print("🧪 TEST: IMPORTACIÓN GESTOR DEVOPS EN TICKETERA")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Estructura de archivos", test_estructura_archivos),
        ("Importación desde raíz", test_import_desde_raiz),
        ("Ajuste de sys.path", test_sys_path_ajuste),
        ("Importación desde Ticketera", test_import_desde_ticketera)
    ]
    
    resultados = {}
    
    for nombre, test_func in tests:
        print(f"\n{'='*20} {nombre.upper()} {'='*20}")
        try:
            resultado = test_func()
            resultados[nombre] = resultado
            if resultado:
                print(f"✅ {nombre}: OK")
            else:
                print(f"❌ {nombre}: FALLÓ")
        except Exception as e:
            print(f"❌ {nombre}: ERROR - {e}")
            resultados[nombre] = False
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DEL TEST")
    print("=" * 80)
    
    tests_pasados = sum(1 for resultado in resultados.values() if resultado)
    total_tests = len(resultados)
    
    print(f"✅ Tests pasados: {tests_pasados}/{total_tests}")
    
    for nombre, resultado in resultados.items():
        status = "✅ OK" if resultado else "❌ FALLÓ"
        print(f"   {status}: {nombre}")
    
    if tests_pasados == total_tests:
        print("\n🎉 TODOS LOS TESTS PASARON - IMPORTACIÓN DEBERÍA FUNCIONAR")
        print("💡 El error de importación debería estar resuelto")
    else:
        print(f"\n⚠️ {total_tests - tests_pasados} TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
    
    return tests_pasados == total_tests

if __name__ == "__main__":
    main()
