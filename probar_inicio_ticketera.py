#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar que Ticketera pueda iniciarse sin errores de sintaxis
"""

import os
import sys
import traceback

def probar_import_app():
    """Probar que se pueda importar la aplicación principal"""
    print("🧪 PROBANDO INICIO DE TICKETERA")
    print("=" * 50)
    
    try:
        # Cambiar al directorio de belgrano_tickets
        os.chdir('belgrano_tickets')
        
        print("📁 Directorio actual:", os.getcwd())
        
        # Intentar importar la aplicación
        print("🔍 Importando app...")
        from app import app
        print("✅ app importado correctamente")
        
        # Verificar que la aplicación se puede crear
        print("🔍 Verificando aplicación...")
        with app.app_context():
            print("✅ Contexto de aplicación creado correctamente")
        
        # Verificar que devops_bp se puede importar
        print("🔍 Verificando devops_bp...")
        from devops_routes import devops_bp
        print("✅ devops_bp importado correctamente")
        
        # Verificar que la aplicación tiene el blueprint registrado
        if 'devops' in app.blueprints:
            print("✅ devops_bp registrado en la aplicación")
        else:
            print("⚠️ devops_bp no está registrado en la aplicación")
        
        print("\n✅ TICKETERA PUEDE INICIARSE CORRECTAMENTE")
        print("   - Sin errores de sintaxis")
        print("   - Todos los módulos se importan")
        print("   - La aplicación se puede crear")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ ERROR DE SINTAXIS:")
        print(f"   Archivo: {e.filename}")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
        
    except ImportError as e:
        print(f"❌ ERROR DE IMPORT:")
        print(f"   {e}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR INESPERADO:")
        print(f"   {e}")
        print("\n📋 Traceback completo:")
        traceback.print_exc()
        return False
        
    finally:
        # Volver al directorio original
        os.chdir('..')

def verificar_archivos_criticos():
    """Verificar que los archivos críticos existan"""
    print("\n🔍 VERIFICANDO ARCHIVOS CRÍTICOS")
    print("=" * 50)
    
    archivos_criticos = [
        'belgrano_tickets/app.py',
        'belgrano_tickets/devops_routes.py',
        'belgrano_tickets/api_client.py'
    ]
    
    archivos_ok = 0
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
            archivos_ok += 1
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
    
    print(f"\n📊 Archivos críticos: {archivos_ok}/{len(archivos_criticos)}")
    return archivos_ok == len(archivos_criticos)

def main():
    """Función principal"""
    print("🚀 VERIFICANDO INICIO DE TICKETERA")
    print("=" * 60)
    
    # Verificar archivos críticos
    archivos_ok = verificar_archivos_criticos()
    
    if not archivos_ok:
        print("\n❌ ARCHIVOS CRÍTICOS FALTANTES")
        return False
    
    # Probar import de la aplicación
    app_ok = probar_import_app()
    
    if app_ok:
        print("\n🎉 ¡ÉXITO! TICKETERA ESTÁ LISTA")
        print("   - Sin errores de sintaxis")
        print("   - Todos los módulos funcionan")
        print("   - La aplicación puede iniciarse")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Reiniciar Ticketera en producción")
        print("   2. Verificar logs de inicio")
        print("   3. Probar endpoints DevOps")
    else:
        print("\n❌ TICKETERA REQUIERE CORRECCIONES")
        print("   - Revisar errores de sintaxis")
        print("   - Verificar imports")
        print("   - Corregir problemas antes del deploy")
    
    return app_ok

if __name__ == "__main__":
    resultado = main()
    sys.exit(0 if resultado else 1)
