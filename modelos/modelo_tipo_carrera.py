from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .db import db

class TipoCarrera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_tipo_carrera = db.Column(db.String(128))
    cantidad_maxima_competidores = db.Column(db.Numeric)

class TipoCarreraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TipoCarrera
        include_relationships = False
        load_instance = True
    cantidad_maxima_competidores = fields.String()