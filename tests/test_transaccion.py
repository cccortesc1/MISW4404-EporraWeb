import json
from unittest import TestCase
from app import app
from faker import Faker


class TestCarrera(TestCase):
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()

        usuario_1 = {
            "usuario": self.data_factory.name(),
            "contrasena": self.data_factory.word(),
            "perfil": "Apostador",
            "saldo": 100000,
            "correo": self.data_factory.ascii_email(),
            "medioPago": self.data_factory.credit_card_number(card_type='amex')
        }

        registro = self.client.post(
            "/signin",
            data=json.dumps(usuario_1),
            headers={"Content-Type": "application/json"},
        )

        respuesta_registro = json.loads(registro.get_data())

        self.token = respuesta_registro["token"]
        self.usuario_code = respuesta_registro["id"]

    def test_crear_transaccion(self):
        nueva_transaccion = {
            "tipo": "recarga",
            "valor": "100000",
        }

        endpoint_transacciones = "/transacciones/{}".format(str(self.usuario_code))
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_transaccion = self.client.post(
            endpoint_transacciones, data=json.dumps(nueva_transaccion), headers=headers
        )

        self.assertEqual(solicitud_nueva_transaccion.status_code, 200)

    def test_crear_transaccion_sin_tipo(self):

        nueva_transaccion = {
            "fecha": "2021-09-07",
            "valor": "100000",
        }

        endpoint_transacciones = "//transacciones/{}".format(str(self.usuario_code))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_transaccion = self.client.post(
            endpoint_transacciones, data=json.dumps(nueva_transaccion), headers=headers
        )

        self.assertEqual(solicitud_nueva_transaccion.status_code, 404)

    def test_crear_transaccion_sin_valor(self):

        nueva_transaccion = {
            "fecha": "2021-09-07",
            "tipo": "recarga",
        }

        endpoint_transacciones = "/transacciones/{}".format(str(self.usuario_code))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.token),
        }

        solicitud_nueva_transaccion = self.client.post(
            endpoint_transacciones, data=json.dumps(nueva_transaccion), headers=headers
        )

        self.assertEqual(solicitud_nueva_transaccion.status_code, 400)
