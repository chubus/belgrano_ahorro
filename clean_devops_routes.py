#!/usr/bin/env python3
"""
Script para limpiar devops_routes.py eliminando duplicados
"""

def clean_devops_routes():
    """Limpiar el archivo devops_routes.py eliminando duplicados"""
    
    # Leer el archivo
    with open('devops_routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar la línea donde terminan las funciones válidas
    valid_end = None
    for i, line in enumerate(lines):
        if 'return redirect(url_for(\'devops.gestion_negocios\'))' in line:
            valid_end = i + 1
            break
    
    if valid_end is None:
        print("❌ No se encontró el final de las funciones válidas")
        return
    
    # Crear el archivo limpio
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
    
    # Escribir el archivo limpio
    with open('devops_routes.py', 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"✅ Archivo limpiado: {len(clean_lines)} líneas")
    print("✅ Duplicados eliminados")

if __name__ == "__main__":
    clean_devops_routes()

