import sys
from datetime import datetime
from unicodedata import numeric
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from modelos import (
    db,
    TipoCarrera,
    TipoCarreraSchema
)

tipo_carrera_schema = TipoCarreraSchema()

class VistaTiposCarreras(Resource):
    @jwt_required()
    def get(self):
        tiposCarreras = TipoCarrera.query.all()
        return [tipo_carrera_schema.dump(tipo_carrera) for tipo_carrera in tiposCarreras]
