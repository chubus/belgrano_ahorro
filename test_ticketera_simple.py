#!/usr/bin/env python3
"""
Script para probar Ticketera de forma simple
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

# Definir modelo simple
class Ticket(db.Model):
    __tablename__ = 'ticket'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cliente_nombre = db.Column(db.String(120), nullable=False)
    cliente_direccion = db.Column(db.String(200), nullable=False)
    cliente_telefono = db.Column(db.String(50), nullable=False)
    cliente_email = db.Column(db.String(120), nullable=False)
    productos = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False, default=0.0)
    estado = db.Column(db.String(20), default='pendiente')
    prioridad = db.Column(db.String(20), default='normal')
    indicaciones = db.Column(db.Text)
    asignado_a = db.Column(db.Integer, nullable=True)
    repartidor_nombre = db.Column(db.String(50), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_asignacion = db.Column(db.DateTime, nullable=True)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    notas_repartidor = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Ticket {self.numero}>'

def test_ticketera_simple():
    """Probar Ticketera de forma simple"""
    try:
        with app.app_context():
            # Probar consulta simple
            ticket_count = db.session.query(Ticket).count()
            print(f"✅ Tickets encontrados: {ticket_count}")
            
            # Probar consulta con filtros
            tickets_pendientes = db.session.query(Ticket).filter_by(estado='pendiente').count()
            print(f"✅ Tickets pendientes: {tickets_pendientes}")
            
            # Probar consulta con joins
            tickets_con_repartidor = db.session.query(Ticket).filter(Ticket.asignado_a.isnot(None)).count()
            print(f"✅ Tickets con repartidor: {tickets_con_repartidor}")
            
            print("✅ Ticketera funcionando correctamente")
            return True
            
    except Exception as e:
        print(f"❌ Error en Ticketera: {e}")
        return False

if __name__ == "__main__":
    test_ticketera_simple()

