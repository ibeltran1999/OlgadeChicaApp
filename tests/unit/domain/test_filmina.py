import unittest
from faker import Faker
from datetime import date
from app.domain import Filmina, Boceto, Archivo, Tag
from app.domain.enums import ProcedenciaFilmina, TipoArchivo


class FilminaTestCase(unittest.TestCase):

    def setUp(self):
        self.data_factory = Faker("es_CO")
        self.data_factory.seed_instance(1000)

        procedencias = [procedencia.value for procedencia in ProcedenciaFilmina]
        tipo_archivo = [tipoarchivo.value for tipoarchivo in TipoArchivo]

        self.datos_filminas = []
        for i in range(0, 10):
            self.datos_filminas.append(
                {
                    "identificador": f"F{i+1:03d}",
                    "descripcion": self.data_factory.sentence(),
                    "fecha": self.data_factory.date_object(),
                    "procedencia": self.data_factory.random_element(procedencias),
                }
            )

        self.datos_bocetos = []
        for i in range(0, 10):
            self.datos_bocetos.append(
                {
                    "identificador": f"B{i + 1:03d}",
                    "descripcion": self.data_factory.sentence(),
                    "fecha": self.data_factory.date_object(),
                }
            )

        self.datos_archivos = []
        for i in range(0, 10):
            tipo = self.data_factory.random_element(tipo_archivo)
            nombre = f"archivo_{i + 1:03d}.{tipo.lower()}"

            self.datos_archivos.append(
                {
                    "ruta": f"archivos/{nombre}",
                    "nombre": nombre,
                    "tipo": TipoArchivo(tipo),
                }
            )
        self.datos_tags = []

        for i in range(0, 10):
            self.datos_tags.append(
                {
                    "identificador": f"T{i+1:03d}",
                    "nombre": self.data_factory.word(),
                }
            )

    def test_crear_filmina(self):
        datos_filmina_1 = self.datos_filminas[0]
        filmina = Filmina(
            identificador=datos_filmina_1["identificador"],
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina_1["procedencia"]),
        )

        self.assertIsInstance(filmina, Filmina)
        self.assertEqual(filmina.identificador, datos_filmina_1["identificador"])
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
            identificador=datos_filmina_1["identificador"],
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina_1["procedencia"]),
        )

        boceto_1 = Boceto(
            identificador=datos_boceto_1["identificador"],
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

    def test_crear_filmina_sin_archivo(self):
        datos_filmina = self.datos_filminas[0]

        filmina = Filmina(
            identificador=datos_filmina["identificador"],
            descripcion=datos_filmina["descripcion"],
            fecha=datos_filmina["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina["procedencia"]),
        )

        self.assertIsInstance(filmina, Filmina)
        self.assertIsNone(filmina.archivo)

    def test_asociar_archivo_a_filmina(self):
        datos_filmina_1 = self.datos_filminas[0]
        datos_archivo_1 = self.datos_archivos[0]

        filmina_1 = Filmina(
            identificador=datos_filmina_1["identificador"],
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina_1["procedencia"]),
        )

        archivo_1 = Archivo(
            ruta=datos_archivo_1["ruta"],
            nombre=datos_archivo_1["nombre"],
            tipo=datos_archivo_1["tipo"],
        )

        filmina_1.agregar_archivo(archivo_1)

        self.assertIs(filmina_1.archivo, archivo_1)
        self.assertIsInstance(filmina_1.archivo, Archivo)

    def test_asociar_tres_tags_a_filmina(self):
        datos_filmina_1 = self.datos_filminas[0]
        datos_3_tags = self.datos_tags[0:3]
        tags = [
            Tag(identificador=datos["identificador"], nombre=datos["nombre"])
            for datos in datos_3_tags
        ]
        filmina_1 = Filmina(
            identificador=datos_filmina_1["identificador"],
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina_1["procedencia"]),
        )

        for tag in tags:
            filmina_1.agregar_tag(tag)

        self.assertEqual(len(filmina_1.tags), 3)

        for tag in tags:
            self.assertIn(tag, filmina_1.tags)

    def test_no_permitir_asociar_4_tags_a_filmina(self):
        datos_filmina_1 = self.datos_filminas[0]
        datos_3_tags = self.datos_tags[0:3]
        datos_1_tag = self.datos_tags[3]
        tags = [
            Tag(identificador=datos["identificador"], nombre=datos["nombre"])
            for datos in datos_3_tags
        ]
        tag4 = Tag(
            identificador=datos_1_tag["identificador"], nombre=datos_1_tag["nombre"] 
        )
        filmina_1 = Filmina(
            identificador=datos_filmina_1["identificador"],
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=ProcedenciaFilmina(datos_filmina_1["procedencia"]),
        )

        for tag in tags:
            filmina_1.agregar_tag(tag)

        with self.assertRaises(ValueError):
            filmina_1.agregar_tag(tag4)

        self.assertEqual(len(filmina_1.tags), 3)


        