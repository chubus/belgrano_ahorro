#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir todos los errores en archivos de DevOps
Análisis minucioso línea por línea
"""

import os
import re
import sys
from pathlib import Path

def analizar_archivo_devops(archivo_path):
    """Analizar un archivo de DevOps línea por línea"""
    print(f"\n🔍 ANALIZANDO: {archivo_path}")
    print("-" * 60)
    
    errores_encontrados = []
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        for i, linea in enumerate(lineas, 1):
            # Verificar errores de indentación
            if re.match(r'^\s*return jsonify.*401', linea):
                # Verificar si la línea anterior tiene un if sin indentación correcta
                if i > 1:
                    linea_anterior = lineas[i-2].strip()
                    if 'if request.headers.get' in linea_anterior and not linea_anterior.startswith('    '):
                        errores_encontrados.append({
                            'linea': i,
                            'tipo': 'indentacion',
                            'descripcion': 'return jsonify sin indentación correcta después de if',
                            'contenido': linea.strip()
                        })
            
            # Verificar imports faltantes
            if 'from flask import' in linea and 'jsonify' not in linea and 'return jsonify' in ''.join(lineas[i:i+10]):
                errores_encontrados.append({
                    'linea': i,
                    'tipo': 'import',
                    'descripcion': 'jsonify no importado pero se usa',
                    'contenido': linea.strip()
                })
            
            # Verificar variables no definidas
            if 'devops_manager' in linea and 'devops_manager = None' not in ''.join(lineas[:i]):
                if 'if devops_manager' not in linea and 'devops_manager.' not in linea:
                    errores_encontrados.append({
                        'linea': i,
                        'tipo': 'variable',
                        'descripcion': 'devops_manager puede no estar definido',
                        'contenido': linea.strip()
                    })
        
        if errores_encontrados:
            print(f"❌ {len(errores_encontrados)} errores encontrados:")
            for error in errores_encontrados:
                print(f"  Línea {error['linea']}: {error['tipo']} - {error['descripcion']}")
                print(f"    Contenido: {error['contenido']}")
        else:
            print("✅ No se encontraron errores obvios")
        
        return errores_encontrados
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return []

def corregir_errores_indentacion(archivo_path):
    """Corregir errores de indentación específicos"""
    print(f"\n🔧 CORRIGIENDO: {archivo_path}")
    print("-" * 40)
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Patrones de corrección
        correcciones = [
            # Corregir indentación de return jsonify después de if
            (r'(\s+)if request\.headers\.get\(\'Accept\'\) == \'application/json\':\s*\n(\s*)return jsonify', 
             r'\1if request.headers.get(\'Accept\') == \'application/json\':\n\1    return jsonify'),
            
            # Corregir imports faltantes
            (r'from flask import ([^)]+)(?!.*jsonify)', 
             r'from flask import \1, jsonify'),
        ]
        
        contenido_corregido = contenido
        cambios_realizados = 0
        
        for patron, reemplazo in correcciones:
            matches = re.findall(patron, contenido_corregido, re.MULTILINE)
            if matches:
                contenido_corregido = re.sub(patron, reemplazo, contenido_corregido, flags=re.MULTILINE)
                cambios_realizados += len(matches)
                print(f"✅ Corregidos {len(matches)} patrones de {patron[:30]}...")
        
        if cambios_realizados > 0:
            # Crear backup
            backup_path = f"{archivo_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"📁 Backup creado: {backup_path}")
            
            # Escribir archivo corregido
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido_corregido)
            print(f"✅ {cambios_realizados} correcciones aplicadas")
        else:
            print("ℹ️ No se encontraron patrones para corregir")
        
        return cambios_realizados > 0
        
    except Exception as e:
        print(f"❌ Error corrigiendo archivo: {e}")
        return False

def verificar_sintaxis_python(archivo_path):
    """Verificar sintaxis Python del archivo"""
    print(f"\n🐍 VERIFICANDO SINTAXIS: {archivo_path}")
    print("-" * 40)
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        compile(codigo, archivo_path, 'exec')
        print("✅ Sintaxis Python correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error verificando sintaxis: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 ANÁLISIS MINUCIOSO DE ARCHIVOS DEVOPS")
    print("=" * 60)
    
    # Archivos de DevOps a analizar
    archivos_devops = [
        'devops_routes.py',
        'belgrano_tickets/devops_routes.py',
        'belgrano_tickets/app.py',
        'devops_belgrano_manager_unified.py',
        'belgrano_client_gateway.py'
    ]
    
    total_errores = 0
    archivos_corregidos = 0
    
    for archivo in archivos_devops:
        if os.path.exists(archivo):
            # 1. Analizar errores
            errores = analizar_archivo_devops(archivo)
            total_errores += len(errores)
            
            # 2. Corregir errores
            if errores:
                if corregir_errores_indentacion(archivo):
                    archivos_corregidos += 1
            
            # 3. Verificar sintaxis
            verificar_sintaxis_python(archivo)
        else:
            print(f"⚠️ Archivo no encontrado: {archivo}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL ANÁLISIS")
    print("=" * 60)
    print(f"Archivos analizados: {len([a for a in archivos_devops if os.path.exists(a)])}")
    print(f"Errores encontrados: {total_errores}")
    print(f"Archivos corregidos: {archivos_corregidos}")
    
    if total_errores == 0:
        print("\n🎉 TODOS LOS ARCHIVOS DEVOPS ESTÁN CORRECTOS")
    else:
        print(f"\n⚠️ {total_errores} errores encontrados y corregidos")
    
    print("\n💡 Para verificar que todo funciona:")
    print("   python -m py_compile devops_routes.py")
    print("   python -m py_compile belgrano_tickets/devops_routes.py")
    print("   python -m py_compile belgrano_tickets/app.py")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Script para corregir todos los errores en archivos de DevOps
Análisis minucioso línea por línea
"""

