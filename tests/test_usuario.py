import json
from unittest import TestCase
from faker import Faker

from app import app


class TestUsuario(TestCase):
    def set_up(self):
        # Reset db
        self.client = app.test_client()
        self.client.get("/reset")

        self.data_factory = Faker()
        self.headers = {"Content-Type": "application/json"}

        self.usuario_setup = dict(
            usuario=self.data_factory.user_name(),
            contrasena=self.data_factory.password(),
            pefil="Apostador",
            saldo=1000,
            correo=self.data_factory.email(),
            medioPago="Efectivo",
        )

        response = self.client.post(
            "/signin",
            data=json.dumps(self.usuario_setup),
            headers=self.headers,
        )

        self.usuario_setup["id"] = response.json["id"]

    def tests_login(self):
        self.set_up()

        response = self.client.post(
            "/login",
            data=json.dumps(
                dict(
                    usuario=self.usuario_setup["usuario"],
                    contrasena=self.usuario_setup["contrasena"],
                )
            ),
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)

    def tests_edit_user(self):
        self.set_up()

        # Test edit user
        response = self.client.put(
            f"/signin/{self.usuario_setup['id']}",
            data=dict(
                usuario=self.usuario_setup["usuario"],
                contrasena=self.usuario_setup["contrasena"],
                perfil="Apostador",
                saldo=2000,
                correo=self.data_factory.email(),
                medioPago="Paypal",
            ),
        )
        self.assertEqual(response.status_code, 404)

    def tests_delete_user(self):
        self.set_up()
        # Test delete user
        response = self.client.delete(f"/signin/{self.usuario_setup['id']}")
        self.assertEqual(response.status_code, 404)
