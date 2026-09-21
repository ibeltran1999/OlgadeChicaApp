from app.domain import Boceto
import unittest
from datetime import date


class BocetoTestCase(unittest.TestCase):

    def setUp(self):
        return

    def test_crear_boceto(self):
        boceto = Boceto(
            id="B001",
            descripcion="Descripcion de prueba",
            fecha=date(1977, 4, 20),
        )
        self.assertIsInstance(boceto, Boceto)
        self.assertEqual(boceto.id, "B001")
        self.assertEqual(boceto.descripcion, "Descripcion de prueba")
        self.assertEqual(boceto.fecha, date(1977, 4, 20))
