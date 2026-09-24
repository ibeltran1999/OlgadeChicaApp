import unittest
from datetime import date

from flask import Flask

from app.domain.enums import ProcedenciaFilmina
from app.domain.filmina import Filmina
from app.presentation.controladores.controlador_filminas import (
    crear_controlador_filminas,
)


class RegistrarFilminaFalso:
    def __init__(self) -> None:
        self.ultima_filmina: Filmina | None = None

    def ejecutar(
        self,
        descripcion: str,
        fecha: date,
        procedencia: str,
    ) -> Filmina:
        self.ultima_filmina = Filmina(
            identificador="F001",
            descripcion=descripcion,
            fecha=fecha,
            procedencia=ProcedenciaFilmina(procedencia),
        )
        return self.ultima_filmina


class ControladorFilminasTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.gestor = RegistrarFilminaFalso()

        self.app = Flask(__name__)
        self.app.register_blueprint(crear_controlador_filminas(self.gestor))
        self.client = self.app.test_client()

    def test_crear_filmina(self) -> None:
        respuesta = self.client.post(
            "/filminas",
            json={
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

        self.assertIsNotNone(self.gestor.ultima_filmina)

    def test_mostrar_formulario_de_creacion_de_filminas(self) -> None:
        respuesta = self.client.get("/filminas/nueva")

        self.assertEqual(respuesta.status_code, 200)

        contenido = respuesta.get_data(as_text=True)

        self.assertIn("Registrar Filmina", contenido)
        self.assertIn('name="descripcion"', contenido)
        self.assertIn('name="fecha"', contenido)
        self.assertIn('name="precedencia"', contenido)
        self.assertIn("Guardar filmina", contenido)
