import unittest
from datetime import date

from flask import Flask

from app.domain.enums import ProcedenciaFilmina
from app.domain.filmina import Filmina
from app.presentation.controladores.controlador_filminas import (
    crear_controlador_filminas,
)


class RepositorioFilminasFalso:
    def __init__(self) -> None:
        self.filminas: dict[str, Filmina] = {}

    def guardar(self, filmina: Filmina) -> None:
        self.filminas[filmina.identificador] = filmina

    def obtener_por_identificador(
        self,
        identificador: str,
    ) -> Filmina | None:
        return self.filminas.get(identificador)


class ControladorFilminasTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.repositorio = RepositorioFilminasFalso()

        self.app = Flask(__name__)
        self.app.register_blueprint(
            crear_controlador_filminas(self.repositorio)
        )
        self.client = self.app.test_client()

    def test_crear_filmina(self) -> None:
        respuesta = self.client.post(
            "/filminas",
            json={
                "identificador": "F001",
                "descripcion": "Filmina de prueba",
                "fecha": "2024-01-15",
                "procedencia": "BLAA",
            },
        )

        self.assertEqual(respuesta.status_code, 201)

        datos = respuesta.get_json()

        self.assertIsNotNone(datos)
        assert datos is not None

        self.assertEqual(datos["identificador"], "F001")
        self.assertEqual(datos["descripcion"], "Filmina de prueba")
        self.assertEqual(datos["fecha"], "2024-01-15")
        self.assertEqual(datos["procedencia"], "BLAA")

        self.assertIn("F001", self.repositorio.filminas)

    def test_obtener_filmina(self) -> None:
        filmina = Filmina(
            identificador="F001",
            descripcion="Filmina de prueba",
            fecha=date(2024, 1, 15),
            procedencia=ProcedenciaFilmina.BLAA,
        )
        self.repositorio.guardar(filmina)

        respuesta = self.client.get("/filminas/F001")

        self.assertEqual(respuesta.status_code, 200)

        datos = respuesta.get_json()

        self.assertIsNotNone(datos)
        assert datos is not None

        self.assertEqual(datos["identificador"], "F001")
        self.assertEqual(datos["descripcion"], "Filmina de prueba")

    def test_obtener_filmina_inexistente(self) -> None:
        respuesta = self.client.get("/filminas/NO-EXISTE")

        self.assertEqual(respuesta.status_code, 404)
