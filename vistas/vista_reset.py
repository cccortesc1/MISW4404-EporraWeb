import sys
from datetime import datetime
from unicodedata import numeric
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from modelos import (
    db,
    Usuario
)

class VistaReset(Resource):
    def get(self):
        db.drop_all()
        db.create_all()

        # Create admin user
        admin = Usuario(
            usuario="admin",
            contrasena="admin",
            perfil="administrador",
        )
        db.session.add(admin)

