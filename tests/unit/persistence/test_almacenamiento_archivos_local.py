import tempfile
import unittest
from pathlib import Path

from app.domain.enums import TipoArchivo
from app.domain import Archivo
from app.persistence.almacenamiento_archivos_local import (
    AlmacenamientoArchivosLocal,
)


class AlmacenamientoArchivosLocalTestCase(unittest.TestCase):

    def setUp(self):
        self.carpeta_temporal = tempfile.TemporaryDirectory()
        self.almacenamiento = AlmacenamientoArchivosLocal(self.carpeta_temporal.name)

        self.contenido = b"contenido de prueba"
        self.categoria = "filminas"
        self.identificador = "F001"
        self.nombre_original = "filmina.jpg"
        self.tipo = TipoArchivo.JPG

    def tearDown(self):
        self.carpeta_temporal.cleanup()

    def test_guardar_archivo_de_filmina_en_el_sistema_de_archivos(self):
        archivo = self.almacenamiento.guardar(
            contenido=self.contenido,
            categoria=self.categoria,
            identificador=self.identificador,
            nombre_original=self.nombre_original,
            tipo=self.tipo,
        )

        ruta_fisica = Path(self.carpeta_temporal.name) / archivo.ruta

        self.assertTrue(ruta_fisica.exists())
        self.assertEqual(
            Path(archivo.ruta).parent,
            Path(self.categoria) / self.identificador,
        )
        self.assertFalse(Path(archivo.ruta).is_absolute())
        self.assertEqual(Path(archivo.ruta).suffix, ".jpg")
        self.assertIsInstance(archivo, Archivo)
        self.assertEqual(ruta_fisica.read_bytes(), self.contenido)
        self.assertEqual(archivo.nombre, self.nombre_original)
        self.assertEqual(archivo.tipo, self.tipo)
