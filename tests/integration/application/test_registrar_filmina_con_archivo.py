import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.application.registrar_filmina import RegistrarFilmina
from app.domain.enums import ProcedenciaFilmina, TipoArchivo
from app.persistence.almacenamiento_archivos_local import (
    AlmacenamientoArchivosLocal,
)


class GeneradorFalso:
    def generar_identificador_filmina(self) -> str:
        return "F001"


class RepositorioFalso:
    def __init__(self) -> None:
        self.filmina_guardada = None

    def guardar(self, filmina) -> None:
        self.filmina_guardada = filmina


class RegistrarFilminaConArchivoTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.directorio_temporal = tempfile.TemporaryDirectory()

        self.almacenamiento = AlmacenamientoArchivosLocal(self.directorio_temporal.name)
        self.repositorio = RepositorioFalso()

        self.gestor = RegistrarFilmina(
            repositorio=self.repositorio,
            generador=GeneradorFalso(),
            almacenamiento=self.almacenamiento,
        )

    def tearDown(self) -> None:
        self.directorio_temporal.cleanup()

    def test_registrar_filmina_y_asociar_archivo(self) -> None:
        contenido = b"contenido de la filmina"
        nombre_archivo = "filmina.jpg"

        archivo = {
            "contenido": contenido,
            "nombre_original": nombre_archivo,
            "tipo": TipoArchivo.JPG,
        }

        resultado = self.gestor.ejecutar(
            descripcion="Filmina con archivo",
            fecha=date(2026, 9, 1),
            procedencia=ProcedenciaFilmina.BLAA.value,
            archivo=archivo,
        )

        self.assertIsNotNone(resultado.archivo)
        assert resultado.archivo is not None

        self.assertEqual(resultado.identificador, "F001")
        self.assertEqual(resultado.archivo.nombre, nombre_archivo)
        self.assertEqual(resultado.archivo.tipo, TipoArchivo.JPG)

        self.assertIs(self.repositorio.filmina_guardada, resultado)

        ruta_fisica = Path(self.directorio_temporal.name) / resultado.archivo.ruta

        self.assertTrue(ruta_fisica.exists())
        self.assertEqual(ruta_fisica.read_bytes(), contenido)
