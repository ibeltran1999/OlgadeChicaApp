import unittest
from faker import Faker
from datetime import date
from app.domain import Filmina, Boceto
from app.domain.enums import ProcedenciaFilmina

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
            procedencia=ProcedenciaFilmina.BLAA,
        )

        self.assertIsInstance(filmina, Filmina)
        self.assertEqual(filmina.id, "F001")
        self.assertEqual(filmina.descripcion, "Descripcion de prueba")
        self.assertEqual(filmina.fecha, date(1977, 4, 20))
        self.assertEqual(filmina.procedencia, ProcedenciaFilmina.BLAA)

    def test_procedencia_filmina(self):
        self.assertEqual(ProcedenciaFilmina.BLAA.value, "BLAA")

    def test_relacionar_una_filmina_con_un_boceto(self):
        filmina_1 = Filmina(
            id="F001",
            descripcion="Filmina 1",
            fecha=date(1977, 4, 20),
            procedencia=ProcedenciaFilmina.BLAA,
        )
        boceto_1 = Boceto(
            id="B001",
            descripcion="Boceto 1",
            fecha=date(1977, 4, 20),
        )
        filmina_1.agregar_boceto(boceto_1)

        self.assertEqual(len(filmina_1.bocetos), 1)
        self.assertEqual(len(boceto_1.filminas), 1)
        self.assertIn(boceto_1, filmina_1.bocetos)
        self.assertIn(filmina_1, boceto_1.filminas)
        self.assertIs(filmina_1.bocetos[0], boceto_1)
        self.assertIs(boceto_1.filminas[0], filmina_1)
