import unittest
from app.domain import Archivo

class ArchivoTestCase(unittest.TestCase):

    def setUp(self):
        return

    def test_crear_archivo(self):
        archivo = Archivo(
            ruta="ruta/del/archivo.pdf",
            nombre="Nombre del archivo",
            tipo="Tipo del archivo",
        )
        self.assertIsInstance(archivo, Archivo)
        self.assertEqual(archivo.ruta, "ruta/del/archivo.pdf")
        self.assertEqual(archivo.nombre, "Nombre del archivo")
        self.assertEqual(archivo.tipo, "Tipo del archivo")


