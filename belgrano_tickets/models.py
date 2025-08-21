from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' o 'flota'
    nombre = db.Column(db.String(50))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    cliente_nombre = db.Column(db.String(120))
    cliente_direccion = db.Column(db.String(200))
    cliente_telefono = db.Column(db.String(50))
    cliente_email = db.Column(db.String(120))
    productos = db.Column(db.Text)  # JSON string con productos y negocios
    estado = db.Column(db.String(20), default='pendiente')
    prioridad = db.Column(db.String(20), default='normal')
    indicaciones = db.Column(db.Text)
    asignado_a = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    repartidor = db.Column(db.String(50), nullable=True)  # Nombre del repartidor (Repartidor1, Repartidor2, etc.)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
