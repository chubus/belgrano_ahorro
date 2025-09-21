#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrector de URLs DevOps
Corrige todas las referencias a devops_bp en los templates
"""

import os
import re

def corregir_archivo(archivo_path):
    """Corregir URLs en un archivo"""
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Mapeo de URLs
        mapeo_urls = {
            'devops_bp.devops_logout': '/devops/logout',
            'devops_bp.gestion_productos': '/devops/productos',
            'devops_bp.gestion_negocios': '/devops/negocios',
            'devops_bp.gestion_ofertas': '/devops/ofertas',
            'devops_bp.gestion_precios': '/devops/precios',
            'devops_bp.devops_health': '/devops/health',
            'devops_bp.ver_logs': '/devops/logs',
            'devops_bp.ver_configuracion': '/devops/config'
        }
        
        # Aplicar correcciones
        contenido_corregido = contenido
        for url_antigua, url_nueva in mapeo_urls.items():
            patron = f"url_for\\('{url_antigua}'\\)"
            contenido_corregido = re.sub(patron, f"'{url_nueva}'", contenido_corregido)
        
        # Escribir archivo corregido
        with open(archivo_path, 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)
        
        print(f"✅ Corregido: {archivo_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo {archivo_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 CORRECTOR DE URLs DEVOPS")
    print("=" * 40)
    
    # Directorio de templates
    templates_dir = "belgrano_tickets/templates/devops"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Directorio no encontrado: {templates_dir}")
        return
    
    # Archivos a corregir
    archivos = [
        "ofertas.html",
        "negocios.html", 
        "productos.html",
        "precios.html",
        "health.html",
        "logs.html",
        "config.html",
        "sync.html"
    ]
    
    archivos_corregidos = 0
    
    for archivo in archivos:
        archivo_path = os.path.join(templates_dir, archivo)
        if os.path.exists(archivo_path):
            if corregir_archivo(archivo_path):
                archivos_corregidos += 1
        else:
            print(f"⚠️ Archivo no encontrado: {archivo}")
    
    print(f"\n✅ CORRECCIÓN COMPLETADA")
    print(f"📊 Archivos corregidos: {archivos_corregidos}")
    print(f"📋 URLs corregidas:")
    print(f"   • devops_bp.devops_logout → /devops/logout")
    print(f"   • devops_bp.gestion_productos → /devops/productos")
    print(f"   • devops_bp.gestion_negocios → /devops/negocios")
    print(f"   • devops_bp.gestion_ofertas → /devops/ofertas")
    print(f"   • devops_bp.gestion_precios → /devops/precios")
    print(f"   • devops_bp.devops_health → /devops/health")
    print(f"   • devops_bp.ver_logs → /devops/logs")
    print(f"   • devops_bp.ver_configuracion → /devops/config")

if __name__ == "__main__":
    main()
