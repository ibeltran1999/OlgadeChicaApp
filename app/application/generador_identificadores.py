from uuid import uuid4


class GeneradorIdentificadores:
    def __init__(self, inicial: int = 1) -> None:
        self._siguiente = inicial

    def generar_identificador_filmina(self) -> str:
        identificador = str(self._siguiente)
        self._siguiente += 1
        return identificador
