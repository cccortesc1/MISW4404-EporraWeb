import sys
from datetime import datetime
from unicodedata import numeric
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from modelos import (
    db,
    Usuario,
    Carrera,
    CarreraSchema,
    Competidor,
    TipoCarrera
)

carrera_schema = CarreraSchema()

class VistaCarrerasUsuario(Resource):
    @jwt_required()
    def post(self, id_usuario):
        stored_carrera = Carrera.query.filter(
            Carrera.nombre_carrera == request.json["nombre"]
        ).first()
        if stored_carrera is not None:
            return "La carrera ya existe", 412

        nueva_carrera = Carrera(nombre_carrera=request.json["nombre"], tipo_carrera = request.json["tipo_carrera"])

        probabilidad_total = 0
        nombres_competidores = []
        if len(request.json["competidores"]) <= 1:
            return "Debe tener al menos 2 competidores", 412
        tipo_carrera_seleccionada = TipoCarrera.query.get(nueva_carrera.tipo_carrera)
        if len(request.json["competidores"]) > tipo_carrera_seleccionada.cantidad_maxima_competidores:
            return "El tipo de carrera " + tipo_carrera_seleccionada.nombre_tipo_carrera + " solo permite " + str(int(tipo_carrera_seleccionada.cantidad_maxima_competidores)) + " competidores", 412
        for competidor in request.json["competidores"]:
            competidor["probabilidad"] = float(competidor["probabilidad"])
            if competidor["probabilidad"] == 0:
                return "La probabilidad de un competidor no puede ser cero", 412

            probabilidad_total += competidor["probabilidad"]
            cuota = round(
                (competidor["probabilidad"] / (1 - competidor["probabilidad"])), 2
            )
            if competidor["competidor"] in nombres_competidores:
                return "El nombre del competidor " + competidor["competidor"] + " está repetido", 412
            nombres_competidores.append(competidor["competidor"])
            competidor = Competidor(
                nombre_competidor=competidor["competidor"],
                probabilidad=competidor["probabilidad"],
                cuota=cuota,
                id_carrera=nueva_carrera.id,
            )
            nueva_carrera.competidores.append(competidor)

        if probabilidad_total != 1:
            return "La suma de las probabilidades debe ser 1", 412

        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.carreras.append(nueva_carrera)

        try:
            db.session.commit()
        except IntegrityError:
            type, value, traceback = sys.exc_info()
            print('> %s: %s: %s' % (type, value, traceback))
            db.session.rollback()
            return "El usuario ya tiene un carrera con dicho nombre", 409

        return carrera_schema.dump(nueva_carrera)

    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        carreras = Carrera.query.all() #usuario.carreras 
        newCarreras = []
        for carrera in carreras:
            newApuestas = []
            for apuesta in carrera.apuestas:
                apuesta.apostador = Usuario.query.get(apuesta.id_apostador).usuario
                newApuestas.append(apuesta)

            carrera.apuestas = newApuestas
            newCarreras.append(carrera)

        return [carrera_schema.dump(carrera) for carrera in newCarreras]

