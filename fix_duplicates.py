#!/usr/bin/env python3
"""
Script para eliminar rutas duplicadas en devops_routes.py
"""

def fix_devops_routes():
    """Eliminar rutas duplicadas del archivo devops_routes.py"""
    
    # Leer el archivo
    with open('devops_routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Identificar líneas de rutas duplicadas
    duplicate_routes = [
        '/ofertas', '/negocios', '/productos', '/sync'
    ]
    
    # Encontrar las líneas que contienen las rutas duplicadas
    route_lines = []
    for i, line in enumerate(lines):
        if '@devops_bp.route(' in line:
            for route in duplicate_routes:
                if f"'{route}'" in line or f'"{route}"' in line:
                    route_lines.append(i)
                    break
    
    print(f"Encontradas {len(route_lines)} líneas de rutas")
    
    # Identificar las duplicadas (las segundas ocurrencias)
    duplicate_line_ranges = []
    
    # Buscar rangos de líneas duplicadas
    for i in range(len(route_lines)):
        if i > 0:  # No es la primera
            # Verificar si esta línea es una duplicada
            line_num = route_lines[i]
            line_content = lines[line_num]
            
            # Si contiene una ruta duplicada, marcar para eliminación
            for route in duplicate_routes:
                if f"'{route}'" in line_content or f'"{route}"' in line_content:
                    # Encontrar el final de esta función
                    end_line = find_function_end(lines, line_num)
                    duplicate_line_ranges.append((line_num, end_line))
                    break
    
    print(f"Encontrados {len(duplicate_line_ranges)} rangos duplicados")
    
    # Eliminar las líneas duplicadas (de atrás hacia adelante)
    for start, end in reversed(duplicate_line_ranges):
        print(f"Eliminando líneas {start+1} a {end+1}")
        del lines[start:end+1]
    
    # Escribir el archivo corregido
    with open('devops_routes.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Archivo devops_routes.py corregido")

def find_function_end(lines, start_line):
    """Encontrar el final de una función"""
    indent_level = None
    
    for i in range(start_line + 1, len(lines)):
        line = lines[i]
        
        # Si es una línea vacía, continuar
        if not line.strip():
            continue
            
        # Si es un comentario, continuar
        if line.strip().startswith('#'):
            continue
            
        # Si es una nueva función o clase, parar
        if (line.strip().startswith('@') or 
            line.strip().startswith('def ') or 
            line.strip().startswith('class ') or
            line.strip().startswith('if __name__')):
            return i - 1
            
        # Determinar nivel de indentación
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
            continue
            
        # Si encontramos una línea con menor indentación, parar
        if line.strip() and len(line) - len(line.lstrip()) <= indent_level:
            return i - 1
    
    return len(lines) - 1

if __name__ == "__main__":
    fix_devops_routes()

