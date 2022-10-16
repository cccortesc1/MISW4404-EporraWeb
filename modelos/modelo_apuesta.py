from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .db import db

class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor_apostado = db.Column(db.Numeric)
    ganancia = db.Column(db.Numeric, default=0)
    id_apostador = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    id_competidor = db.Column(db.Integer, db.ForeignKey("competidor.id"))
    id_carrera = db.Column(db.Integer, db.ForeignKey("carrera.id"))

class ApuestaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Apuesta
        include_relationships = True
        include_fk = True
        load_instance = True

    apostador = fields.String()
    valor_apostado = fields.String()
    ganancia = fields.String()
