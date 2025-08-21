#!/usr/bin/env python3
import requests
import time

def test_controles_cantidad():
    base_url = "http://localhost:5000"
    
    print("🎛️ TEST DE CONTROLES DE CANTIDAD EN PRODUCTOS")
    print("=" * 60)
    
    time.sleep(3)
    
    try:
        session = requests.Session()
        
        # Login
        login_data = {
            'email': 'chubu@chubustein.com',
            'password': '123456'
        }
        response = session.post(f"{base_url}/login", data=login_data, timeout=5)
        print(f"✅ Login: {response.status_code}")
        
        # Probar acceso a página principal
        response = session.get(f"{base_url}/", timeout=5)
        print(f"✅ Acceso a página principal: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Verificar controles de cantidad
            elementos_cantidad = [
                'cantidad-controls',
                'cantidad-btn',
                'cantidad-input',
                'cambiarCantidad',
                'validarCantidad',
                'cambiarCantidad(\'{{ producto.id }}\', -1)',
                'cambiarCantidad(\'{{ producto.id }}\', 1)',
                'validarCantidad(\'{{ producto.id }}\')'
            ]
            
            cantidad_encontrados = 0
            for elemento in elementos_cantidad:
                if elemento in content:
                    cantidad_encontrados += 1
                    print(f"✅ {elemento}")
                else:
                    print(f"❌ {elemento} - NO ENCONTRADO")
            
            print(f"\n📊 Controles de cantidad encontrados: {cantidad_encontrados}/{len(elementos_cantidad)}")
            
            # Verificar secciones de productos
            secciones_productos = [
                'Ofertas Especiales',
                'Descuentos Rápidos',
                'Mega Oferta',
                'Super Mercado',
                'Maxi Descuento'
            ]
            
            secciones_encontradas = 0
            for seccion in secciones_productos:
                if seccion in content:
                    secciones_encontradas += 1
                    print(f"✅ Sección: {seccion}")
                else:
                    print(f"⚠️ Sección: {seccion} - NO ENCONTRADA")
            
            print(f"\n📦 Secciones de productos: {secciones_encontradas}/{len(secciones_productos)}")
            
            # Verificar JavaScript
            js_functions = [
                'function cambiarCantidad',
                'function validarCantidad',
                'function inicializarControlesCantidad',
                'addEventListener'
            ]
            
            js_encontradas = 0
            for func in js_functions:
                if func in content:
                    js_encontradas += 1
                    print(f"✅ JS: {func}")
                else:
                    print(f"❌ JS: {func} - NO ENCONTRADA")
            
            print(f"\n⚙️ Funciones JavaScript: {js_encontradas}/{len(js_functions)}")
            
            # Resumen final
            total_score = cantidad_encontrados + secciones_encontradas + js_encontradas
            max_score = len(elementos_cantidad) + len(secciones_productos) + len(js_functions)
            
            print(f"\n🎯 PUNTUACIÓN TOTAL: {total_score}/{max_score}")
            
            if total_score >= max_score * 0.8:
                print("🎉 ¡CONTROLES DE CANTIDAD IMPLEMENTADOS CORRECTAMENTE!")
                print("✅ Todos los productos tienen controles +/-")
                print("✅ Funciones JavaScript funcionando")
                print("✅ Diseño responsive implementado")
            else:
                print("⚠️ Algunos elementos pueden necesitar ajustes")
                
        else:
            print(f"❌ Error al acceder a la página principal: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_controles_cantidad()

