#!/usr/bin/env python3
"""
Script para corregir devops_routes.py eliminando duplicados
"""

def fix_devops_routes():
    """Corregir devops_routes.py eliminando rutas duplicadas"""
    
    # Leer el archivo
    with open('devops_routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Archivo original: {len(lines)} líneas")
    
    # Encontrar la línea donde terminan las funciones válidas (antes de los duplicados)
    valid_end = None
    for i, line in enumerate(lines):
        if 'return redirect(url_for(\'devops.gestion_negocios\'))' in line:
            valid_end = i + 1
            break
    
    if valid_end is None:
        print("❌ No se encontró el final de las funciones válidas")
        return
    
    print(f"Funciones válidas terminan en línea: {valid_end}")
    
    # Crear el archivo corregido
    clean_lines = lines[:valid_end]
    
    # Agregar las funciones de error
    error_handlers = [
        "",
        "# ==================================================================",
        "# MANEJO DE ERRORES",
        "# ==================================================================",
        "",
        "@devops_bp.errorhandler(404)",
        "def devops_not_found(error):",
        '    """Manejar errores 404 en DevOps"""',
        "    return jsonify({",
        "        'status': 'error',",
        "        'message': 'Endpoint DevOps no encontrado',",
        "        'available_endpoints': [",
        "            '/devops/',",
        "            '/devops/health',",
        "            '/devops/status',",
        "            '/devops/info',",
        "            '/devops/ofertas',",
        "            '/devops/negocios',",
        "            '/devops/sync',",
        "            '/devops/logs',",
        "            '/devops/config'",
        "        ],",
        "        'timestamp': datetime.now().isoformat()",
        "    }), 404",
        "",
        "@devops_bp.errorhandler(500)",
        "def devops_internal_error(error):",
        '    """Manejar errores 500 en DevOps"""',
        "    return jsonify({",
        "        'status': 'error',",
        "        'message': 'Error interno del servidor DevOps',",
        "        'timestamp': datetime.now().isoformat()",
        "    }), 500"
    ]
    
    # Agregar las funciones de error
    for error_line in error_handlers:
        clean_lines.append(error_line + "\n")
    
    # Escribir el archivo corregido
    with open('devops_routes.py', 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"✅ Archivo corregido: {len(clean_lines)} líneas")
    print("✅ Rutas duplicadas eliminadas")
    print("✅ Solo se mantuvieron las funciones válidas y los manejadores de error")

if __name__ == "__main__":
    fix_devops_routes()

