from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .db import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    perfil = db.Column(db.String(50))
    saldo = db.Column(db.String(50), default="0")
    correo = db.Column(db.String(160), default="")
    medioPago = db.Column(db.String(50), default="")
    carreras = db.relationship("Carrera", cascade="all, delete, delete-orphan")
    apuestas = db.relationship("Apuesta", cascade="all, delete, delete-orphan")
    

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

    saldo = fields.String()
