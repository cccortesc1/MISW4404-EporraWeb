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
)
from modelos.modelo_transaccion import Transaccion
from modelos.modelo_usuario import Usuario

apuesta_schema = ApuestaSchema()

class VistaApuestas(Resource):

    @jwt_required()
    def post(self, id_usuario):
        nueva_apuesta = Apuesta(
            valor_apostado=request.json["valor_apostado"],
            id_apostador=request.json["id_apostador"],
            id_competidor=request.json["id_competidor"],
            id_carrera=request.json["id_carrera"],
        )
        db.session.add(nueva_apuesta)

        nueva_transaccion = Transaccion(
                    id_usuario= request.json["id_apostador"],
                    valor = request.json["valor_apostado"],
                    tipo= "retiro",
                    fecha=datetime.now(),
                )
        db.session.add(nueva_transaccion)

        usuario = Usuario.query.get_or_404(nueva_apuesta.id_apostador)    
        usuario.saldo = float(usuario.saldo) - float(request.json["valor_apostado"])    

        db.session.commit()
        return apuesta_schema.dump(nueva_apuesta)

    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        if usuario.perfil == "administrador":
            apuestas = Apuesta.query.all()
            newApuestas = []
            for apuesta in apuestas:
                apuesta.apostador = Usuario.query.get_or_404(
                    apuesta.id_apostador
                ).usuario
                newApuestas.append(apuesta)
            return [apuesta_schema.dump(apuesta) for apuesta in newApuestas]
        else:
            apuestas = Apuesta.query.filter_by(id_apostador=id_usuario).all()
            return [apuesta_schema.dump(apuesta) for apuesta in apuestas]