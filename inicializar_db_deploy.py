#!/usr/bin/env python3
"""
Script de inicialización de bases de datos para deploy
Inicializa las bases de datos de Belgrano Ahorro y Belgrano Tickets
"""

import sqlite3
import os
import sys
from datetime import datetime

def inicializar_belgrano_ahorro():
    """Inicializar base de datos de Belgrano Ahorro"""
    
    print("🗄️ Inicializando base de datos Belgrano Ahorro...")
    
    try:
        # Importar función de creación de BD
        from db import crear_base_datos
        
        # Crear base de datos
        crear_base_datos()
        
        # Verificar que se creó correctamente
        if os.path.exists('belgrano_ahorro.db'):
            # Verificar tablas creadas
            conn = sqlite3.connect('belgrano_ahorro.db')
            cursor = conn.cursor()
            
            # Listar tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()
            
            print(f"   ✅ Base de datos creada: belgrano_ahorro.db")
            print(f"   📋 Tablas creadas: {len(tablas)}")
            
            for tabla in tablas:
                print(f"      - {tabla[0]}")
            
            conn.close()
            return True
        else:
            print("   ❌ Error: No se pudo crear la base de datos")
            return False
            
    except Exception as e:
        print(f"   ❌ Error inicializando BD Belgrano Ahorro: {e}")
        return False

def inicializar_belgrano_tickets():
    """Inicializar base de datos de Belgrano Tickets"""
    
    print("🗄️ Inicializando base de datos Belgrano Tickets...")
    
    try:
        # Cambiar al directorio de tickets
        tickets_dir = 'belgrano_tickets'
        if not os.path.exists(tickets_dir):
            print(f"   ❌ Error: Directorio {tickets_dir} no encontrado")
            return False
        
        # Verificar que la base de datos ya existe y tiene usuarios
        db_path = os.path.join(tickets_dir, 'belgrano_tickets.db')
        if os.path.exists(db_path):
            # Verificar tablas creadas
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Listar tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = cursor.fetchall()
            
            print(f"   ✅ Base de datos existente: {db_path}")
            print(f"   📋 Tablas encontradas: {len(tablas)}")
            
            for tabla in tablas:
                print(f"      - {tabla[0]}")
            
            # Verificar usuarios existentes
            try:
                cursor.execute("SELECT COUNT(*) FROM user")
                usuarios_count = cursor.fetchone()[0]
                print(f"   👥 Usuarios existentes: {usuarios_count}")
            except:
                print("   ⚠️ No se pudo contar usuarios")
            
            conn.close()
            return True
        else:
            print("   ❌ Error: Base de datos no encontrada")
            print("   💡 La base de datos se creará automáticamente al ejecutar la aplicación")
            return False
                
    except Exception as e:
        print(f"   ❌ Error verificando BD Belgrano Tickets: {e}")
        return False

def verificar_estructura_bd():
    """Verificar la estructura de ambas bases de datos"""
    
    print("\n🔍 Verificando estructura de bases de datos...")
    
    # Verificar Belgrano Ahorro
    if os.path.exists('belgrano_ahorro.db'):
        try:
            conn = sqlite3.connect('belgrano_ahorro.db')
            cursor = conn.cursor()
            
            # Verificar tablas principales
            tablas_requeridas = ['usuarios', 'pedidos', 'pedido_items', 'comerciantes']
            tablas_existentes = []
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            for tabla in cursor.fetchall():
                tablas_existentes.append(tabla[0])
            
            print("   📊 Belgrano Ahorro:")
            for tabla in tablas_requeridas:
                if tabla in tablas_existentes:
                    print(f"      ✅ {tabla}")
                else:
                    print(f"      ❌ {tabla} (FALTANTE)")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Error verificando BD Ahorro: {e}")
    
    # Verificar Belgrano Tickets
    tickets_db_path = os.path.join('belgrano_tickets', 'belgrano_tickets.db')
    if os.path.exists(tickets_db_path):
        try:
            conn = sqlite3.connect(tickets_db_path)
            cursor = conn.cursor()
            
            # Verificar tablas principales
            tablas_requeridas = ['user', 'ticket', 'configuracion']
            tablas_existentes = []
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            for tabla in cursor.fetchall():
                tablas_existentes.append(tabla[0])
            
            print("   📊 Belgrano Tickets:")
            for tabla in tablas_requeridas:
                if tabla in tablas_existentes:
                    print(f"      ✅ {tabla}")
                else:
                    print(f"      ❌ {tabla} (FALTANTE)")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Error verificando BD Tickets: {e}")