import os
import re
import sys
from pathlib import Path

def analizar_archivo_devops(archivo_path):
    """Analizar un archivo de DevOps línea por línea"""
    print(f"\n🔍 ANALIZANDO: {archivo_path}")
    print("-" * 60)
    
    errores_encontrados = []
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        for i, linea in enumerate(lineas, 1):
            # Verificar errores de indentación
            if re.match(r'^\s*return jsonify.*401', linea):
                # Verificar si la línea anterior tiene un if sin indentación correcta
                if i > 1:
                    linea_anterior = lineas[i-2].strip()
                    if 'if request.headers.get' in linea_anterior and not linea_anterior.startswith('    '):
                        errores_encontrados.append({
                            'linea': i,
                            'tipo': 'indentacion',
                            'descripcion': 'return jsonify sin indentación correcta después de if',
                            'contenido': linea.strip()
                        })
            
            # Verificar imports faltantes
            if 'from flask import' in linea and 'jsonify' not in linea and 'return jsonify' in ''.join(lineas[i:i+10]):
                errores_encontrados.append({
                    'linea': i,
                    'tipo': 'import',
                    'descripcion': 'jsonify no importado pero se usa',
                    'contenido': linea.strip()
                })
            
            # Verificar variables no definidas
            if 'devops_manager' in linea and 'devops_manager = None' not in ''.join(lineas[:i]):
                if 'if devops_manager' not in linea and 'devops_manager.' not in linea:
                    errores_encontrados.append({
                        'linea': i,
                        'tipo': 'variable',
                        'descripcion': 'devops_manager puede no estar definido',
                        'contenido': linea.strip()
                    })
        
        if errores_encontrados:
            print(f"❌ {len(errores_encontrados)} errores encontrados:")
            for error in errores_encontrados:
                print(f"  Línea {error['linea']}: {error['tipo']} - {error['descripcion']}")
                print(f"    Contenido: {error['contenido']}")
        else:
            print("✅ No se encontraron errores obvios")
        
        return errores_encontrados
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return []

