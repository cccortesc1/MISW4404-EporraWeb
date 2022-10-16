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

class VistaApostadores(Resource):
    @jwt_required()
    def get(self):
        """
        It returns all the users that have the perfil "apostador"
        """
        apostadores = Usuario.query.filter_by(perfil="Apostador").all()
        return [usuario_schema.dump(apostador) for apostador in apostadores]

