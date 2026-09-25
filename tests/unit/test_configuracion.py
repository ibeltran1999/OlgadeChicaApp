import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from app.configuracion import carpeta_datos, carpeta_recursos, ruta_base_datos
from app.migration.comando import main


class ConfiguracionTestCase(unittest.TestCase):
    def test_desarrollo_no_depende_del_directorio_actual(self):
        with patch.dict(os.environ, {}, clear=True), patch(
            "app.configuracion.sys.platform", "linux"
        ), patch("app.configuracion.sys.frozen", False, create=True):
            esperado = Path(__file__).resolve().parents[2] / "instance"
            self.assertEqual(carpeta_datos(), esperado)

    def test_windows_y_paquete_comparten_datos_fuera_de_recursos(self):
        with tempfile.TemporaryDirectory() as temporal:
            with patch.dict(os.environ, {"LOCALAPPDATA": temporal}, clear=True), patch(
                "app.configuracion.sys.platform", "win32"
            ), patch("app.configuracion.sys.frozen", True, create=True), patch(
                "app.configuracion.sys._MEIPASS", temporal + "/paquete", create=True
            ):
                self.assertEqual(carpeta_datos(), Path(temporal) / "OlgaDeChica")
                self.assertEqual(carpeta_recursos(), Path(temporal) / "paquete")

    def test_argumento_tiene_prioridad_sobre_variable(self):
        with tempfile.TemporaryDirectory() as temporal:
            with patch.dict(os.environ, {"OLGA_DATA_DIR": temporal + "/entorno"}):
                self.assertEqual(carpeta_datos(), Path(temporal) / "entorno")
                self.assertEqual(carpeta_datos(Path(temporal)), Path(temporal))

    def test_migracion_y_aplicacion_comparten_base_en_windows(self):
        with tempfile.TemporaryDirectory() as temporal:
            with patch.dict(os.environ, {"LOCALAPPDATA": temporal}, clear=True), patch(
                "app.configuracion.sys.platform", "win32"
            ), patch("app.configuracion.sys.frozen", True, create=True):
                self.assertEqual(main([]), 0)
                self.assertTrue(ruta_base_datos().is_file())
                app = create_app()
                respuesta = app.test_client().post(
                    "/tags", json={"identificador": "prueba", "nombre": "Prueba"}
                )
                self.assertEqual(respuesta.status_code, 201)

    def test_alembic_desde_otra_carpeta_usa_configuracion_compartida(self):
        raiz = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as temporal:
            datos = Path(temporal) / "datos con espacios 100%"
            entorno = dict(os.environ, OLGA_DATA_DIR=str(datos))
            resultado = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "alembic",
                    "-c",
                    str(raiz / "alembic.ini"),
                    "upgrade",
                    "head",
                ],
                cwd=temporal,
                env=entorno,
                capture_output=True,
                text=True,
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            with patch.dict(os.environ, entorno):
                self.assertEqual(main([]), 0)
                respuesta = (
                    create_app()
                    .test_client()
                    .post("/tags", json={"identificador": "prueba", "nombre": "Prueba"})
                )
                self.assertEqual(respuesta.status_code, 201)
