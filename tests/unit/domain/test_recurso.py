import unittest
from faker import Faker
from datetime import date
from app.domain import Recurso

class RecursoTestCase(unittest.TestCase):

    def setUp(self):
        return

    def test_crear_recurso(self):
        recurso = Recurso(
            id="R001",
            nombre="Nombre del recurso",
            tipo="Tipo del recurso"
        )
        self.assertIsInstance(recurso, Recurso)
        self.assertEqual(recurso.id, "R001")
        self.assertEqual(recurso.nombre, "Nombre del recurso")
        self.assertEqual(recurso.tipo, "Tipo del recurso")
        