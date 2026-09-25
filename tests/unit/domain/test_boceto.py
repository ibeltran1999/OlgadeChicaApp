import unittest
from faker import Faker
from app.domain.enums import TipoArchivo
from app.domain import Boceto, Archivo, Tag
from datetime import date


class BocetoTestCase(unittest.TestCase):

    def setUp(self):
        self.data_factory = Faker("es_CO")

        self.data_factory.seed_instance(1000)

        tipo_archivo = [tipoarchivo.value for tipoarchivo in TipoArchivo]

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

    def test_crear_boceto(self):
        boceto = Boceto(
            identificador="B001",
            descripcion="Descripcion de prueba",
            fecha=date(1977, 4, 20),
        )
        self.assertIsInstance(boceto, Boceto)
        self.assertEqual(boceto.identificador, "B001")
        self.assertEqual(boceto.descripcion, "Descripcion de prueba")
        self.assertEqual(boceto.fecha, date(1977, 4, 20))

    def test_crear_boceto_sin_fecha(self):
        boceto = Boceto(
            identificador="B001",
            descripcion="Descripcion de prueba",
        )
        self.assertIsInstance(boceto, Boceto)
        self.assertEqual(boceto.identificador, "B001")
        self.assertEqual(boceto.descripcion, "Descripcion de prueba")
        self.assertIsNone(boceto.fecha)

    def test_asociar_boceto_con_archivo(self):
        datos_archivo_1 = self.datos_archivos[0]

        boceto_1 = Boceto(
            identificador="B001",
            descripcion="Descripcion de Prueba",
            fecha=date(2023, 4, 20),
        )

        archivo_1 = Archivo(
            ruta=datos_archivo_1["ruta"],
            nombre=datos_archivo_1["nombre"],
            tipo=datos_archivo_1["tipo"],
        )

        boceto_1.agregar_archivo(archivo_1)

        self.assertIs(boceto_1.archivo, archivo_1)
        self.assertIsInstance(boceto_1.archivo, Archivo)

    def test_permitir_asociar_tres_tags_a_filmina(self):
        datos_boceto_1 = self.datos_bocetos[0]
        datos_3_tags = self.datos_tags[0:3]
        tags = [
            Tag(identificador=datos["identificador"], nombre=datos["nombre"])
            for datos in datos_3_tags
        ]
        boceto_1 = Boceto(
            identificador=datos_boceto_1["identificador"],
            descripcion=datos_boceto_1["descripcion"],
            fecha=datos_boceto_1["fecha"],
        )

        for tag in tags:
            boceto_1.agregar_tag(tag)

        self.assertEqual(len(boceto_1.tags), 3)

        for tag in tags:
            self.assertIn(tag, boceto_1.tags)


def test_no_permitir_asociar_4_tags_a_filmina(self):
    datos_boceto_1 = self.datos_bocetos[0]
    datos_3_tags = self.datos_tags[0:3]
    datos_1_tag = self.datos_tags[3]
    tags = [
        Tag(identificador=datos["identificador"], nombre=datos["nombre"])
        for datos in datos_3_tags
    ]
    tag4 = Tag(identificador=datos_1_tag["identificador"], nombre=datos_1_tag["nombre"])
    boceto_1 = Boceto(
        identificador=datos_boceto_1["identificador"],
        descripcion=datos_boceto_1["descripcion"],
        fecha=datos_boceto_1["fecha"],
    )

    for tag in tags:
        boceto_1.agregar_tag(tag)

    with self.assertRaises(ValueError):
        boceto_1.agregar_tag(tag4)

    self.assertEqual(len(boceto_1.tags), 3)
