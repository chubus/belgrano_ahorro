#!/usr/bin/env python3
"""
Script para iniciar La Ticketera y ver errores
"""
import os
import sys

def main():
    print("🎫 INICIANDO LA TICKETERA")
    print("=" * 30)
    
    # Cambiar al directorio de tickets
    os.chdir("belgrano_tickets")
    
    # Verificar archivos
    if not os.path.exists("app.py"):
        print("❌ No se encontró app.py")
        return
    
    if not os.path.exists("belgrano_tickets.db"):
        print("❌ No se encontró belgrano_tickets.db")
        print("💡 Ejecutando crear_db_simple.py...")
        os.system("python crear_db_simple.py")
    
    print("✅ Archivos verificados")
    print("🚀 Iniciando aplicación...")
    print("🌐 URL: http://localhost:5001")
    print("🔐 Login: admin@belgranoahorro.com / admin123")
    print("-" * 30)
    
    # Importar y ejecutar
    try:
        from app import app, socketio
        print("✅ Aplicación importada correctamente")
        socketio.run(app, debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

