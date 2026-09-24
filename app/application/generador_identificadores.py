from uuid import uuid4


class GeneradorIdentificadores:

    def generar_identificador_filmina(self) -> str:
        return f"F-{uuid4().hex[:8].upper()}"
