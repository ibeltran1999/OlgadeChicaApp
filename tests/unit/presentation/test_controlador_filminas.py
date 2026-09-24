import unittest
from datetime import date
from io import BytesIO
from flask import Flask
from werkzeug.datastructures import MultiDict

from app.domain.enums import ProcedenciaFilmina
from app.domain.filmina import Filmina
from app.domain.tag import Tag
from app.presentation.controladores.controlador_filminas import (
    crear_controlador_filminas,
)


class RegistrarFilminaFalso:
    def __init__(self) -> None:
        self.ultima_filmina: Filmina | None = None
        self.ultimo_archivo: None

    def ejecutar(
        self,
        descripcion: str,
        fecha: date,
        procedencia: str,
        archivo=None,
        tags=None,
    ):
        self.ultimo_archivo = archivo
        self.ultima_filmina = Filmina(
            identificador="F001",
            descripcion=descripcion,
            fecha=fecha,
            procedencia=ProcedenciaFilmina(procedencia),
        )
        for datos_tag in tags or []:
            self.ultima_filmina.agregar_tag(
                Tag(
                    identificador=datos_tag["identificador"],
                    nombre=datos_tag["nombre"],
                )
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
        self.assertIn('name="procedencia"', contenido)
        self.assertIn("Guardar filmina", contenido)

    def test_crear_filmina_con_archivo(self) -> None:
        respuesta = self.client.post(
            "/filminas",
            data={
                "descripcion": "Filmina con archivo",
                "fecha": "2026-09-01",
                "procedencia": "BLAA",
                "archivo": (BytesIO(b"contenido de prueba"), "filmina.jpg"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(respuesta.status_code, 200)

        contenido = respuesta.get_data(as_text=True)

        self.assertIn(
            "Filmina creada correctamente",
            contenido,
        )

    def test_crear_filmina_con_tres_tags_desde_formulario(self) -> None:
        respuesta = self.client.post(
            "/filminas",
            data=MultiDict([
                ("descripcion", "Filmina clasificada"),
                ("fecha", "2026-09-01"),
                ("procedencia", "BLAA"),
                ("tag_identificador", "T001"),
                ("tag_nombre", "Arquitectura"),
                ("tag_identificador", "T002"),
                ("tag_nombre", "Fachada"),
                ("tag_identificador", "T003"),
                ("tag_nombre", "Patrimonio"),
            ]),
            content_type="multipart/form-data",
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIsNotNone(self.gestor.ultima_filmina)
        assert self.gestor.ultima_filmina is not None
        self.assertEqual(len(self.gestor.ultima_filmina.tags), 3)
        self.assertEqual(
            [tag.identificador for tag in self.gestor.ultima_filmina.tags],
            ["T001", "T002", "T003"],
        )
