from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()
const_user_id = "usuario.id"
const_all_del_orphan = "all, delete, delete-orphan"
class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor_apostado = db.Column(db.Numeric)
    ganancia = db.Column(db.Numeric, default=0)
    id_apostador = db.Column(db.Integer, db.ForeignKey(const_user_id))
    id_competidor = db.Column(db.Integer, db.ForeignKey("competidor.id"))
    id_carrera = db.Column(db.Integer, db.ForeignKey("carrera.id"))


class Carrera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_carrera = db.Column(db.String(128))
    tipo_carrera = db.Column(db.Integer, db.ForeignKey("tipo_carrera.id"))
    abierta = db.Column(db.Boolean, default=True)
    competidores = db.relationship("Competidor", cascade=const_all_del_orphan)
    apuestas = db.relationship("Apuesta", cascade=const_all_del_orphan)
    usuario = db.Column(db.Integer, db.ForeignKey(const_user_id))


class Competidor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_competidor = db.Column(db.String(128))
    probabilidad = db.Column(db.Numeric)
    cuota = db.Column(db.Numeric)
    es_ganador = db.Column(db.Boolean, default=False)
    id_carrera = db.Column(db.Integer, db.ForeignKey("carrera.id"))


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    perfil = db.Column(db.String(50))
    saldo = db.Column(db.String(50), default="0")
    correo = db.Column(db.String(160), default="")
    medioPago = db.Column(db.String(50), default="")
    carreras = db.relationship("Carrera", cascade=const_all_del_orphan)
    apuestas = db.relationship("Apuesta", cascade=const_all_del_orphan)
    

class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Numeric)
    fecha = db.Column(db.DateTime)
    tipo = db.Column(db.String(50))
    id_usuario = db.Column(db.Integer, db.ForeignKey(const_user_id))


class TipoCarrera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_tipo_carrera = db.Column(db.String(128))
    cantidad_maxima_competidores = db.Column(db.Numeric)
    carreras = db.relationship("Carrera", cascade=const_all_del_orphan)

class ApuestaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Apuesta
        include_relationships = True
        include_fk = True
        load_instance = True

    apostador = fields.String()
    valor_apostado = fields.String()
    ganancia = fields.String()


class CompetidorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Competidor
        include_relationships = True
        load_instance = True

    probabilidad = fields.String()
    cuota = fields.String()


class CarreraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Carrera
        include_relationships = True
        load_instance = True

    competidores = fields.List(fields.Nested(CompetidorSchema()))
    apuestas = fields.List(fields.Nested(ApuestaSchema()))
    ganancia_casa = fields.Float()

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

    saldo = fields.String()


class TransaccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transaccion
        include_relationships = True
        load_instance = True

    valor = fields.String()
    fecha = fields.String()
    tipo = fields.String()

class ReporteSchema(Schema):
    carrera = fields.Nested(CarreraSchema())
    ganancia_casa = fields.Float()

class TipoCarreraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TipoCarrera
        include_relationships = False
        load_instance = True
    cantidad_maxima_competidores = fields.String()