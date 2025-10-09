#!/usr/bin/env python3
"""
Script para verificar SQLAlchemy específicamente
"""

import os
import sys
sys.path.append('belgrano_tickets')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configurar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///belgrano_tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

def check_sqlalchemy_specific():
    """Verificar SQLAlchemy específicamente"""
    
    print("🔧 Verificando SQLAlchemy...")
    
    try:
        with app.app_context():
            # Verificar conexión
            print(f"✅ Conexión a base de datos: {db.engine.url}")
            
            # Verificar tablas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Tablas encontradas: {tables}")
            
            # Verificar columnas de ticket
            if 'ticket' in tables:
                columns = inspector.get_columns('ticket')
                print(f"✅ Columnas de ticket:")
                for col in columns:
                    print(f"  - {col['name']} ({col['type']})")
            
            # Verificar si hay problema con la consulta
            try:
                result = db.session.execute("SELECT COUNT(*) FROM ticket")
                count = result.fetchone()[0]
                print(f"✅ Consulta directa exitosa: {count} tickets")
            except Exception as e:
                print(f"❌ Error en consulta directa: {e}")
            
            # Verificar si hay problema con SQLAlchemy
            try:
                result = db.session.execute("SELECT id, numero, cliente_nombre, total FROM ticket LIMIT 1")
                row = result.fetchone()
                if row:
                    print(f"✅ Consulta SQLAlchemy exitosa: ID={row[0]}, Número={row[1]}, Cliente={row[2]}, Total={row[3]}")
                else:
                    print("✅ Consulta SQLAlchemy exitosa: No hay datos")
            except Exception as e:
                print(f"❌ Error en consulta SQLAlchemy: {e}")
            
    except Exception as e:
        print(f"❌ Error verificando SQLAlchemy: {e}")

if __name__ == "__main__":
    check_sqlalchemy_specific()

