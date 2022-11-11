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
    Usuario,
    UsuarioSchema,
    Carrera,
    CarreraSchema,
    CompetidorSchema,
    Competidor,
    ReporteSchema,
    Transaccion,
    TransaccionSchema,
    TipoCarreraSchema,
)
from modelos.modelos import TipoCarrera

apuesta_schema = ApuestaSchema()
carrera_schema = CarreraSchema()
competidor_schema = CompetidorSchema()
usuario_schema = UsuarioSchema()
reporte_schema = ReporteSchema()
transaccion_schema = TransaccionSchema()
tipo_carrera_schema = TipoCarreraSchema()


class VistaSignIn(Resource):
    def post(self):
        stored_user = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"]
        ).first()
        if stored_user is not None:
            return "El usuario ya existe", 412

        nuevo_usuario = Usuario(
            usuario=request.json["usuario"],
            contrasena=request.json["contrasena"],
            perfil="Apostador",
            saldo=numeric("0"),
            correo=request.json["correo"],
            medioPago=request.json["medioPago"],
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
            "medioPago": nuevo_usuario.medioPago,
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
                "medioPago": usuario.medioPago,
            }


class VistaCarrerasUsuario(Resource):
    @jwt_required()
    def post(self, id_usuario):
        stored_carrera = Carrera.query.filter(
            Carrera.nombre_carrera == request.json["nombre"]
        ).first()
        if stored_carrera is not None:
            return "La carrera ya existe", 412

        nueva_carrera = Carrera(
            nombre_carrera=request.json["nombre"], tipo_carrera=request.json["nombre"]
        )

        probabilidad_total = 0
        for competidor in request.json["competidores"]:
            competidor["probabilidad"] = float(competidor["probabilidad"])
            probabilidad_total += competidor["probabilidad"]
            cuota = round(
                (competidor["probabilidad"] / (1 - competidor["probabilidad"])), 2
            )
            competidor = Competidor(
                nombre_competidor=competidor["competidor"],
                probabilidad=competidor["probabilidad"],
                cuota=cuota,
                id_carrera=nueva_carrera.id,
            )
            nueva_carrera.competidores.append(competidor)

        if probabilidad_total != 1:
            return "La suma de las probabilidades debe ser 1", 412

        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.carreras.append(nueva_carrera)

        try:
            db.session.commit()
        except IntegrityError:
            value_type, value, traceback = sys.exc_info()
            print("> %s: %s: %s" % (value_type, value, traceback))
            db.session.rollback()
            return "El usuario ya tiene un carrera con dicho nombre", 409

        return carrera_schema.dump(nueva_carrera)

    @jwt_required()
    def get(self, id_usuario):
        carreras = Carrera.query.all()  # usuario.carreras
        newCarreras = []
        for carrera in carreras:
            new_apuestas = []
            for apuesta in carrera.apuestas:
                apuesta.apostador = Usuario.query.get(apuesta.id_apostador).usuario
                new_apuestas.append(apuesta)

            carrera.apuestas = new_apuestas
            newCarreras.append(carrera)

        return [carrera_schema.dump(carrera) for carrera in newCarreras]


class VistaCarrera(Resource):
    # @jwt_required()
    # def get(self, id_carrera):
    #     return carrera_schema.dump(Carrera.query.get_or_404(id_carrera))
    @jwt_required()
    def get(self, id_carrera):
        carrera = Carrera.query.get_or_404(id_carrera)

        newApuestas = []
        for apuesta in carrera.apuestas:
            apuesta.apostador = Usuario.query.get(apuesta.id_apostador).usuario
            newApuestas.append(apuesta)

        carrera.apuestas = newApuestas
        return carrera_schema.dump(carrera)

    @jwt_required()
    def put(self, id_carrera):
        carrera = Carrera.query.get_or_404(id_carrera)
        carrera.nombre_carrera = request.json.get("nombre", carrera.nombre_carrera)
        carrera.competidores = []
        suma_probabilidad = 0
        for item in request.json["competidores"]:
            probabilidad = float(item["probabilidad"])
            cuota = round((probabilidad / (1 - probabilidad)), 2)
            suma_probabilidad += probabilidad
            competidor = Competidor(
                nombre_competidor=item["competidor"],
                probabilidad=probabilidad,
                cuota=cuota,
                id_carrera=carrera.id,
            )
            carrera.competidores.append(competidor)

        if suma_probabilidad != 1:
            return "La sumatoria de las probabilidades es diferente de 1", 412

        db.session.commit()
        return carrera_schema.dump(carrera)

    @jwt_required()
    def delete(self, id_carrera):
        carrera = Carrera.query.get_or_404(id_carrera)
        db.session.delete(carrera)
        db.session.commit()
        return "", 204


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
            id_usuario=nueva_apuesta.id_apostador,
            valor=nueva_apuesta.ganancia,
            tipo="retiro",
            fecha=datetime.now(),
        )
        db.session.add(nueva_transaccion)

        usuario = Usuario.query.get_or_404(nueva_apuesta.id_apostador)
        usuario = Usuario.query.get_or_404(nueva_apuesta.id_apostador)
        usuario.saldo = float(usuario.saldo) + float(nueva_apuesta.ganancia)

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
                    id_usuario=apuesta.id_apostador,
                    valor=float(apuesta.ganancia),
                    tipo="recarga",
                    fecha=datetime.now(),
                )
                db.session.add(nueva_transaccion)
            else:
                apuesta.ganancia = 0

            usuario = Usuario.query.get_or_404(apuesta.id_apostador)
            usuario.saldo = float(usuario.saldo) + float(apuesta.ganancia)

        db.session.commit()
        return competidor_schema.dump(competidor)


class VistaReporte(Resource):
    @jwt_required()
    def get(self, id_carrera):
        carreraReporte = Carrera.query.get_or_404(id_carrera)
        ganancia_casa_final = 0

        newApuestas = []
        for apuesta in carreraReporte.apuestas:
            apuesta.apostador = Usuario.query.get(apuesta.id_apostador).usuario
            newApuestas.append(apuesta)
            ganancia_casa_final = (
                ganancia_casa_final + apuesta.valor_apostado - apuesta.ganancia
            )

        carreraReporte.apuestas = newApuestas
        reporte = dict(carrera=carreraReporte, ganancia_casa=ganancia_casa_final)
        schema = ReporteSchema()
        return schema.dump(reporte)


class VistaApostadores(Resource):
    @jwt_required()
    def get(self):
        """
        It returns all the users that have the perfil "apostador"
        """
        apostadores = Usuario.query.filter_by(perfil="Apostador").all()
        return [usuario_schema.dump(apostador) for apostador in apostadores]


class VistaTiposCarreras(Resource):
    @jwt_required()
    def get(self):
        tiposCarreras = TipoCarrera.query.all()
        return [
            tipo_carrera_schema.dump(tipo_carrera) for tipo_carrera in tiposCarreras
        ]


class VistaApostador(Resource):
    @jwt_required()
    def get(self, id_apostador):
        """
        It returns the user (apostador) with the given id
        """
        return usuario_schema.dump(Usuario.query.get_or_404(id_apostador))


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
        usuario.saldo = (
            float(usuario.saldo) + float(request.json["valor"]) * suma_o_resta_saldo
        )
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
