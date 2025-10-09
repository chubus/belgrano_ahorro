#!/usr/bin/env python3
"""
Script para verificar la configuración de SQLAlchemy
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

def check_sqlalchemy_config():
    """Verificar configuración de SQLAlchemy"""
    
    print(f"🔧 Configuración SQLAlchemy:")
    print(f"  - DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"  - TRACK_MODIFICATIONS: {app.config['SQLALCHEMY_TRACK_MODIFICATIONS']}")
    
    try:
        with app.app_context():
            # Verificar conexión
            db.engine.execute("SELECT 1")
            print("✅ Conexión a base de datos exitosa")
            
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
                result = db.engine.execute("SELECT COUNT(*) FROM ticket")
                count = result.fetchone()[0]
                print(f"✅ Consulta directa exitosa: {count} tickets")
            except Exception as e:
                print(f"❌ Error en consulta directa: {e}")
            
            # Verificar si hay problema con SQLAlchemy
            try:
                result = db.session.execute("SELECT COUNT(*) FROM ticket")
                count = result.fetchone()[0]
                print(f"✅ Consulta SQLAlchemy exitosa: {count} tickets")
            except Exception as e:
                print(f"❌ Error en consulta SQLAlchemy: {e}")
            
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")

if __name__ == "__main__":
    check_sqlalchemy_config()

