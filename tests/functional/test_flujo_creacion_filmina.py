import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask

from app.application.registrar_filmina import RegistrarFilmina
from app.persistence.modelos import Base
from app.persistence.repositorio_filminas import (
    RepositorioFilminasSQLAlchemy,
)
from app.presentation.controladores.controlador_filminas import (
    crear_controlador_filminas,
)


class GeneradorIdentificadoresFalso:
    def generar_identificador_filmina(self) -> str:
        return "F001"


class FilminasFunctionalTestCase(unittest.TestCase):

    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        session_factory = sessionmaker(bind=engine)
        session = session_factory()

        repositorio = RepositorioFilminasSQLAlchemy(session)
        generador = GeneradorIdentificadoresFalso()
        gestor = RegistrarFilmina(repositorio, generador)

        self.app = Flask(__name__)
        self.app.register_blueprint(
            crear_controlador_filminas(gestor)
        )
        self.client = self.app.test_client()
        self.session = session

    def tearDown(self) -> None:
        self.session.close()

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

