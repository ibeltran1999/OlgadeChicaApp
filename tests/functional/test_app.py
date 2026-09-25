import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, event, text
from app.migration.comando import migrate

from app import create_app


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_pagina_principal(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Plataforma Olga de Chica", response.data)


class CierreConexionesTestCase(unittest.TestCase):
    def test_cierra_conexiones_y_permite_otra_peticion(self):
        with tempfile.TemporaryDirectory() as temporal, patch.dict(
            os.environ, {"OLGA_DATA_DIR": temporal}
        ):
            migrate()
            conexiones = []

            def crear_engine(*args, **kwargs):
                engine = create_engine(*args, **kwargs)
                event.listen(
                    engine,
                    "connect",
                    lambda conexion, registro: conexiones.append(conexion),
                )
                return engine

            with patch("app.create_engine", side_effect=crear_engine):
                app = create_app()
            app.config["TESTING"] = True

            # Usar peticiones reales para comprobar tanto lecturas como escrituras.
            cliente = app.test_client()
            for identificador in ("primero", "segundo"):
                respuesta = cliente.post(
                    "/tags", json={"identificador": identificador, "nombre": "Prueba"}
                )
                self.assertEqual(respuesta.status_code, 201)
                self.assertTrue(conexiones)
                for conexion in conexiones:
                    with self.assertRaises(sqlite3.ProgrammingError):
                        conexion.execute("SELECT 1")

            def fallar_despues_de_consulta(repositorio, tag):
                repositorio.session.execute(text("SELECT 1"))
                raise RuntimeError("fallo simulado")

            with patch(
                "app.persistence.repositorio_tags.RepositorioTagsSQLAlchemy.guardar",
                fallar_despues_de_consulta,
            ):
                with self.assertRaisesRegex(RuntimeError, "fallo simulado"):
                    cliente.post(
                        "/tags", json={"identificador": "error", "nombre": "Prueba"}
                    )
            for conexion in conexiones:
                with self.assertRaises(sqlite3.ProgrammingError):
                    conexion.execute("SELECT 1")
            respuesta = cliente.post(
                "/tags", json={"identificador": "recuperado", "nombre": "Prueba"}
            )
            self.assertEqual(respuesta.status_code, 201)
