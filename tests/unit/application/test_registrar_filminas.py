import unittest
import tempfile
from datetime import date
from faker import Faker

from app.domain import Filmina, Archivo
from app.application.registrar_filmina import RegistrarFilmina
from app.domain.enums import ProcedenciaFilmina, TipoArchivo


class RepositorioFilminasEnMemoria:
    def __init__(self):
        self.filminas = []

    def guardar(self, filmina):
        self.filminas.append(filmina)


class GeneradorIdentificadoresEnMemoria:
    def generar_identificador_filmina(self):
        return "F001"


class AlmacenamientoArchivosEnMemoria:
    def __init__(self) -> None:
        self.archivo_guardado = None

    def guardar(
        self,
        contenido,
        categoria,
        identificador,
        nombre_original,
        tipo,
    ):
        self.archivo_guardado = Archivo(
            ruta=f"{categoria}/{identificador}/{nombre_original}",
            nombre=nombre_original,
            tipo=tipo,
        )
        return self.archivo_guardado


class RegistrarFilminaTestCase(unittest.TestCase):
    def setUp(self):
        self.directorio_temporal = tempfile.TemporaryDirectory()
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

    def tearDown(self) -> None:
        self.directorio_temporal.cleanup()

    def test_registrar_filmina_sin_archivo(self):
        repositorio = RepositorioFilminasEnMemoria()
        generador = GeneradorIdentificadoresEnMemoria()
        almacenamiento = AlmacenamientoArchivosEnMemoria()

        caso_de_uso = RegistrarFilmina(repositorio, generador, almacenamiento)
        datos_filmina_1 = self.datos_filminas[0]

        filmina = caso_de_uso.ejecutar(
            descripcion=datos_filmina_1["descripcion"],
            fecha=datos_filmina_1["fecha"],
            procedencia=datos_filmina_1["procedencia"],
        )

        self.assertIsInstance(filmina, Filmina)
        self.assertEqual(filmina.identificador, "F001")
        self.assertEqual(filmina.descripcion, datos_filmina_1["descripcion"])
        self.assertEqual(filmina.fecha, datos_filmina_1["fecha"])
        self.assertEqual(
            filmina.procedencia, ProcedenciaFilmina(datos_filmina_1["procedencia"])
        )
        self.assertIsNone(filmina.archivo)
        self.assertEqual(len(repositorio.filminas), 1)
        self.assertIs(repositorio.filminas[0], filmina)

    def test_registrar_filmina_con_archivo(self) -> None:
        repositorio = RepositorioFilminasEnMemoria()
        generador = GeneradorIdentificadoresEnMemoria()
        almacenamiento = AlmacenamientoArchivosEnMemoria()

        caso_de_uso = RegistrarFilmina(
            repositorio,
            generador,
            almacenamiento,
        )

        contenido = b"contenido de prueba"
        nombre = "filmina.jpg"

        filmina = caso_de_uso.ejecutar(
            descripcion="Filmina con archivo",
            fecha=date(2026, 9, 1),
            procedencia=ProcedenciaFilmina.BLAA.value,
            archivo={
                "contenido": contenido,
                "nombre_original": nombre,
                "tipo": TipoArchivo.JPG,
            },
        )

        self.assertIsNotNone(filmina.archivo)
        assert filmina.archivo is not None

        self.assertEqual(filmina.identificador, "F001")
        self.assertEqual(filmina.archivo.nombre, nombre)
        self.assertEqual(filmina.archivo.tipo, TipoArchivo.JPG)
        self.assertIs(repositorio.filminas[0], filmina)
        self.assertIs(almacenamiento.archivo_guardado, filmina.archivo)
