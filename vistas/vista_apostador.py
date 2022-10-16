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

class VistaApostador(Resource):
    @jwt_required()
    def get(self, id_apostador):
        """
        It returns the user (apostador) with the given id
        """
        return usuario_schema.dump(Usuario.query.get_or_404(id_apostador))
