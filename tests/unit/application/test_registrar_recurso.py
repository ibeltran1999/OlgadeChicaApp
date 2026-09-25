import unittest
from datetime import date
from unittest.mock import Mock

from app.application.registrar_recurso import RegistrarRecurso
from app.domain import Archivo, Boceto, Filmina
from app.domain.enums import ProcedenciaFilmina, TipoArchivo, TipoRecurso


class RegistrarRecursoTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Mock(spec=["guardar"])
        self.generador = Mock(spec=["generar_identificador_recurso"])
        self.generador.generar_identificador_recurso.side_effect = ["1", "2", "3"]
        self.storage = Mock(spec=["guardar"])
        self.gestor = RegistrarRecurso(self.repo, self.generador, self.storage)
        self.filmina = Filmina(
            "1", "Filmina", date(2020, 1, 1), ProcedenciaFilmina.BLAA
        )
        self.boceto = Boceto("1", "Boceto")

    def test_registra_obra_sin_archivo_asociada_a_filmina(self):
        recurso = self.gestor.ejecutar(
            nombre="Obra", tipo="Obra fisica", filmina=self.filmina
        )
        self.assertEqual(recurso.identificador, "1")
        self.assertEqual(recurso.nombre, "Obra")
        self.assertIs(recurso.filmina, self.filmina)
        self.assertIsNone(recurso.boceto)
        self.assertIsNone(recurso.archivo)
        self.repo.guardar.assert_called_once_with(recurso)
        self.storage.guardar.assert_not_called()

    def test_material_blaa_asociado_a_boceto_con_archivo(self):
        archivo = Archivo("recursos/1/material.pdf", "material.pdf", TipoArchivo.PDF)
        self.storage.guardar.return_value = archivo
        recurso = self.gestor.ejecutar(
            nombre="Material",
            tipo="Material físico consultable en la BLAA",
            boceto=self.boceto,
            archivo=dict(
                contenido=b"pdf", nombre_original="material.pdf", tipo=TipoArchivo.PDF
            ),
        )
        self.assertEqual(recurso.tipo, TipoArchivo.PDF.value)
        self.assertIs(recurso.archivo, archivo)
        self.assertIs(recurso.boceto, self.boceto)
        self.storage.guardar.assert_called_once_with(
            categoria="recursos",
            identificador="1",
            contenido=b"pdf",
            nombre_original="material.pdf",
            tipo=TipoArchivo.PDF,
        )
        self.repo.guardar.assert_called_once_with(recurso)

    def test_permite_ambas_asociaciones_y_solicita_identificadores(self):
        uno = self.gestor.ejecutar(
            nombre="Uno", tipo="Obra fisica", filmina=self.filmina, boceto=self.boceto
        )
        dos = self.gestor.ejecutar(nombre="Dos", tipo="Obra fisica", boceto=self.boceto)
        self.assertIs(uno.filmina, self.filmina)
        self.assertIs(uno.boceto, self.boceto)
        self.assertNotEqual(uno.identificador, dos.identificador)

    def test_rechaza_sin_asociacion_sin_efectos_secundarios(self):
        with self.assertRaises(ValueError):
            self.gestor.ejecutar(nombre="Obra", tipo="Obra fisica")
        self.generador.generar_identificador_recurso.assert_not_called()
        self.storage.guardar.assert_not_called()
        self.repo.guardar.assert_not_called()

    def test_rechaza_tipo_o_nombre_invalidos(self):
        for nombre, tipo in [
            ("Obra", "Otro"),
            ("", "Obra fisica"),
            ("  ", "Obra fisica"),
        ]:
            with self.subTest(nombre=nombre, tipo=tipo), self.assertRaises(ValueError):
                self.gestor.ejecutar(nombre=nombre, tipo=tipo, filmina=self.filmina)
        self.repo.guardar.assert_not_called()
        self.storage.guardar.assert_not_called()

    def test_no_guarda_si_falla_almacenamiento(self):
        self.storage.guardar.side_effect = OSError("Disco")
        with self.assertRaises(OSError):
            self.gestor.ejecutar(
                nombre="Obra",
                tipo="Obra fisica",
                filmina=self.filmina,
                archivo=dict(
                    contenido=b"x", nombre_original="a.pdf", tipo=TipoArchivo.PDF
                ),
            )
        self.repo.guardar.assert_not_called()
