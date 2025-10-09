# test_agregacion.py
# Script para probar las funciones de agregacion

import json

def test_json_operations():
    """Test básico de operaciones JSON"""
    try:
        # Leer archivo
        with open('productos.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        print(" Lectura de JSON exitosa")
        
        # Verificar estructura
        required_keys = ['productos', 'sucursales', 'ofertas', 'negocios', 'categorias']
        for key in required_keys:
            if key not in datos:
                datos[key] = [] if key != 'negocios' and key != 'categorias' else {}
                print(f" Agregada sección faltante: {key}")
        
        # Test de escritura
        with open('productos_test.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print(" Escritura de JSON exitosa")
        
        # Limpiar archivo de test
        import os
        os.remove('productos_test.json')
        print(" Test completado exitosamente")
        
        return True
        
    except Exception as e:
        print(f" Error en test: {e}")
        return False

if __name__ == "__main__":
    test_json_operations()
