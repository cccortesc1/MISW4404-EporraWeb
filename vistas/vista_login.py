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
)

class VistaLogIn(Resource):
    def post(self):
        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"],
            Usuario.contrasena == request.json["contrasena"],
        ).first()
        db.session.commit()
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            return {
                "mensaje": "Inicio de sesión exitoso",
                "token": token_de_acceso,
                "perfil": usuario.perfil,
                "saldo": usuario.saldo,
                "correo": usuario.correo,
                "medioPago": usuario.medioPago
            }

