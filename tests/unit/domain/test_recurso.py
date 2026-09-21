import unittest
from faker import Faker
from datetime import date
from app.domain import Recurso
from app.domain.enums import TipoRecurso


class RecursoTestCase(unittest.TestCase):

    def setUp(self):
        return

    def test_crear_recurso(self):
        recurso = Recurso(
            id="R001",
            nombre="Nombre del recurso",
            tipo=TipoRecurso.OBRA_FISICA.value,
            archivo="ruta/del/archivo.pdf",
        )
        self.assertIsInstance(recurso, Recurso)
        self.assertEqual(recurso.id, "R001")
        self.assertEqual(recurso.nombre, "Nombre del recurso")
        self.assertEqual(recurso.tipo, TipoRecurso.OBRA_FISICA.value)

    def test_tipo_recurso(self):
        self.assertEqual(TipoRecurso.OBRA_FISICA.value, "Obra fisica")
