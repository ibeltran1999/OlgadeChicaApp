import unittest

from flask import Flask

from app.domain.tag import Tag
from app.presentation.controladores.controlador_tags import crear_controlador_tags


class RegistrarTagFalso:
    def __init__(self) -> None:
        self.ultimo_tag: Tag | None = None

    def ejecutar(self, identificador: str, nombre: str) -> Tag:
        self.ultimo_tag = Tag(identificador=identificador, nombre=nombre)
        return self.ultimo_tag


class ControladorTagsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.gestor = RegistrarTagFalso()
        self.app = Flask(__name__)
        self.app.register_blueprint(crear_controlador_tags(self.gestor))
        self.client = self.app.test_client()

    def test_mostrar_formulario_de_creacion_de_tags(self) -> None:
        respuesta = self.client.get("/tags/nueva")

        self.assertEqual(respuesta.status_code, 200)
        contenido = respuesta.get_data(as_text=True)
        self.assertIn("Crear tag", contenido)
        self.assertIn('name="identificador"', contenido)
        self.assertIn('name="nombre"', contenido)

    def test_crear_tag_desde_formulario(self) -> None:
        respuesta = self.client.post(
            "/tags",
            data={
                "identificador": "T001",
                "nombre": "Arquitectura",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Tag creado correctamente", respuesta.get_data(as_text=True))
        self.assertIsNotNone(self.gestor.ultimo_tag)
        assert self.gestor.ultimo_tag is not None
        self.assertEqual(self.gestor.ultimo_tag.identificador, "T001")
        self.assertEqual(self.gestor.ultimo_tag.nombre, "Arquitectura")

    def test_crear_tag_desde_json(self) -> None:
        respuesta = self.client.post(
            "/tags",
            json={
                "identificador": "T002",
                "nombre": "Fachada",
            },
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(
            respuesta.get_json(),
            {"identificador": "T002", "nombre": "Fachada"},
        )