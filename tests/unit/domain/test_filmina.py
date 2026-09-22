import unittest
from faker import Faker
from datetime import date
from app.domain import Filmina, Boceto
from app.domain.enums import ProcedenciaFilmina


class FilminaTestCase(unittest.TestCase):

    def setUp(self):
        self.data_factory = Faker("es_CO")
        self.data_factory.seed_instance(1000)

        procedencias = [procedencia.value for procedencia in ProcedenciaFilmina]

        self.datos_filminas = []
        for i in range(0, 10):
            self.datos_filminas.append(
                {
                    "id": f"F{i+1:03d}",
                    "descripcion": self.data_factory.sentence(),
                    "fecha": self.data_factory.date_object(),
                    "procedencia": self.data_factory.random_element(procedencias),
                }
            )

        self.datos_bocetos = []
        for i in range(0, 10):
            self.datos_bocetos.append(
                {
                    "id": f"B{i + 1:03d}",
                    "descripcion": self.data_factory.sentence(),
                    "fecha": self.data_factory.date_object(),
                }
            )

    def test_crear_filmina(self):
        datos_filmina_1 = self.datos_filminas[0]
        filmina = Filmina(
            id=datos_filmina_1["id"],
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina_1["procedencia"]),
        )

        self.assertIsInstance(filmina, Filmina)
        self.assertEqual(filmina.id, datos_filmina_1["id"])
        self.assertEqual(filmina.descripcion, datos_filmina_1["descripcion"])
        self.assertEqual(filmina.fecha, datos_filmina_1["fecha"])
        self.assertEqual(
            filmina.procedencia, ProcedenciaFilmina(datos_filmina_1["procedencia"])
        )

    def test_procedencia_filmina(self):
        self.assertEqual(ProcedenciaFilmina.BLAA.value, "BLAA")

    def test_relacionar_una_filmina_con_un_boceto(self):
        datos_filmina_1 = self.datos_filminas[0]
        datos_boceto_1 = self.datos_bocetos[0]

        filmina_1 = Filmina(
            id=datos_filmina_1["id"],
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina_1["procedencia"]),
        )

        boceto_1 = Boceto(
            id=datos_boceto_1["id"],
            descripcion=datos_boceto_1["descripcion"],
            fecha=datos_boceto_1["fecha"],
        )

        filmina_1.agregar_boceto(boceto_1)

        self.assertEqual(len(filmina_1.bocetos), 1)
        self.assertEqual(len(boceto_1.filminas), 1)
        self.assertIn(boceto_1, filmina_1.bocetos)
        self.assertIn(filmina_1, boceto_1.filminas)
        self.assertIs(filmina_1.bocetos[0], boceto_1)
        self.assertIs(boceto_1.filminas[0], filmina_1)
