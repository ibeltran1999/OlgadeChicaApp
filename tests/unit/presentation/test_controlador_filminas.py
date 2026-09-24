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
        for tag in tags or []:
            self.ultima_filmina.agregar_tag(tag)
        return self.ultima_filmina


class RepositorioTagsFalso:
    def __init__(self, tags):
        self.tags = {tag.identificador: tag for tag in tags}

    def listar(self):
        return list(self.tags.values())

    def obtener_por_identificador(self, identificador):
        return self.tags.get(identificador)


class ControladorFilminasTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.gestor = RegistrarFilminaFalso()
        self.tags = [
            Tag(identificador="T001", nombre="Arquitectura"),
            Tag(identificador="T002", nombre="Fachada"),
            Tag(identificador="T003", nombre="Patrimonio"),
        ]
        self.repositorio_tags = RepositorioTagsFalso(self.tags)

        self.app = Flask(__name__)
        self.app.register_blueprint(
            crear_controlador_filminas(self.gestor, self.repositorio_tags)
        )
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
        self.assertIn('value="T001"', contenido)
        self.assertIn("Arquitectura", contenido)
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
                ("tag_identificador", "T002"),
                ("tag_identificador", "T003"),
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

    def test_ignorar_tag_repetido_seleccionado_en_el_formulario(self) -> None:
        respuesta = self.client.post(
            "/filminas",
            data=MultiDict([
                ("descripcion", "Filmina clasificada"),
                ("fecha", "2026-09-01"),
                ("procedencia", "BLAA"),
                ("tag_identificador", "T001"),
                ("tag_identificador", "T001"),
            ]),
            content_type="multipart/form-data",
        )

        self.assertEqual(respuesta.status_code, 200)
        assert self.gestor.ultima_filmina is not None
        self.assertEqual(len(self.gestor.ultima_filmina.tags), 1)
        self.assertEqual(self.gestor.ultima_filmina.tags[0].identificador, "T001")
