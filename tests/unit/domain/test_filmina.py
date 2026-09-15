import unittest
from faker import Faker
from datetime import date
from app.domain import Filmina

faker = Faker("es_CO")
Faker.seed(1000)

class FilminaTestCase(unittest.TestCase):

    def setUp(self):
        return

    def test_crear_filmina(self):
        filmina = Filmina(
            id="F001",
            descripcion="Descripcion de prueba",
            fecha=date(1977, 4, 20),
        )   

        self.assertIsInstance(filmina, Filmina)
        self.assertEqual(filmina.id, "F001")
        self.assertEqual(filmina.descripcion, "Descripcion de prueba")
        self.assertEqual(filmina.fecha, date(1977, 4, 20))
        