import unittest
from faker import Faker
from datetime import date
from app.domain import Tag


class TagTestCase(unittest.TestCase):

    def setUp(self):
        return

    def test_crear_tag(self):
        tag = Tag(
            identificador="T001",
            nombre="Nombre del tag",
        )

        self.assertIsInstance(tag, Tag)
        self.assertEqual(tag.identificador, "T001")
        self.assertEqual(tag.nombre, "Nombre del tag")
