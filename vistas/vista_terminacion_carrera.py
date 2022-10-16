import sys
from datetime import datetime
from unicodedata import numeric
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from modelos import (
    db,
    Carrera,
    CompetidorSchema,
    Competidor
)
from modelos.modelo_transaccion import Transaccion
from modelos.modelo_usuario import Usuario

competidor_schema = CompetidorSchema()

class VistaTerminacionCarrera(Resource):
    def put(self, id_competidor):
        competidor = Competidor.query.get_or_404(id_competidor)
        competidor.es_ganador = True
        carrera = Carrera.query.get_or_404(competidor.id_carrera)
        carrera.abierta = False

        for apuesta in carrera.apuestas:
            if apuesta.id_competidor == competidor.id:
                apuesta.ganancia = apuesta.valor_apostado + (
                    apuesta.valor_apostado / competidor.cuota
                )
                nueva_transaccion = Transaccion(
                    id_usuario= apuesta.id_apostador,
                    valor= float(apuesta.ganancia),
                    tipo= "recarga",
                    fecha=datetime.now(),
                )
                db.session.add(nueva_transaccion)
            else:
                apuesta.ganancia = 0
            
            usuario = Usuario.query.get_or_404(apuesta.id_apostador)
            usuario.saldo = float(usuario.saldo) + float(apuesta.ganancia)    

        db.session.commit()
        return competidor_schema.dump(competidor)


