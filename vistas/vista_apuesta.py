import sys
from datetime import datetime
from unicodedata import numeric
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from modelos import (
    db,
    Apuesta,
    ApuestaSchema,
    Usuario
)

apuesta_schema = ApuestaSchema()

class VistaApuesta(Resource):
    @jwt_required()
    def get(self, id_apuesta):
        return apuesta_schema.dump(Apuesta.query.get_or_404(id_apuesta))

    @jwt_required()
    def put(self, id_apuesta):
        apuesta = Apuesta.query.get_or_404(id_apuesta)
        apuesta.valor_apostado = request.json.get(
            "valor_apostado", apuesta.valor_apostado
        )
        apuesta.id_apostador = request.json.get("id_apostador", apuesta.id_apostador)
        apostador = Usuario.query.get(apuesta.id_apostador)
        if apostador.saldo < apuesta.valor_apostado:
            return "No puede apostar esa cantidad, su saldo actual es " + str(apostador.saldo), 412
        apuesta.id_competidor = request.json.get("id_competidor", apuesta.id_competidor)
        apuesta.id_carrera = request.json.get("id_carrera", apuesta.id_carrera)
        db.session.commit()

        return apuesta_schema.dump(apuesta)

    @jwt_required()
    def delete(self, id_apuesta):
        apuesta = Apuesta.query.get_or_404(id_apuesta)
        db.session.delete(apuesta)
        db.session.commit()
        return "", 204


