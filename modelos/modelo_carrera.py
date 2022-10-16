from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from modelos.modelo_apuesta import ApuestaSchema

from modelos.modelo_competidor import CompetidorSchema
from .db import db

class Carrera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_carrera = db.Column(db.String(128))
    tipo_carrera = db.Column(db.Integer, db.ForeignKey("tipo_carrera.id"))
    abierta = db.Column(db.Boolean, default=True)
    competidores = db.relationship("Competidor", cascade="all, delete, delete-orphan")
    apuestas = db.relationship("Apuesta", cascade="all, delete, delete-orphan")
    usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))

class CarreraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Carrera
        include_relationships = True
        load_instance = True

    competidores = fields.List(fields.Nested(CompetidorSchema()))
    apuestas = fields.List(fields.Nested(ApuestaSchema()))
    ganancia_casa = fields.Float()

class ReporteSchema(Schema):
    carrera = fields.Nested(CarreraSchema())
    ganancia_casa = fields.Float()