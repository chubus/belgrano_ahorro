#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la sintaxis del archivo devops_routes.py
"""

import ast
import sys
import os

def verificar_sintaxis_archivo(archivo_path):
    """Verificar la sintaxis de un archivo Python"""
    print(f"🔍 Verificando sintaxis de: {archivo_path}")
    
    if not os.path.exists(archivo_path):
        print(f"❌ Archivo no encontrado: {archivo_path}")
        return False
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        # Intentar compilar el código
        ast.parse(codigo)
        print(f"✅ Sintaxis correcta en: {archivo_path}")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en {archivo_path}:")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ Error verificando {archivo_path}: {e}")
        return False

def verificar_imports_devops_routes():
    """Verificar que se puedan importar los módulos necesarios"""
    print("\n🔍 Verificando imports de devops_routes...")
    
    try:
        # Cambiar al directorio correcto
        os.chdir('belgrano_tickets')
        
        # Intentar importar el módulo
        import devops_routes
        print("✅ devops_routes importado correctamente")
        
        # Verificar que el blueprint existe
        if hasattr(devops_routes, 'devops_bp'):
            print("✅ devops_bp encontrado")
        else:
            print("❌ devops_bp no encontrado")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Error importando devops_routes: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando imports: {e}")
        return False
    finally:
        # Volver al directorio original
        os.chdir('..')

def main():
    """Función principal"""
    print("🧪 VERIFICANDO SINTAXIS DE DEVOPS_ROUTES.PY")
    print("=" * 60)
    
    # Verificar sintaxis
    archivo_devops = 'belgrano_tickets/devops_routes.py'
    sintaxis_ok = verificar_sintaxis_archivo(archivo_devops)
    
    if not sintaxis_ok:
        print("\n❌ ERRORES DE SINTAXIS ENCONTRADOS")
        print("   El archivo devops_routes.py tiene errores de sintaxis")
        return False
    
    # Verificar imports
    imports_ok = verificar_imports_devops_routes()
    
    if not imports_ok:
        print("\n❌ ERRORES DE IMPORT ENCONTRADOS")
        print("   No se puede importar devops_routes correctamente")
        return False
    
    print("\n✅ VERIFICACIÓN EXITOSA")
    print("   - Sintaxis correcta")
    print("   - Imports funcionando")
    print("   - devops_bp disponible")
    print("   - Ticketera debería poder iniciarse")
    
    return True

if __name__ == "__main__":
    resultado = main()
    sys.exit(0 if resultado else 1)
