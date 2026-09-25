import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.application.generador_identificadores import GeneradorIdentificadores
from app.domain.enums import ProcedenciaFilmina
from app.domain.filmina import Filmina
from app.persistence.modelos import Base
from app.persistence.repositorio_filminas import RepositorioFilminasSQLAlchemy


class GeneradorIdentificadoresTestCase(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.engine = create_engine(
            "sqlite:///" + str(Path(temporal.name) / "prueba.db"),
            connect_args={"timeout": 20},
        )
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)

    def guardar(self, identificador=None):
        with Session(self.engine) as session:
            if identificador is None:
                identificador = GeneradorIdentificadores(
                    session
                ).generar_identificador_filmina()
            RepositorioFilminasSQLAlchemy(session).guardar(
                Filmina(
                    identificador, "Prueba", date(2026, 1, 1), ProcedenciaFilmina.BLAA
                )
            )
            return identificador

    def test_continua_en_otra_sesion_y_tras_reabrir_conexiones(self):
        self.assertEqual(self.guardar(), "1")
        self.engine.dispose()
        self.assertEqual(self.guardar(), "2")

    def test_usa_maximo_numerico_e_ignora_identificadores_anteriores(self):
        for identificador in ("9", "10", "F999"):
            self.guardar(identificador)
        self.assertEqual(self.guardar(), "11")

    def test_registros_simultaneos_no_repiten_numero(self):
        with ThreadPoolExecutor(max_workers=4) as ejecutor:
            numeros = list(ejecutor.map(lambda _: self.guardar(), range(12)))
        self.assertEqual(sorted(map(int, numeros)), list(range(1, 13)))

    def test_rollback_libera_el_numero_no_guardado(self):
        with Session(self.engine) as session:
            self.assertEqual(
                GeneradorIdentificadores(session).generar_identificador_filmina(), "1"
            )
            session.rollback()
        self.assertEqual(self.guardar(), "1")
