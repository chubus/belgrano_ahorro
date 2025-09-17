#!/usr/bin/env python3
"""
Script para verificar que las correcciones de deploy se aplicaron correctamente
"""

import os
import sys

def check_blueprint_registration():
    """Verificar que no hay registros duplicados del blueprint"""
    app_file = "belgrano_tickets/app.py"
    
    if not os.path.exists(app_file):
        print(f"❌ Archivo no encontrado: {app_file}")
        return False
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar ocurrencias de register_blueprint(devops_bp)
        blueprint_registrations = content.count('register_blueprint(devops_bp)')
        
        print(f"📊 Registros de blueprint DevOps encontrados: {blueprint_registrations}")
        
        if blueprint_registrations == 1:
            print("✅ Blueprint DevOps registrado una sola vez (correcto)")
            return True
        elif blueprint_registrations > 1:
            print("❌ Blueprint DevOps registrado múltiples veces (problema)")
            return False
        else:
            print("❌ Blueprint DevOps no registrado (problema)")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando blueprint: {e}")
        return False

def check_indentation_fix():
    """Verificar que el script de inicialización no tiene errores de indentación"""
    script_file = "scripts/init_users_flota.py"
    
    if not os.path.exists(script_file):
        print(f"❌ Archivo no encontrado: {script_file}")
        return False
    
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Verificar que no hay errores de indentación obvios
        indentation_errors = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not line.startswith(' ') and not line.startswith('\t'):
                # Línea no vacía que no empieza con espacio o tab
                if not (stripped.startswith('#') or 
                       stripped.startswith('def ') or 
                       stripped.startswith('class ') or
                       stripped.startswith('if __name__') or
                       stripped.startswith('import ') or
                       stripped.startswith('from ') or
                       stripped == '"""' or
                       stripped.startswith('"""') or
                       stripped.startswith("'''") or
                       stripped.endswith('"""') or
                       stripped.endswith("'''")):
                    # Esta línea podría tener problemas de indentación
                    if 'return' in stripped or 'print(' in stripped:
                        print(f"⚠️ Posible problema de indentación en línea {i}: {stripped}")
                        indentation_errors += 1
        
        if indentation_errors == 0:
            print("✅ No se encontraron errores de indentación obvios")
            return True
        else:
            print(f"❌ Se encontraron {indentation_errors} posibles errores de indentación")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando indentación: {e}")
        return False

def test_script_syntax():
    """Probar que el script de inicialización tiene sintaxis válida"""
    script_file = "scripts/init_users_flota.py"
    
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Compilar el código para verificar sintaxis
        compile(code, script_file, 'exec')
        print("✅ Script de inicialización tiene sintaxis válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en {script_file}:")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Error verificando sintaxis: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICANDO CORRECCIONES DE DEPLOY")
    print("=" * 50)
    
    all_checks_passed = True
    
    # 1. Verificar blueprint
    print("\n1️⃣ Verificando registro de blueprint DevOps...")
    if not check_blueprint_registration():
        all_checks_passed = False
    
    # 2. Verificar indentación
    print("\n2️⃣ Verificando corrección de indentación...")
    if not check_indentation_fix():
        all_checks_passed = False
    
    # 3. Verificar sintaxis
    print("\n3️⃣ Verificando sintaxis del script...")
    if not test_script_syntax():
        all_checks_passed = False
    
    # Resultado final
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 TODAS LAS VERIFICACIONES PASARON")
        print("✅ Los errores de deploy han sido corregidos")
        print("\n💡 Próximos pasos:")
        print("   1. Commit y push de los cambios")
        print("   2. Redeploy en Render")
        print("   3. Verificar que el deploy sea exitoso")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("⚠️ Revisar los errores anteriores antes del deploy")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
