#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar sintaxis de app.py
"""

import ast
import sys

def verificar_sintaxis(archivo):
    """Verificar que el archivo tiene sintaxis válida"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Intentar parsear el código
        ast.parse(contenido)
        print(f"✅ Sintaxis correcta en {archivo}")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en {archivo}:")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ Error verificando {archivo}: {e}")
        return False

if __name__ == "__main__":
    archivo = "app.py"
    if verificar_sintaxis(archivo):
        print("🎉 El archivo está listo para deploy!")
        sys.exit(0)
    else:
        print("💥 Hay errores de sintaxis que deben corregirse")
        sys.exit(1)
