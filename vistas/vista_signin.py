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
    UsuarioSchema
)

usuario_schema = UsuarioSchema()

class VistaSignIn(Resource):
    def post(self):
        nuevo_usuario = Usuario(
            usuario=request.json["usuario"],
            contrasena=request.json["contrasena"],
            perfil="Apostador",
            saldo=numeric("0"),
            correo = request.json["correo"],
            medioPago = request.json["medioPago"]
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        token_de_acceso = create_access_token(identity=nuevo_usuario.id)
        return {
            "mensaje": "usuario creado exitosamente",
            "token": token_de_acceso,
            "id": nuevo_usuario.id,
            "perfil": nuevo_usuario.perfil,
            "correo": nuevo_usuario.correo,
            "medioPago": nuevo_usuario.medioPago
        }

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return "", 204

