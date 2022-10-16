from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .db import db

class Competidor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_competidor = db.Column(db.String(128))
    probabilidad = db.Column(db.Numeric)
    cuota = db.Column(db.Numeric)
    es_ganador = db.Column(db.Boolean, default=False)
    id_carrera = db.Column(db.Integer, db.ForeignKey("carrera.id"))

class CompetidorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Competidor
        include_relationships = True
        load_instance = True

    probabilidad = fields.String()
    cuota = fields.String()
