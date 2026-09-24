import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.tag import Tag
from app.persistence.modelos import Base
from app.persistence.repositorio_tags import RepositorioTagsSQLAlchemy


class RepositorioTagsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()
        self.repositorio = RepositorioTagsSQLAlchemy(self.session)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_persistir_y_consultar_tag(self):
        tag = Tag(identificador="T001", nombre="Arquitectura")

        self.repositorio.guardar(tag)

        resultado = self.repositorio.obtener_por_identificador("T001")

        self.assertIsNotNone(resultado)
        assert resultado is not None
        self.assertEqual(resultado.identificador, "T001")
        self.assertEqual(resultado.nombre, "Arquitectura")

    def test_listar_tags_existentes(self):
        self.repositorio.guardar(Tag(identificador="T002", nombre="Fachada"))
        self.repositorio.guardar(Tag(identificador="T001", nombre="Arquitectura"))

        resultado = self.repositorio.listar()

        self.assertEqual(
            [(tag.identificador, tag.nombre) for tag in resultado],
            [("T001", "Arquitectura"), ("T002", "Fachada")],
        )
