import unittest
from datetime import date
from pathlib import Path
import tempfile

from io import BytesIO

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask

from app.application.registrar_filmina import RegistrarFilmina
from app.persistence.modelos import Base
from app.persistence.repositorio_filminas import (
    RepositorioFilminasSQLAlchemy,
)
from app.persistence.almacenamiento_archivos_local import AlmacenamientoArchivosLocal
from app.presentation.controladores.controlador_filminas import (
    crear_controlador_filminas,
)


class GeneradorIdentificadoresFalso:
    def generar_identificador_filmina(self) -> str:
        return "F001"


class FilminasFunctionalTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.directorio_temporal = tempfile.TemporaryDirectory()
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        session_factory = sessionmaker(bind=engine)
        session = session_factory()

        repositorio = RepositorioFilminasSQLAlchemy(session)
        generador = GeneradorIdentificadoresFalso()
        almacenamiento = AlmacenamientoArchivosLocal(self.directorio_temporal.name)
        gestor = RegistrarFilmina(repositorio, generador, almacenamiento)

        self.app = Flask(__name__)
        self.app.register_blueprint(crear_controlador_filminas(gestor))
        self.client = self.app.test_client()
        self.session = session

    def tearDown(self) -> None:
        self.session.close()
        self.directorio_temporal.cleanup()

    def test_crear_filmina_desde_formulario_y_persistirla(self) -> None:
        respuesta = self.client.post(
            "/filminas",
            data={
                "descripcion": "Filmina funcional",
                "fecha": "2024-01-15",
                "procedencia": "BLAA",
            },
            follow_redirects=True,
        )

        self.assertEqual(respuesta.status_code, 201)

        repositorio = RepositorioFilminasSQLAlchemy(self.session)
        filmina = repositorio.obtener_por_identificador("F001")

        self.assertIsNotNone(filmina)
        assert filmina is not None

        self.assertEqual(filmina.identificador, "F001")
        self.assertEqual(filmina.descripcion, "Filmina funcional")
        self.assertEqual(filmina.fecha, date(2024, 1, 15))

    def test_crear_filmina_con_archivo_desde_formulario(self) -> None:
        contenido = b"contenido de prueba"

        respuesta = self.client.post(
            "/filminas",
            data={
                "descripcion": "Filmina con archivo",
                "fecha": "2024-01-15",
                "procedencia": "BLAA",
                "archivo": (
                    BytesIO(contenido),
                    "filmina.jpg",
                ),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(respuesta.status_code, 201)

        datos = respuesta.get_json()
        self.assertIsNotNone(datos)
        assert datos is not None

        self.assertEqual(datos["identificador"], "F001")
        self.assertEqual(
            datos["descripcion"],
            "Filmina con archivo",
        )

        archivos = list(Path(self.directorio_temporal.name).rglob("filmina.jpg"))

        self.assertEqual(len(archivos), 1)
        self.assertEqual(archivos[0].read_bytes(), contenido)

        repositorio = RepositorioFilminasSQLAlchemy(self.session)
        filmina = repositorio.obtener_por_identificador("F001")

        self.assertIsNotNone(filmina)
        assert filmina is not None
        self.assertIsNotNone(filmina.archivo)