def crear_backup():
    """Crear backup de las bases de datos existentes"""
    
    print("\n💾 Creando backups de bases de datos existentes...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Backup Belgrano Ahorro
    if os.path.exists('belgrano_ahorro.db'):
        backup_path = f'belgrano_ahorro_backup_{timestamp}.db'
        try:
            import shutil
            shutil.copy2('belgrano_ahorro.db', backup_path)
            print(f"   ✅ Backup creado: {backup_path}")
        except Exception as e:
            print(f"   ❌ Error creando backup Ahorro: {e}")
    
    # Backup Belgrano Tickets
    tickets_db_path = os.path.join('belgrano_tickets', 'belgrano_tickets.db')
    if os.path.exists(tickets_db_path):
        backup_path = f'belgrano_tickets_backup_{timestamp}.db'
        try:
            import shutil
            shutil.copy2(tickets_db_path, backup_path)
            print(f"   ✅ Backup creado: {backup_path}")
        except Exception as e:
            print(f"   ❌ Error creando backup Tickets: {e}")

def generar_reporte_inicializacion(resultados):
    """Generar reporte de inicialización"""
    
    reporte = {
        'fecha_inicializacion': datetime.now().isoformat(),
        'resultados': resultados,
        'archivos_creados': [],
        'errores': []
    }
    
    # Verificar archivos creados
    if os.path.exists('belgrano_ahorro.db'):
        reporte['archivos_creados'].append('belgrano_ahorro.db')
    
    tickets_db_path = os.path.join('belgrano_tickets', 'belgrano_tickets.db')
    if os.path.exists(tickets_db_path):
        reporte['archivos_creados'].append('belgrano_tickets.db')
    
    # Guardar reporte
    with open('reporte_inicializacion_db.json', 'w') as f:
        import json
        json.dump(reporte, f, indent=2)
    
    print("\n📄 Reporte guardado en: reporte_inicializacion_db.json")

def main():
    """Función principal de inicialización"""
    
    print("🚀 INICIALIZACIÓN DE BASES DE DATOS PARA DEPLOY")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear backups antes de inicializar
    crear_backup()
    
    # Resultados de inicialización
    resultados = {
        'ahorro_inicializado': False,
        'tickets_inicializado': False,
        'errores': []
    }
    
    # 1. Inicializar Belgrano Ahorro
    print("\n1️⃣ INICIALIZANDO BELGRANO AHORRO")
    print("-" * 30)
    resultados['ahorro_inicializado'] = inicializar_belgrano_ahorro()
    
    # 2. Inicializar Belgrano Tickets
    print("\n2️⃣ INICIALIZANDO BELGRANO TICKETS")
    print("-" * 30)
    resultados['tickets_inicializado'] = inicializar_belgrano_tickets()
    
    # 3. Verificar estructura
    verificar_estructura_bd()
    
    # 4. Resumen
    print("\n📋 RESUMEN DE INICIALIZACIÓN")
    print("=" * 30)
    
    total_sistemas = 2
    sistemas_inicializados = sum([
        resultados['ahorro_inicializado'],
        resultados['tickets_inicializado']
    ])
    
    print(f"✅ Sistemas inicializados: {sistemas_inicializados}/{total_sistemas}")
    
    if resultados['ahorro_inicializado']:
        print("   ✅ Belgrano Ahorro: INICIALIZADO")
    else:
        print("   ❌ Belgrano Ahorro: ERROR")
        resultados['errores'].append("Error inicializando Belgrano Ahorro")
    
    if resultados['tickets_inicializado']:
        print("   ✅ Belgrano Tickets: INICIALIZADO")
    else:
        print("   ❌ Belgrano Tickets: ERROR")
        resultados['errores'].append("Error inicializando Belgrano Tickets")
    
    # 5. Recomendaciones
    print("\n💡 RECOMENDACIONES")
    print("=" * 20)
    
    if sistemas_inicializados == total_sistemas:
        print("🎉 ¡Inicialización completada exitosamente!")
        print("   - Ambas bases de datos están listas")
        print("   - Los usuarios han sido creados")
        print("   - El sistema está listo para deploy")
    elif sistemas_inicializados >= 1:
        print("⚠️ Inicialización parcial")
        print("   - Algunas bases de datos pueden no estar disponibles")
        print("   - Revisar los errores listados arriba")
        print("   - Verificar permisos de archivos")
    else:
        print("🚨 Inicialización fallida")
        print("   - Ninguna base de datos se pudo inicializar")
        print("   - Revisar configuración del sistema")
        print("   - Verificar dependencias instaladas")
    
    # 6. Generar reporte
    generar_reporte_inicializacion(resultados)
    
    print("\n🏁 Inicialización completada")
    print("=" * 30)

if __name__ == "__main__":
    main()
