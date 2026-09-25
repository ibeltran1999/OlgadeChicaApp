import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import run


class ArranqueTestCase(unittest.TestCase):
    @patch("run.webbrowser.open", return_value=True)
    @patch("run.time.sleep")
    @patch("run.build_opener")
    def test_abre_navegador_solo_despues_de_responder(self, construir, dormir, abrir):
        cliente = construir.return_value
        cliente.open.side_effect = [URLError("iniciando"), MagicMock()]
        run.abrir_navegador(intentos=2)
        self.assertEqual(cliente.open.call_count, 2)
        abrir.assert_called_once_with(run.URL)

    @patch("run.webbrowser.open")
    @patch("run.time.sleep")
    @patch("run.build_opener")
    def test_no_abre_navegador_si_servidor_no_responde(self, construir, dormir, abrir):
        construir.return_value.open.side_effect = URLError("sin respuesta")
        with self.assertLogs(level="ERROR"):
            run.abrir_navegador(intentos=2)
        abrir.assert_not_called()
