import io
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from app import create_app
from app.migration.comando import migrate


class RecursosFunctionalTestCase(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        entorno = patch.dict(os.environ, {"OLGA_DATA_DIR": temporal.name})
        entorno.start()
        self.addCleanup(entorno.stop)
        migrate()
        self.app = create_app()
        self.client = self.app.test_client()
        self.filmina = self.client.post("/filminas", json=dict(descripcion="Filmina", fecha="2020-01-01", procedencia="BLAA")).get_json()["identificador"]
        self.boceto = self.client.post("/bocetos", json=dict(descripcion="Boceto")).get_json()["identificador"]

    def test_registra_consulta_y_continua_numeracion_tras_reinicio(self):
        datos = dict(nombre="Obra conservada", tipo="Obra fisica", filmina_identificador=self.filmina)
        respuesta = self.client.post("/recursos", json=datos)
        self.assertEqual(respuesta.status_code, 201)
        identificador = respuesta.get_json()["identificador"]
        cliente = create_app().test_client()
        self.assertIn("Obra conservada", cliente.get("/recursos/" + identificador).get_data(as_text=True))
        self.assertIn("Obra conservada", cliente.get("/recursos").get_data(as_text=True))
        segunda = cliente.post("/recursos", json=datos)
        self.assertEqual(segunda.status_code, 201)
        self.assertNotEqual(segunda.get_json()["identificador"], identificador)
        self.assertEqual(cliente.get("/recursos/ausente").status_code, 404)

    def test_formulario_archivo_y_ambas_relaciones(self):
        respuesta = self.client.post("/recursos", data=dict(nombre="Material", tipo="Material físico consultable en la BLAA",
            filmina_identificador=self.filmina, boceto_identificador=self.boceto,
            archivo=(io.BytesIO(b"%PDF-1.4"), "material.pdf")))
        self.assertEqual(respuesta.status_code, 302)
        cliente = create_app().test_client()
        detalle = cliente.get(respuesta.location).get_data(as_text=True)
        for valor in ("Material", "material.pdf", "/filminas/" + self.filmina, "/bocetos/" + self.boceto):
            self.assertIn(valor, detalle)
        with cliente.get(respuesta.location + "/archivo") as archivo:
            self.assertEqual(archivo.status_code, 200)
            self.assertEqual(archivo.data, b"%PDF-1.4")

    def test_rechaza_asociaciones_y_tipo_invalidos(self):
        for extras in ({}, {"filmina_identificador": "ausente"}, {"boceto_identificador": "ausente"}, {"filmina_identificador": self.filmina, "tipo": "Otro"}):
            datos = dict(nombre="No guardar", tipo="Obra fisica")
            datos.update(extras)
            with self.subTest(extras=extras):
                self.assertEqual(self.client.post("/recursos", json=datos).status_code, 400)
        self.assertNotIn("No guardar", self.client.get("/recursos").get_data(as_text=True))

    def test_concurrencia(self):
        def registrar(numero):
            with self.app.test_client() as cliente:
                respuesta = cliente.post("/recursos", json=dict(nombre=str(numero), tipo="Obra fisica", boceto_identificador=self.boceto))
                self.assertEqual(respuesta.status_code, 201)
                return respuesta.get_json()["identificador"]
        with ThreadPoolExecutor(max_workers=4) as ejecutor:
            ids = list(ejecutor.map(registrar, range(8)))
        self.assertEqual(len(set(ids)), 8)

    def test_formulario_y_navegacion_pendiente(self):
        self.assertEqual(self.client.get("/recursos/nuevo").status_code, 200)
        self.assertIn('href="/tags"', self.client.get("/tags/nueva").get_data(as_text=True))
        self.assertEqual(self.client.get("/tags").status_code, 200)
