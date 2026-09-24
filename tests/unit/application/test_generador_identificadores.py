import re
import unittest

from app.application.generador_identificadores import (
    GeneradorIdentificadores,
)


class GeneradorIdentificadoresTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.generador = GeneradorIdentificadores()

    def test_generar_identificador_de_filmina(self) -> None:
        identificador = (
            self.generador.generar_identificador_filmina()
        )

        self.assertRegex(identificador, r"^F-[A-F0-9]{8}$")

    def test_generar_identificadores_diferentes(self) -> None:
        primero = self.generador.generar_identificador_filmina()
        segundo = self.generador.generar_identificador_filmina()

        self.assertNotEqual(primero, segundo)
