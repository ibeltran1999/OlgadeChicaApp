import os
import io
import sqlite3
from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from app.migration.comando import migrate


class ConsultaFilminasTestCase(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        entorno = patch.dict(os.environ, {"OLGA_DATA_DIR": self.temporal.name})
        entorno.start()
        self.addCleanup(entorno.stop)
        migrate()
        self.cliente = create_app().test_client()

    def test_listado_vacio_y_detalle_inexistente(self):
        respuesta = self.cliente.get("/filminas")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("Aún no hay filminas", respuesta.get_data(as_text=True))
        self.assertEqual(self.cliente.get("/filminas/inexistente").status_code, 404)
        self.assertIn(b"/filminas", self.cliente.get("/").data)

    def test_consulta_registros_persistidos_y_escapa_descripcion(self):
        self.cliente.post("/tags", json={"identificador": "T1", "nombre": "Paisaje"})
        ids = []
        for fecha, descripcion in (
            ("2024-01-01", "Primera filmina"),
            ("2025-01-01", "<script>alert(1)</script>"),
        ):
            respuesta = self.cliente.post(
                "/filminas",
                json={
                    "descripcion": descripcion,
                    "fecha": fecha,
                    "procedencia": "BLAA",
                    "tags": ["T1"],
                },
            )
            self.assertEqual(respuesta.status_code, 201)
            ids.append(respuesta.get_json()["identificador"])
        cliente = create_app().test_client()
        listado = cliente.get("/filminas").get_data(as_text=True)
        self.assertLess(
            listado.index(f'href="/filminas/{ids[0]}"'),
            listado.index(f'href="/filminas/{ids[1]}"'),
        )
        self.assertNotIn("<script>", listado)
        respuesta = cliente.get("/filminas/" + ids[1])
        self.assertEqual(respuesta.status_code, 200)
        detalle = respuesta.get_data(as_text=True)
        for valor in ("Paisaje", "2025-01-01", "BLAA", "Sin archivo digital"):
            self.assertIn(valor, detalle)
        self.assertIn("&lt;script&gt;", detalle)

    def registrar_con_archivo(self, nombre, contenido):
        respuesta = self.cliente.post(
            "/filminas",
            data={
                "descripcion": "Con archivo",
                "fecha": "2025-01-01",
                "procedencia": "BLAA",
                "archivo": (io.BytesIO(contenido), nombre),
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        with closing(sqlite3.connect(Path(self.temporal.name) / "olga.db")) as conexion:
            return conexion.execute(
                "SELECT identificador FROM filminas ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]

    def test_preview_y_descarga_segun_formato(self):
        for nombre, contenido, mime, elemento in (
            ("imagen.png", b"png de prueba", "image/png", "<img"),
            ("foto.jpg", b"jpg de prueba", "image/jpeg", "<img"),
            ("documento.pdf", b"%PDF-1.4", "application/pdf", "<iframe"),
            (
                "original.cr2",
                b"raw de prueba",
                "application/octet-stream",
                "archivos CR2",
            ),
        ):
            with self.subTest(nombre=nombre):
                identificador = self.registrar_con_archivo(nombre, contenido)
                url = "/filminas/" + identificador
                detalle = self.cliente.get(url).get_data(as_text=True)
                self.assertIn(elemento, detalle)
                with self.cliente.get(url + "/archivo") as respuesta:
                    self.assertEqual(respuesta.status_code, 200)
                    self.assertEqual(respuesta.data, contenido)
                    self.assertEqual(respuesta.mimetype, mime)
                with self.cliente.get(url + "/archivo?descargar=1") as descarga:
                    self.assertEqual(descarga.data, contenido)
                    self.assertIn("attachment", descarga.headers["Content-Disposition"])

    def test_archivo_ausente_y_ruta_fuera_de_storage(self):
        self.assertEqual(
            self.cliente.get("/filminas/inexistente/archivo").status_code, 404
        )
        identificador = self.registrar_con_archivo("imagen.png", b"imagen")
        url = "/filminas/" + identificador + "/archivo"
        with closing(sqlite3.connect(Path(self.temporal.name) / "olga.db")) as conexion:
            conexion.execute("UPDATE archivos SET ruta = ?", ("../olga.db",))
            conexion.commit()
        self.assertEqual(self.cliente.get(url).status_code, 404)
        with closing(sqlite3.connect(Path(self.temporal.name) / "olga.db")) as conexion:
            conexion.execute("UPDATE archivos SET ruta = ?", ("no-existe.png",))
            conexion.commit()
        self.assertEqual(self.cliente.get(url).status_code, 404)

    def test_registra_despues_de_reiniciar_con_tags(self):
        self.cliente.post("/tags", json={"identificador": "T1", "nombre": "Paisaje"})
        datos = {
            "descripcion": "Primera",
            "fecha": "2025-01-01",
            "procedencia": "BLAA",
            "tags": ["T1"],
        }
        primera = self.cliente.post("/filminas", json=datos)
        self.assertEqual(primera.status_code, 201)
        segunda = create_app().test_client().post("/filminas", json=datos)
        self.assertEqual(segunda.status_code, 201)
        self.assertEqual(
            int(segunda.get_json()["identificador"]),
            int(primera.get_json()["identificador"]) + 1,
        )
