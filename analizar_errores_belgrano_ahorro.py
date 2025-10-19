#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar errores específicos en archivos de Belgrano Ahorro
Análisis minucioso línea por línea
"""

import os
import re
import sys
from pathlib import Path

def analizar_archivo_belgrano_ahorro(archivo_path):
    """Analizar un archivo de Belgrano Ahorro línea por línea"""
    print(f"\n🔍 ANALIZANDO: {archivo_path}")
    print("-" * 60)
    
    errores_encontrados = []
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        for i, linea in enumerate(lineas, 1):
            # Verificar errores de codificación Unicode
            if re.search(r'print.*[🔗📋✅❌⚠️ℹ️]', linea):
                errores_encontrados.append({
                    'linea': i,
                    'tipo': 'unicode',
                    'descripcion': 'Emoji en print puede causar UnicodeEncodeError',
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
            if 'session.get' in linea and 'from flask import session' not in ''.join(lineas[:i]):
                errores_encontrados.append({
                    'linea': i,
                    'tipo': 'variable',
                    'descripcion': 'session puede no estar importado',
                    'contenido': linea.strip()
                })
            
            # Verificar errores de indentación
            if re.match(r'^\s*return jsonify.*401', linea):
                if i > 1:
                    linea_anterior = lineas[i-2].strip()
                    if 'if request.headers.get' in linea_anterior and not linea_anterior.startswith('    '):
                        errores_encontrados.append({
                            'linea': i,
                            'tipo': 'indentacion',
                            'descripcion': 'return jsonify sin indentación correcta después de if',
                            'contenido': linea.strip()
                        })
            
            # Verificar errores de logging
            if 'logging.basicConfig' in linea and 'jsonify' in linea:
                errores_encontrados.append({
                    'linea': i,
                    'tipo': 'logging',
                    'descripcion': 'logging.basicConfig con parámetro inválido jsonify',
                    'contenido': linea.strip()
                })
            
            # Verificar errores de comillas escapadas
            if re.search(r"request\.headers\.get\\(\\'Accept\\'\\)", linea):
                errores_encontrados.append({
                    'linea': i,
                    'tipo': 'comillas',
                    'descripcion': 'Comillas escapadas incorrectamente',
                    'contenido': linea.strip()
                })
            
            # Verificar errores de sintaxis en datetime
            if 'datetime.now(' in linea and ', jsonify)' in linea:
                errores_encontrados.append({
                    'linea': i,
                    'tipo': 'sintaxis',
                    'descripcion': 'datetime.now con parámetro inválido',
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

def verificar_unicode_errors(archivo_path):
    """Verificar errores de codificación Unicode"""
    print(f"\n🔤 VERIFICANDO UNICODE: {archivo_path}")
    print("-" * 40)
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar emojis que pueden causar problemas
        emojis_problematicos = ['🔗', '📋', '✅', '❌', '⚠️', 'ℹ️']
        emojis_encontrados = []
        
        for emoji in emojis_problematicos:
            if emoji in contenido:
                emojis_encontrados.append(emoji)
        
        if emojis_encontrados:
            print(f"⚠️ Emojis encontrados que pueden causar UnicodeEncodeError: {emojis_encontrados}")
            return False
        else:
            print("✅ No se encontraron emojis problemáticos")
            return True
        
    except Exception as e:
        print(f"❌ Error verificando Unicode: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 ANÁLISIS MINUCIOSO DE ARCHIVOS BELGRANO AHORRO")
    print("=" * 60)
    
    # Archivos principales de Belgrano Ahorro
    archivos_belgrano_ahorro = [
        'app.py',
        'app_unificado.py',
        'db.py',
        'api_belgrano_ahorro.py',
        'auth_middleware.py',
        'error_handlers.py',
        'belgrano_client_gateway.py',
        'sincronizar_belgrano_ahorro.py'
    ]
    
    total_errores = 0
    archivos_con_errores = 0
    
    for archivo in archivos_belgrano_ahorro:
        if os.path.exists(archivo):
            # 1. Analizar errores
            errores = analizar_archivo_belgrano_ahorro(archivo)
            total_errores += len(errores)
            
            if errores:
                archivos_con_errores += 1
            
            # 2. Verificar sintaxis
            verificar_sintaxis_python(archivo)
            
            # 3. Verificar Unicode
            verificar_unicode_errors(archivo)
        else:
            print(f"⚠️ Archivo no encontrado: {archivo}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL ANÁLISIS")
    print("=" * 60)
    print(f"Archivos analizados: {len([a for a in archivos_belgrano_ahorro if os.path.exists(a)])}")
    print(f"Errores encontrados: {total_errores}")
    print(f"Archivos con errores: {archivos_con_errores}")
    
    if total_errores == 0:
        print("\n🎉 TODOS LOS ARCHIVOS BELGRANO AHORRO ESTÁN CORRECTOS")
    else:
        print(f"\n⚠️ {total_errores} errores encontrados en {archivos_con_errores} archivos")
    
    print("\n💡 Para verificar que todo funciona:")
    print("   python -m py_compile app.py")
    print("   python -m py_compile app_unificado.py")
    print("   python -m py_compile db.py")

if __name__ == "__main__":
    main()




