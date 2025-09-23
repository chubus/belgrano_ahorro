#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir errores de indentación en devops_persistence.py
"""

import re

def corregir_indentacion():
    """Corregir errores de indentación en devops_persistence.py"""
    
    with open('devops_persistence.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Patrones de errores comunes
    patrones_correccion = [
        # Corregir if sin indentación
        (r'(\n\s+)if ([^:]+):\n(\s+)return', r'\1if \2:\n\1    return'),
        (r'(\n\s+)if ([^:]+):\n(\s+)raise', r'\1if \2:\n\1    raise'),
        (r'(\n\s+)if ([^:]+):\n(\s+)logger', r'\1if \2:\n\1    logger'),
        (r'(\n\s+)if ([^:]+):\n(\s+)cursor', r'\1if \2:\n\1    cursor'),
        (r'(\n\s+)if ([^:]+):\n(\s+)conn', r'\1if \2:\n\1    conn'),
        
        # Corregir else sin indentación
        (r'(\n\s+)else:\n(\s+)return', r'\1else:\n\1    return'),
        (r'(\n\s+)else:\n(\s+)raise', r'\1else:\n\1    raise'),
        (r'(\n\s+)else:\n(\s+)logger', r'\1else:\n\1    logger'),
        (r'(\n\s+)else:\n(\s+)cursor', r'\1else:\n\1    cursor'),
        (r'(\n\s+)else:\n(\s+)conn', r'\1else:\n\1    conn'),
        
        # Corregir for sin indentación
        (r'(\n\s+)for ([^:]+):\n(\s+)return', r'\1for \2:\n\1    return'),
        (r'(\n\s+)for ([^:]+):\n(\s+)raise', r'\1for \2:\n\1    raise'),
        (r'(\n\s+)for ([^:]+):\n(\s+)logger', r'\1for \2:\n\1    logger'),
        (r'(\n\s+)for ([^:]+):\n(\s+)cursor', r'\1for \2:\n\1    cursor'),
        (r'(\n\s+)for ([^:]+):\n(\s+)conn', r'\1for \2:\n\1    conn'),
    ]
    
    # Aplicar correcciones
    for patron, reemplazo in patrones_correccion:
        contenido = re.sub(patron, reemplazo, contenido)
    
    # Escribir archivo corregido
    with open('devops_persistence.py', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ Errores de indentación corregidos")

if __name__ == "__main__":
    corregir_indentacion()
