import unittest
from datetime import date
from unittest.mock import Mock

from app.application.registrar_bocetos import RegistrarBocetos
from app.domain import Boceto, Archivo, Filmina, Tag
from app.domain.enums import TipoArchivo, ProcedenciaFilmina


class RegistrarBocetosTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Mock(spec=['guardar'])
        self.generador = Mock(spec=['generar_identificador_boceto'])
        self.generador.generar_identificador_boceto.side_effect = ['1', '2']
        self.storage = Mock(spec=['guardar'])
        self.gestor = RegistrarBocetos(self.repo, self.generador, self.storage)

    def test_registra_sin_fecha_ni_archivo(self):
        boceto = self.gestor.ejecutar(descripcion='Estudio')
        self.assertIsInstance(boceto, Boceto)
        self.assertEqual(boceto.identificador, '1')
        self.assertEqual(boceto.descripcion, 'Estudio')
        self.assertIsNone(boceto.fecha)
        self.assertIsNone(boceto.archivo)
        self.repo.guardar.assert_called_once_with(boceto)
        self.storage.guardar.assert_not_called()

    def test_registra_fecha_archivo_tags_y_filmina(self):
        archivo = Archivo('bocetos/1/a.png', 'a.png', TipoArchivo.PNG)
        self.storage.guardar.return_value = archivo
        tags = [Tag(str(i), str(i)) for i in range(3)]
        filmina = Filmina('1', 'Filmina', date(2020, 1, 1), ProcedenciaFilmina.BLAA)
        boceto = self.gestor.ejecutar(
            descripcion='Estudio', fecha=date(2021, 1, 1), tags=tags, filmina=filmina,
            archivo=dict(contenido=b'imagen', nombre_original='a.png', tipo=TipoArchivo.PNG),
        )
        self.assertEqual(boceto.fecha, date(2021, 1, 1))
        self.assertIs(boceto.archivo, archivo)
        self.assertEqual(boceto.tags, tags)
        self.assertIn(filmina, boceto.filminas)
        self.assertIn(boceto, filmina.bocetos)
        self.repo.guardar.assert_called_once_with(boceto)
        self.storage.guardar.assert_called_once_with(contenido=b'imagen', categoria='bocetos', identificador='1', nombre_original='a.png', tipo=TipoArchivo.PNG)

    def test_rechaza_tags_invalidos_antes_de_guardar(self):
        for tags in ([Tag(str(i), str(i)) for i in range(4)], [Tag('1', 'A'), Tag('1', 'B')]):
            with self.subTest(tags=tags), self.assertRaises(ValueError):
                self.gestor.ejecutar(descripcion='Estudio', tags=tags)
        self.repo.guardar.assert_not_called()
        self.storage.guardar.assert_not_called()

    def test_solicita_identificadores_distintos(self):
        primero = self.gestor.ejecutar(descripcion='Uno')
        segundo = self.gestor.ejecutar(descripcion='Dos')
        self.assertNotEqual(primero.identificador, segundo.identificador)

    def test_no_guarda_si_falla_archivo(self):
        self.storage.guardar.side_effect = OSError('Disco')
        with self.assertRaises(OSError):
            self.gestor.ejecutar(descripcion='Estudio', archivo=dict(contenido=b'x', nombre_original='a.png', tipo=TipoArchivo.PNG))
        self.repo.guardar.assert_not_called()
