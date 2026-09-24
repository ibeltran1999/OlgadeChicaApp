import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.filmina import Filmina
from app.domain.tag import Tag
from app.domain.enums import ProcedenciaFilmina
from app.persistence.modelos import Base
from app.persistence.repositorio_filminas import RepositorioFilminasSQLAlchemy
from app.persistence.repositorio_tags import RepositorioTagsSQLAlchemy


class RepositorioFilminasTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()
        self.repositorio = RepositorioFilminasSQLAlchemy(self.session)
        self.repositorio_tags = RepositorioTagsSQLAlchemy(self.session)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_persistir_y_recuperar_filmina_sin_archivo(self):
        filmina = Filmina(
            identificador="F001",
            descripcion="Filmina de prueba",
            fecha=date(2024, 1, 15),
            procedencia=ProcedenciaFilmina.BLAA,
        )

        self.repositorio.guardar(filmina)

        self.session.close()

        nueva_sesion = self.Session()

        try:
            nuevo_repositorio = RepositorioFilminasSQLAlchemy(nueva_sesion)

            resultado = nuevo_repositorio.obtener_por_identificador("F001")

            if resultado is None:
                self.fail("No se encontro la filmina persistida")

            self.assertEqual(resultado.identificador, "F001")
            self.assertEqual(resultado.descripcion, "Filmina de prueba")
            self.assertEqual(resultado.fecha, date(2024, 1, 15))
            self.assertEqual(resultado.procedencia, ProcedenciaFilmina.BLAA)
            self.assertIsNone(resultado.archivo)
        finally:
            nueva_sesion.close()

    def test_persistir_y_recuperar_tags_de_filmina(self):
        filmina = Filmina(
            identificador="F002",
            descripcion="Filmina con tags",
            fecha=date(2024, 1, 15),
            procedencia=ProcedenciaFilmina.BLAA,
        )
        tags = [
            Tag(identificador="T001", nombre="Arquitectura"),
            Tag(identificador="T002", nombre="Fachada"),
        ]

        for tag in tags:
            self.repositorio_tags.guardar(tag)
            filmina.agregar_tag(tag)

        self.repositorio.guardar(filmina)

        self.session.close()

        nueva_sesion = self.Session()

        try:
            nuevo_repositorio = RepositorioFilminasSQLAlchemy(nueva_sesion)

            resultado = nuevo_repositorio.obtener_por_identificador("F002")

            if resultado is None:
                self.fail("No se encontro la filmina persistida")

            self.assertEqual(len(resultado.tags), 2)
            self.assertEqual(
                {(tag.identificador, tag.nombre) for tag in resultado.tags},
                {("T001", "Arquitectura"), ("T002", "Fachada")},
            )
        finally:
            nueva_sesion.close()

    def test_no_crear_tag_al_guardar_filmina_con_tag_inexistente(self):
        filmina = Filmina(
            identificador="F003",
            descripcion="Filmina con tag inexistente",
            fecha=date(2024, 1, 15),
            procedencia=ProcedenciaFilmina.BLAA,
        )
        filmina.agregar_tag(Tag(identificador="T999", nombre="Inexistente"))

        with self.assertRaises(ValueError):
            self.repositorio.guardar(filmina)

        self.assertIsNone(
            self.repositorio_tags.obtener_por_identificador("T999")
        )
