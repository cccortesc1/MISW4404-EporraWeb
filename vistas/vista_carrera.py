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
    Competidor
)

carrera_schema = CarreraSchema()

class VistaCarrera(Resource):
    # @jwt_required()
    # def get(self, id_carrera):
    #     return carrera_schema.dump(Carrera.query.get_or_404(id_carrera))
    @jwt_required()
    def get(self, id_carrera):
        carrera = Carrera.query.get_or_404(id_carrera)

        newApuestas = []
        for apuesta in carrera.apuestas:
            apuesta.apostador = Usuario.query.get(apuesta.id_apostador).usuario
            newApuestas.append(apuesta)

        carrera.apuestas = newApuestas
        return carrera_schema.dump(carrera)

    @jwt_required()
    def put(self, id_carrera):
        carrera = Carrera.query.get_or_404(id_carrera)
        carrera.nombre_carrera = request.json.get("nombre", carrera.nombre_carrera)
        carrera.competidores = []
        suma_probabilidad = 0
        for item in request.json["competidores"]:
            probabilidad = float(item["probabilidad"])
            cuota = round((probabilidad / (1 - probabilidad)), 2)
            suma_probabilidad += probabilidad
            competidor = Competidor(
                nombre_competidor=item["competidor"],
                probabilidad=probabilidad,
                cuota=cuota,
                id_carrera=carrera.id,
            )
            carrera.competidores.append(competidor)

        if suma_probabilidad != 1:
            return "La sumatoria de las probabilidades es diferente de 1", 412

        db.session.commit()
        return carrera_schema.dump(carrera)

    @jwt_required()
    def delete(self, id_carrera):
        carrera = Carrera.query.get_or_404(id_carrera)
        db.session.delete(carrera)
        db.session.commit()
        return "", 204

