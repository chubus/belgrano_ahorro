#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación de Errores DevOps - Item por Item
Comprueba cada error mencionado anteriormente
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class VerificadorErroresDevOps:
    """Verificador de errores específicos en DevOps"""
    
    def __init__(self):
        self.base_url = "http://localhost:5002"
        self.errores_encontrados = []
        self.errores_corregidos = []
        self.estado_actual = {}
    
    def verificar_endpoint_logs(self) -> Dict:
        """Verificar error en /devops/logs"""
        print("🔍 VERIFICANDO /devops/logs...")
        
        try:
            # Simular petición al endpoint
            import requests
            response = requests.get(f"{self.base_url}/devops/logs", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'logs' in data['data']:
                        self.errores_corregidos.append("devops/logs - JSON válido")
                        return {'estado': 'corregido', 'detalle': 'Devuelve JSON válido'}
                    else:
                        self.errores_encontrados.append("devops/logs - Estructura JSON incorrecta")
                        return {'estado': 'error', 'detalle': 'Estructura JSON incorrecta'}
                except json.JSONDecodeError:
                    self.errores_encontrados.append("devops/logs - Error JSON")
                    return {'estado': 'error', 'detalle': 'Error de conexión: Unexpected token'}
            else:
                self.errores_encontrados.append(f"devops/logs - Status {response.status_code}")
                return {'estado': 'error', 'detalle': f'Status {response.status_code}'}
        except Exception as e:
            self.errores_encontrados.append(f"devops/logs - Error de conexión: {e}")
            return {'estado': 'error', 'detalle': f'Error de conexión: {e}'}
    
    def verificar_endpoint_config(self) -> Dict:
        """Verificar error en /devops/config"""
        print("🔍 VERIFICANDO /devops/config...")
        
        try:
            import requests
            response = requests.get(f"{self.base_url}/devops/config", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'config' in data['data']:
                        self.errores_corregidos.append("devops/config - JSON válido")
                        return {'estado': 'corregido', 'detalle': 'Devuelve JSON válido'}
                    else:
                        self.errores_encontrados.append("devops/config - Estructura JSON incorrecta")
                        return {'estado': 'error', 'detalle': 'Estructura JSON incorrecta'}
                except json.JSONDecodeError:
                    self.errores_encontrados.append("devops/config - Error JSON")
                    return {'estado': 'error', 'detalle': 'Error de conexión: Unexpected token'}
            else:
                self.errores_encontrados.append(f"devops/config - Status {response.status_code}")
                return {'estado': 'error', 'detalle': f'Status {response.status_code}'}
        except Exception as e:
            self.errores_encontrados.append(f"devops/config - Error de conexión: {e}")
            return {'estado': 'error', 'detalle': f'Error de conexión: {e}'}
    
    def verificar_endpoint_test(self) -> Dict:
        """Verificar error en /devops/test"""
        print("🔍 VERIFICANDO /devops/test...")
        
        try:
            import requests
            response = requests.get(f"{self.base_url}/devops/test", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'authenticated' in data and 'message' in data:
                        self.errores_corregidos.append("devops/test - JSON válido")
                        return {'estado': 'corregido', 'detalle': 'Devuelve JSON válido'}
                    else:
                        self.errores_encontrados.append("devops/test - Estructura JSON incorrecta")
                        return {'estado': 'error', 'detalle': 'Estructura JSON incorrecta'}
                except json.JSONDecodeError:
                    self.errores_encontrados.append("devops/test - Error JSON")
                    return {'estado': 'error', 'detalle': 'Error de conexión: Unexpected token'}
            else:
                self.errores_encontrados.append(f"devops/test - Status {response.status_code}")
                return {'estado': 'error', 'detalle': f'Status {response.status_code}'}
        except Exception as e:
            self.errores_encontrados.append(f"devops/test - Error de conexión: {e}")
            return {'estado': 'error', 'detalle': f'Error de conexión: {e}'}
    
    def verificar_endpoint_sync(self) -> Dict:
        """Verificar error en /devops/sync"""
        print("🔍 VERIFICANDO /devops/sync...")
        
        try:
            import requests
            response = requests.get(f"{self.base_url}/devops/sync", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and 'sync' in data['data']:
                        self.errores_corregidos.append("devops/sync - JSON válido")
                        return {'estado': 'corregido', 'detalle': 'Devuelve JSON válido'}
                    else:
                        self.errores_encontrados.append("devops/sync - Estructura JSON incorrecta")
                        return {'estado': 'error', 'detalle': 'Estructura JSON incorrecta'}
                except json.JSONDecodeError:
                    self.errores_encontrados.append("devops/sync - Error JSON")
                    return {'estado': 'error', 'detalle': 'Error de conexión: Unexpected token'}
            else:
                self.errores_encontrados.append(f"devops/sync - Status {response.status_code}")
                return {'estado': 'error', 'detalle': f'Status {response.status_code}'}
        except Exception as e:
            self.errores_encontrados.append(f"devops/sync - Error de conexión: {e}")
            return {'estado': 'error', 'detalle': f'Error de conexión: {e}'}
    
    def verificar_lista_productos_ofertas(self) -> Dict:
        """Verificar lista completa de productos en ofertas"""
        print("🔍 VERIFICANDO lista de productos en ofertas...")
        
        # Verificar archivo de ofertas
        if os.path.exists('belgrano_tickets/templates/devops/ofertas.html'):
            try:
                with open('belgrano_tickets/templates/devops/ofertas.html', 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Verificar si hay loop de productos
                if '{% for producto in productos %}' in contenido:
                    self.errores_corregidos.append("ofertas - Lista de productos dinámica")
                    return {'estado': 'corregido', 'detalle': 'Lista de productos dinámica implementada'}
                else:
                    self.errores_encontrados.append("ofertas - Lista de productos estática")
                    return {'estado': 'error', 'detalle': 'Lista de productos no es dinámica'}
            except Exception as e:
                self.errores_encontrados.append(f"ofertas - Error leyendo archivo: {e}")
                return {'estado': 'error', 'detalle': f'Error leyendo archivo: {e}'}
        else:
            self.errores_encontrados.append("ofertas - Archivo no encontrado")
            return {'estado': 'error', 'detalle': 'Archivo ofertas.html no encontrado'}
    
    def verificar_crear_negocio(self) -> Dict:
        """Verificar error Method Not Allowed al crear negocio"""
        print("🔍 VERIFICANDO crear negocio...")
        
        # Verificar archivo de rutas
        if os.path.exists('devops_routes.py'):
            try:
                with open('devops_routes.py', 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Verificar si la ruta acepta POST
                if '@devops_bp.route(\'/negocios\', methods=[\'GET\', \'POST\'])' in contenido:
                    self.errores_corregidos.append("negocios - Método POST configurado")
                    return {'estado': 'corregido', 'detalle': 'Método POST configurado para crear negocio'}
                else:
                    self.errores_encontrados.append("negocios - Método POST no configurado")
                    return {'estado': 'error', 'detalle': 'Method Not Allowed - POST no configurado'}
            except Exception as e:
                self.errores_encontrados.append(f"negocios - Error leyendo archivo: {e}")
                return {'estado': 'error', 'detalle': f'Error leyendo archivo: {e}'}
        else:
            self.errores_encontrados.append("negocios - Archivo devops_routes.py no encontrado")
            return {'estado': 'error', 'detalle': 'Archivo devops_routes.py no encontrado'}
    
    def verificar_crear_producto(self) -> Dict:
        """Verificar error Method Not Allowed al crear producto"""
        print("🔍 VERIFICANDO crear producto...")
        
        # Verificar archivo de rutas
        if os.path.exists('devops_routes.py'):
            try:
                with open('devops_routes.py', 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Verificar si la ruta acepta POST
                if '@devops_bp.route(\'/productos\', methods=[\'GET\', \'POST\'])' in contenido:
                    self.errores_corregidos.append("productos - Método POST configurado")
                    return {'estado': 'corregido', 'detalle': 'Método POST configurado para crear producto'}
                else:
                    self.errores_encontrados.append("productos - Método POST no configurado")
                    return {'estado': 'error', 'detalle': 'Method Not Allowed - POST no configurado'}
            except Exception as e:
                self.errores_encontrados.append(f"productos - Error leyendo archivo: {e}")
                return {'estado': 'error', 'detalle': f'Error leyendo archivo: {e}'}
        else:
            self.errores_encontrados.append("productos - Archivo devops_routes.py no encontrado")
            return {'estado': 'error', 'detalle': 'Archivo devops_routes.py no encontrado'}
    
    def verificar_reflejo_belgrano_ahorro(self) -> Dict:
        """Verificar que los cambios se reflejen en Belgrano Ahorro"""
        print("🔍 VERIFICANDO reflejo en Belgrano Ahorro...")
        
        # Verificar archivo de rutas
        if os.path.exists('devops_routes.py'):
            try:
                with open('devops_routes.py', 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Verificar si hay sincronización con Belgrano Ahorro
                if 'cargar_datos_completos' in contenido and 'guardar_datos_json' in contenido:
                    self.errores_corregidos.append("belgrano_ahorro - Sincronización configurada")
                    return {'estado': 'corregido', 'detalle': 'Sincronización con Belgrano Ahorro configurada'}
                else:
                    self.errores_encontrados.append("belgrano_ahorro - Sincronización no configurada")
                    return {'estado': 'error', 'detalle': 'Sincronización con Belgrano Ahorro no configurada'}
            except Exception as e:
                self.errores_encontrados.append(f"belgrano_ahorro - Error leyendo archivo: {e}")
                return {'estado': 'error', 'detalle': f'Error leyendo archivo: {e}'}
        else:
            self.errores_encontrados.append("belgrano_ahorro - Archivo devops_routes.py no encontrado")
            return {'estado': 'error', 'detalle': 'Archivo devops_routes.py no encontrado'}
    
    def ejecutar_verificacion_completa(self):
        """Ejecutar verificación completa de todos los errores"""
        print("🚀 INICIANDO VERIFICACIÓN COMPLETA DE ERRORES DEVOPS...")
        print("=" * 60)
        
        # 1. Verificar endpoint logs
        self.estado_actual['logs'] = self.verificar_endpoint_logs()
        
        # 2. Verificar endpoint config
        self.estado_actual['config'] = self.verificar_endpoint_config()
        
        # 3. Verificar endpoint test
        self.estado_actual['test'] = self.verificar_endpoint_test()
        
        # 4. Verificar endpoint sync
        self.estado_actual['sync'] = self.verificar_endpoint_sync()
        
        # 5. Verificar lista de productos en ofertas
        self.estado_actual['productos_ofertas'] = self.verificar_lista_productos_ofertas()
        
        # 6. Verificar crear negocio
        self.estado_actual['crear_negocio'] = self.verificar_crear_negocio()
        
        # 7. Verificar crear producto
        self.estado_actual['crear_producto'] = self.verificar_crear_producto()
        
        # 8. Verificar reflejo en Belgrano Ahorro
        self.estado_actual['reflejo_belgrano'] = self.verificar_reflejo_belgrano_ahorro()
        
        # Generar reporte
        self.generar_reporte_verificacion()
        
        return self.estado_actual
    
    def generar_reporte_verificacion(self):
        """Generar reporte de verificación"""
        print("\n📋 GENERANDO REPORTE DE VERIFICACIÓN...")
        
        reporte = f"""
# 🔍 REPORTE DE VERIFICACIÓN DE ERRORES DEVOPS
## Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 ESTADO ACTUAL DE CADA ERROR

### 1. /devops/logs
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['logs']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['logs']['detalle']}

### 2. /devops/config
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['config']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['config']['detalle']}

### 3. /devops/test
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['test']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['test']['detalle']}

### 4. /devops/sync
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['sync']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['sync']['detalle']}

### 5. Lista de productos en ofertas
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['productos_ofertas']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['productos_ofertas']['detalle']}

### 6. Crear negocio (Method Not Allowed)
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['crear_negocio']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['crear_negocio']['detalle']}

### 7. Crear producto (Method Not Allowed)
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['crear_producto']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['crear_producto']['detalle']}

### 8. Reflejo en Belgrano Ahorro
- **Estado**: {'✅ CORREGIDO' if self.estado_actual['reflejo_belgrano']['estado'] == 'corregido' else '❌ ERROR'}
- **Detalle**: {self.estado_actual['reflejo_belgrano']['detalle']}

## 📈 RESUMEN DE RESULTADOS

### ✅ ERRORES CORREGIDOS: {len(self.errores_corregidos)}
{chr(10).join([f"- {error}" for error in self.errores_corregidos])}

### ❌ ERRORES PENDIENTES: {len(self.errores_encontrados)}
{chr(10).join([f"- {error}" for error in self.errores_encontrados])}

## 🎯 CONCLUSIÓN

{'✅ TODOS LOS ERRORES CORREGIDOS' if len(self.errores_encontrados) == 0 else '⚠️ ALGUNOS ERRORES PENDIENTES'}

### 🚀 PRÓXIMOS PASOS:
1. **Ejecutar aplicaciones**: python app_unificado.py, python app_tickets.py
2. **Testear endpoints**: Verificar que todos los endpoints funcionen
3. **Verificar flujos**: Probar creación de negocios y productos
4. **Validar sincronización**: Confirmar que los cambios se reflejen en Belgrano Ahorro
"""
        
        # Guardar reporte
        with open('reporte_verificacion_errores.txt', 'w', encoding='utf-8') as f:
            f.write(reporte)
        
        print("✅ VERIFICACIÓN COMPLETADA")
        print("📄 Reporte guardado en 'reporte_verificacion_errores.txt'")
        
        return reporte

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE ERRORES DEVOPS - ITEM POR ITEM")
    print("=" * 60)
    
    verificador = VerificadorErroresDevOps()
    resultados = verificador.ejecutar_verificacion_completa()
    
    print("\n🎯 RESUMEN FINAL:")
    print(f"Errores corregidos: {len(verificador.errores_corregidos)}")
    print(f"Errores pendientes: {len(verificador.errores_encontrados)}")
    
    if len(verificador.errores_encontrados) == 0:
        print("✅ TODOS LOS ERRORES HAN SIDO CORREGIDOS")
    else:
        print("⚠️ ALGUNOS ERRORES AÚN PENDIENTES")

if __name__ == "__main__":
    main()
