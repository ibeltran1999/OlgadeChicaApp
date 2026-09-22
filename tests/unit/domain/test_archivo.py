import unittest
from app.domain import Archivo
from app.domain.enums import TipoArchivo
from faker import Faker


class ArchivoTestCase(unittest.TestCase):

    def setUp(self):
        self.data_factory = Faker("es_CO")
        self.data_factory.seed_instance(1000)

        tipo_archivo = [tipoarchivo.value for tipoarchivo in TipoArchivo]

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

    def test_crear_archivo(self):
        datos_archivo_1 = self.datos_archivos[0]
        archivo = Archivo(
            ruta=datos_archivo_1["ruta"],
            nombre=datos_archivo_1["nombre"],
            tipo=datos_archivo_1["tipo"],
        )
        self.assertIsInstance(archivo, Archivo)
        self.assertEqual(archivo.ruta, datos_archivo_1["ruta"])
        self.assertEqual(archivo.nombre, datos_archivo_1["nombre"])
        self.assertEqual(archivo.tipo, datos_archivo_1["tipo"])
