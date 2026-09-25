import io
import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from app.migration.comando import migrate


class BocetosFunctionalTestCase(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        entorno = patch.dict(os.environ, {"OLGA_DATA_DIR": temporal.name})
        entorno.start()
        self.addCleanup(entorno.stop)
        migrate()
        self.client = create_app().test_client()

    def test_registro_consulta_y_reinicio(self):
        respuesta = self.client.post('/bocetos', json={'descripcion': 'Estudio sin fecha'})
        self.assertEqual(respuesta.status_code, 201)
        identificador = respuesta.get_json()['identificador']
        cliente = create_app().test_client()
        self.assertIn('Estudio sin fecha', cliente.get('/bocetos/' + identificador).get_data(as_text=True))
        self.assertIn('Estudio sin fecha', cliente.get('/bocetos').get_data(as_text=True))
        segunda = cliente.post('/bocetos', json={'descripcion': 'Segundo'})
        self.assertEqual(segunda.status_code, 201)
        self.assertNotEqual(segunda.get_json()['identificador'], identificador)
        self.assertEqual(cliente.get('/bocetos/inexistente').status_code, 404)

    def test_archivo_fecha_tags_y_relacion_persisten(self):
        filmina = self.client.post('/filminas', json={'descripcion': 'Filmina', 'fecha': '2020-01-01', 'procedencia': 'BLAA'}).get_json()['identificador']
        for i in range(3):
            self.client.post('/tags', json={'identificador': str(i), 'nombre': 'Tag ' + str(i)})
        respuesta = self.client.post('/bocetos', data={
            'descripcion': 'Con archivo', 'fecha': '2021-01-01',
            'filmina_identificador': filmina, 'tag_identificador': ['0', '1', '2'],
            'archivo': (io.BytesIO(b'imagen'), 'estudio.png'),
        })
        self.assertEqual(respuesta.status_code, 302)
        detalle = self.client.get(respuesta.location).get_data(as_text=True)
        for valor in ('Con archivo', '2021-01-01', 'Tag 0', 'Tag 1', 'Tag 2', 'estudio.png', '/filminas/' + filmina):
            self.assertIn(valor, detalle)
        with self.client.get(respuesta.location + '/archivo') as archivo:
            self.assertEqual(archivo.status_code, 200)
            self.assertEqual(archivo.data, b'imagen')

    def test_rechaza_asociaciones_invalidas(self):
        for extra in ({'tags': ['x']}, {'tags': ['x', 'x']}, {'tags': ['1','2','3','4']}, {'filmina_identificador': 'ausente'}, {'fecha': 'incorrecta'}):
            with self.subTest(extra=extra):
                respuesta = self.client.post('/bocetos', json=dict(descripcion='No guardar', **extra))
                self.assertEqual(respuesta.status_code, 400)
        self.assertNotIn('No guardar', self.client.get('/bocetos').get_data(as_text=True))

    def test_formulario_y_estado_vacio(self):
        self.assertEqual(self.client.get('/bocetos/nuevo').status_code, 200)
        self.assertIn('Aún no hay bocetos', self.client.get('/bocetos').get_data(as_text=True))
