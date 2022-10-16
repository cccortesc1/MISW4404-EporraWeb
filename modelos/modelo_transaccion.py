from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .db import db

class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Numeric)
    fecha = db.Column(db.DateTime)
    tipo = db.Column(db.String(50))
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))

class TransaccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transaccion
        include_relationships = True
        load_instance = True

    valor = fields.String()
    fecha = fields.String()
    tipo = fields.String()
