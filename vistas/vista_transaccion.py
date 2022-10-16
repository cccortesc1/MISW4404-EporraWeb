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
    Transaccion,
    TransaccionSchema
)

transaccion_schema = TransaccionSchema()

class VistaTransaccion(Resource):
    @jwt_required()
    def post(self, id_usuario):
        if not request.json.get("valor") or not request.json.get("tipo"):
            return {"error": "Faltan datos"}, 400

        if not Usuario.query.get_or_404(id_usuario):
            return "El usuario no existe", 404

        if request.json["tipo"] not in ["recarga", "retiro"]:
            return "El tipo de transaccion no es valido", 400

        if int(request.json["valor"]) < 0:
            return "El valor de la recarga o retiro debe ser positivo", 400

        nueva_transaccion = Transaccion(
            id_usuario=id_usuario,
            valor=request.json["valor"],
            tipo=request.json["tipo"],
            fecha=datetime.now(),
        )

        suma_o_resta_saldo = 1 if request.json["tipo"] == "recarga" else -1

        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.saldo = float(usuario.saldo) + float(request.json["valor"]) * suma_o_resta_saldo
        db.session.add(nueva_transaccion)
        db.session.commit()
        return transaccion_schema.dump(nueva_transaccion)

    @jwt_required()
    def get(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        if usuario.perfil == "administrador":
            transacciones = Transaccion.query.all()
            return [
                transaccion_schema.dump(transaccion) for transaccion in transacciones
            ]
        else:
            transacciones = Transaccion.query.filter_by(id_usuario=id_usuario).all()
            return [
                transaccion_schema.dump(transaccion) for transaccion in transacciones
            ]
