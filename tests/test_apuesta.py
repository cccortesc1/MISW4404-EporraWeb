import json
from unittest import TestCase

from faker import Faker
from faker.generator import random

from app import app


class TestApuesta(TestCase):
    def setUp(self):
        # Reset db
        self.client = app.test_client()
        self.client.get("/reset")

        self.data_factory = Faker()

        nuevo_usuario = {
            "usuario": "apostador1",
            "contrasena": self.data_factory.word(),
            "perfil": "Apostador",
            "saldo": 100000,
            "correo": self.data_factory.ascii_email(),
            "medioPago": self.data_factory.credit_card_number(card_type="amex"),
        }
        solicitud_nuevo_usuario = self.client.post(
            "/signin",
            data=json.dumps(nuevo_usuario),
            headers={"Content-Type": "application/json"},
        )

        nuevo_usuario2 = {
            "usuario": "apostador2",
            "contrasena": self.data_factory.word(),
            "perfil": "Apostador",
            "saldo": 100000,
            "correo": self.data_factory.ascii_email(),
            "medioPago": self.data_factory.credit_card_number(card_type="amex"),
        }

        solicitud_nuevo_usuario = self.client.post(
            "/signin",
            data=json.dumps(nuevo_usuario2),
            headers={"Content-Type": "application/json"},
        )

        respuesta_al_crear_usuario = json.loads(solicitud_nuevo_usuario.get_data())

        self.token = respuesta_al_crear_usuario["token"]
        self.usuario_code = respuesta_al_crear_usuario["id"]

    def test_crear_apuesta(self):
        nueva_carrera = {
            "nombre": "Carrera5",
            "competidores": [
                {"probabilidad": 0.6, "competidor": "Lorem ipsum"},
                {
                    "probabilidad": 0.2,  # round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name(),
                },
                {
                    "probabilidad": 0.2,  # round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name(),
                },
            ],
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_carrera = self.client.post(
            endpoint_carreras, data=json.dumps(nueva_carrera), headers=headers
        )

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = [
            x
            for x in respuesta_al_crear_carrera["competidores"]
            if x["nombre_competidor"] == "Lorem ipsum"
        ][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": 1,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        endpoint_apuestas = "/apuestas/{}".format(str(self.usuario_code))
        solicitud_nueva_apuesta = self.client.post(
            endpoint_apuestas, data=json.dumps(nueva_apuesta), headers=headers
        )
        respuesta = solicitud_nueva_apuesta.get_data()
        respuesta_al_crear_apuesta = json.loads(respuesta)
        id_apostador = respuesta_al_crear_apuesta["id_apostador"]

        self.assertEqual(
            solicitud_nueva_apuesta.status_code, 200, "Mensaje {0}".format(respuesta)
        )
        self.assertEqual(id_apostador, 1)

    def test_editar_apuesta(self):
        nueva_carrera = {
            "nombre": "Carrera7",
            "competidores": [
                {"probabilidad": 0.6, "competidor": "Damian Corral"},
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
            ],
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_carrera = self.client.post(
            endpoint_carreras, data=json.dumps(nueva_carrera), headers=headers
        )

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = [
            x
            for x in respuesta_al_crear_carrera["competidores"]
            if x["nombre_competidor"] == "Damian Corral"
        ][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": 1,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        endpoint_apuestas = "/apuestas/{}".format(str(self.usuario_code))

        solicitud_nueva_apuesta = self.client.post(
            endpoint_apuestas, data=json.dumps(nueva_apuesta), headers=headers
        )

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta.get_data())
        id_apostador_antes = respuesta_al_crear_apuesta["id_apostador"]
        id_apuesta = respuesta_al_crear_apuesta["id"]

        endpoint_apuesta = "/apuesta/{}".format(str(id_apuesta))

        apuesta_editada = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": 2,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        solicitud_editar_apuesta = self.client.put(
            endpoint_apuesta, data=json.dumps(apuesta_editada), headers=headers
        )

        respuesta_al_editar_apuesta = json.loads(solicitud_editar_apuesta.get_data())
        id_apostador_despues = respuesta_al_editar_apuesta["id_apostador"]

        self.assertEqual(solicitud_nueva_apuesta.status_code, 200)
        self.assertNotEqual(id_apostador_antes, id_apostador_despues)

    def test_obtener_apuesta_por_id(self):
        nueva_carrera = {
            "nombre": "Carrera8",
            "competidores": [
                {"probabilidad": 0.6, "competidor": "Paz Manrique"},
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
            ],
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_carrera = self.client.post(
            endpoint_carreras, data=json.dumps(nueva_carrera), headers=headers
        )

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = [
            x
            for x in respuesta_al_crear_carrera["competidores"]
            if x["nombre_competidor"] == "Paz Manrique"
        ][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": 1,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        endpoint_apuestas = "/apuestas/{}".format(str(self.usuario_code))

        solicitud_nueva_apuesta = self.client.post(
            endpoint_apuestas, data=json.dumps(nueva_apuesta), headers=headers
        )

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta.get_data())
        id_apuesta = respuesta_al_crear_apuesta["id"]

        endpoint_apuesta = "/apuesta/{}".format(str(id_apuesta))

        solicitud_consultar_apuesta_por_id = self.client.get(
            endpoint_apuesta, headers=headers
        )
        apuesta_obtenida = json.loads(solicitud_consultar_apuesta_por_id.get_data())

        self.assertEqual(solicitud_consultar_apuesta_por_id.status_code, 200)
        self.assertEqual(apuesta_obtenida["id_apostador"], 1)

    def test_obtener_apuesta_por_id_administrador(self):
        nueva_carrera = {
            "nombre": "Carrera9",
            "competidores": [
                {"probabilidad": 0.6, "competidor": "Paz Manrique"},
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
            ],
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_carrera = self.client.post(
            endpoint_carreras, data=json.dumps(nueva_carrera), headers=headers
        )

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = [
            x
            for x in respuesta_al_crear_carrera["competidores"]
            if x["nombre_competidor"] == "Paz Manrique"
        ][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": 1,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        endpoint_apuestas = "/apuestas/{}".format(str(self.usuario_code))

        solicitud_nueva_apuesta = self.client.post(
            endpoint_apuestas, data=json.dumps(nueva_apuesta), headers=headers
        )

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta.get_data())
        id_apuesta = respuesta_al_crear_apuesta["id"]

        endpoint_apuesta = "/apuesta/{}".format(str(id_apuesta))

        solicitud_consultar_apuesta_por_id = self.client.get(
            endpoint_apuesta, headers=headers
        )
        apuesta_obtenida = json.loads(solicitud_consultar_apuesta_por_id.get_data())

        self.assertEqual(solicitud_consultar_apuesta_por_id.status_code, 200)
        self.assertEqual(apuesta_obtenida["id_apostador"], 1)

    def test_obtener_apuestas(self):
        nueva_carrera = {
            "nombre": "Carrera9",
            "competidores": [
                {"probabilidad": 0.6, "competidor": "Zakaria Vila"},
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
            ],
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_carrera = self.client.post(
            endpoint_carreras, data=json.dumps(nueva_carrera), headers=headers
        )

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = [
            x
            for x in respuesta_al_crear_carrera["competidores"]
            if x["nombre_competidor"] == "Zakaria Vila"
        ][0]["id"]

        nueva_apuesta1 = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": self.usuario_code,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        endpoint_apuestas = "/apuestas/{}".format(str(self.usuario_code))

        solicitud_nueva_apuesta1 = self.client.post(
            endpoint_apuestas, data=json.dumps(nueva_apuesta1), headers=headers
        )

        solicitud_consulta_apuestas_antes = self.client.get(
            endpoint_apuestas, headers=headers
        )
        total_apuestas_antes = len(
            json.loads(solicitud_consulta_apuestas_antes.get_data())
        )

        nueva_apuesta2 = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": self.usuario_code,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        solicitud_nueva_apuesta2 = self.client.post(
            endpoint_apuestas, data=json.dumps(nueva_apuesta2), headers=headers
        )

        solicitud_consulta_apuestas_despues = self.client.get(
            endpoint_apuestas, headers=headers
        )
        total_apuestas_despues = len(
            json.loads(solicitud_consulta_apuestas_despues.get_data())
        )

        self.assertEqual(solicitud_consulta_apuestas_despues.status_code, 200)
        self.assertGreater(total_apuestas_despues, total_apuestas_antes)

    def test_eliminar_apuesta(self):
        nueva_carrera = {
            "nombre": "Carrera10",
            "competidores": [
                {"probabilidad": 0.6, "competidor": "Eduardo Tejera"},
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
                {
                    "probabilidad": 0.2,
                    "competidor": self.data_factory.name(),
                },
            ],
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_carrera = self.client.post(
            endpoint_carreras, data=json.dumps(nueva_carrera), headers=headers
        )

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = [
            x
            for x in respuesta_al_crear_carrera["competidores"]
            if x["nombre_competidor"] == "Eduardo Tejera"
        ][0]["id"]

        nueva_apuesta1 = {
            "valor_apostado": random.uniform(100, 500000),
            "id_apostador": self.usuario_code,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera,
        }

        endpoint_apuestas = "/apuestas/{}".format(str(self.usuario_code))

        solicitud_nueva_apuesta1 = self.client.post(
            endpoint_apuestas, data=json.dumps(nueva_apuesta1), headers=headers
        )

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta1.get_data())
        id_apuesta = respuesta_al_crear_apuesta["id"]
        solicitud_consulta_apuestas_antes = self.client.get(
            endpoint_apuestas, headers=headers
        )

        total_apuestas_antes = len(
            json.loads(solicitud_consulta_apuestas_antes.get_data())
        )

        endpoint_apuesta = "/apuesta/{}".format(str(id_apuesta))

        solicitud_eliminar_apuesta = self.client.delete(
            endpoint_apuesta, headers=headers
        )
        solicitud_consulta_apuestas_despues = self.client.get(
            endpoint_apuestas, headers=headers
        )
        total_apuestas_despues = len(
            json.loads(solicitud_consulta_apuestas_despues.get_data())
        )

        self.assertLess(total_apuestas_despues, total_apuestas_antes)
        self.assertEqual(solicitud_eliminar_apuesta.status_code, 204)
