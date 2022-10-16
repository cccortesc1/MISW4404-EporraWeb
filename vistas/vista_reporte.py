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
    ReporteSchema
)

reporte_schema = ReporteSchema()

class VistaReporte(Resource):
    @jwt_required()
    def get(self, id_carrera):
        carreraReporte = Carrera.query.get_or_404(id_carrera)
        ganancia_casa_final = 0

        newApuestas = []
        for apuesta in carreraReporte.apuestas:
            apuesta.apostador = Usuario.query.get(apuesta.id_apostador).usuario
            newApuestas.append(apuesta)
            ganancia_casa_final = (
                ganancia_casa_final + apuesta.valor_apostado - apuesta.ganancia
            )

        carreraReporte.apuestas = newApuestas
        reporte = dict(carrera=carreraReporte, ganancia_casa=ganancia_casa_final)
        schema = ReporteSchema()
        return schema.dump(reporte)