def corregir_errores_indentacion(archivo_path):
    """Corregir errores de indentación específicos"""
    print(f"\n🔧 CORRIGIENDO: {archivo_path}")
    print("-" * 40)
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Patrones de corrección
        correcciones = [
            # Corregir indentación de return jsonify después de if
            (r'(\s+)if request\.headers\.get\(\'Accept\'\) == \'application/json\':\s*\n(\s*)return jsonify', 
             r'\1if request.headers.get(\'Accept\') == \'application/json\':\n\1    return jsonify'),
            
            # Corregir imports faltantes
            (r'from flask import ([^)]+)(?!.*jsonify)', 
             r'from flask import \1, jsonify'),
        ]
        
        contenido_corregido = contenido
        cambios_realizados = 0
        
        for patron, reemplazo in correcciones:
            matches = re.findall(patron, contenido_corregido, re.MULTILINE)
            if matches:
                contenido_corregido = re.sub(patron, reemplazo, contenido_corregido, flags=re.MULTILINE)
                cambios_realizados += len(matches)
                print(f"✅ Corregidos {len(matches)} patrones de {patron[:30]}...")
        
        if cambios_realizados > 0:
            # Crear backup
            backup_path = f"{archivo_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"📁 Backup creado: {backup_path}")
            
            # Escribir archivo corregido
            with open(archivo_path, 'w', encoding='utf-8') as f:
                f.write(contenido_corregido)
            print(f"✅ {cambios_realizados} correcciones aplicadas")
        else:
            print("ℹ️ No se encontraron patrones para corregir")
        
        return cambios_realizados > 0
        
    except Exception as e:
        print(f"❌ Error corrigiendo archivo: {e}")
        return False

def verificar_sintaxis_python(archivo_path):
    """Verificar sintaxis Python del archivo"""
    print(f"\n🐍 VERIFICANDO SINTAXIS: {archivo_path}")
    print("-" * 40)
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        compile(codigo, archivo_path, 'exec')
        print("✅ Sintaxis Python correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error verificando sintaxis: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 ANÁLISIS MINUCIOSO DE ARCHIVOS DEVOPS")
    print("=" * 60)
    
    # Archivos de DevOps a analizar
    archivos_devops = [
        'devops_routes.py',
        'belgrano_tickets/devops_routes.py',
        'belgrano_tickets/app.py',
        'devops_belgrano_manager_unified.py',
        'belgrano_client_gateway.py'
    ]
    
    total_errores = 0
    archivos_corregidos = 0
    
    for archivo in archivos_devops:
        if os.path.exists(archivo):
            # 1. Analizar errores
            errores = analizar_archivo_devops(archivo)
            total_errores += len(errores)
            
            # 2. Corregir errores
            if errores:
                if corregir_errores_indentacion(archivo):
                    archivos_corregidos += 1
            
            # 3. Verificar sintaxis
            verificar_sintaxis_python(archivo)
        else:
            print(f"⚠️ Archivo no encontrado: {archivo}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL ANÁLISIS")
    print("=" * 60)
    print(f"Archivos analizados: {len([a for a in archivos_devops if os.path.exists(a)])}")
    print(f"Errores encontrados: {total_errores}")
    print(f"Archivos corregidos: {archivos_corregidos}")
    
    if total_errores == 0:
        print("\n🎉 TODOS LOS ARCHIVOS DEVOPS ESTÁN CORRECTOS")
    else:
        print(f"\n⚠️ {total_errores} errores encontrados y corregidos")
    
    print("\n💡 Para verificar que todo funciona:")
    print("   python -m py_compile devops_routes.py")
    print("   python -m py_compile belgrano_tickets/devops_routes.py")
    print("   python -m py_compile belgrano_tickets/app.py")

if __name__ == "__main__":
    main()


