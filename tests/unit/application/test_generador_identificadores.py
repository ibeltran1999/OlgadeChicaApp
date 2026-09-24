import re
import unittest

from app.application.generador_identificadores import (
    GeneradorIdentificadores,
)



class GeneradorIdentificadoresTestCase(unittest.TestCase):

    def test_generar_identificadores_incrementales(self) -> None:
        generador = GeneradorIdentificadores()

        self.assertEqual(
            generador.generar_identificador_filmina(),
            "1",
        )
        self.assertEqual(
            generador.generar_identificador_filmina(),
            "2",
        )
        self.assertEqual(
            generador.generar_identificador_filmina(),
            "3",
        )

    def test_generador_puede_iniciar_en_otro_numero(self) -> None:
        generador = GeneradorIdentificadores(inicial=10)

        self.assertEqual(
            generador.generar_identificador_filmina(),
            "10",
        )
