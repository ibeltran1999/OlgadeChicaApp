from sqlalchemy import text


class GeneradorIdentificadores:
    """Calcula el siguiente número dentro de la transacción de registro.

    La sesión debe ser la misma que utiliza el repositorio para guardar.
    El llamador debe guardar o revertir antes de solicitar otro número.
    """

    def __init__(self, session) -> None:
        self.session = session

    def generar_identificador_filmina(self) -> str:
        # Un UPDATE sin filas adquiere el bloqueo de escritura de SQLite.
        # Se conserva hasta el commit/rollback del registro, sin modificar datos.
        self.session.execute(
            text("UPDATE filminas SET identificador = identificador WHERE 0")
        )
        ultimo = self.session.execute(
            text(
                "SELECT COALESCE(MAX(CAST(identificador AS INTEGER)), 0) "
                "FROM filminas WHERE identificador <> '' "
                "AND identificador NOT GLOB '*[^0-9]*'"
            )
        ).scalar_one()
        return str(ultimo + 1)

    def generar_identificador_boceto(self) -> str:
        # Un UPDATE sin filas adquiere el bloqueo de escritura de SQLite.
        # Se conserva hasta el commit/rollback del registro, sin modificar datos.
        self.session.execute(
            text("UPDATE bocetos SET identificador = identificador WHERE 0")
        )
        ultimo = self.session.execute(
            text(
                "SELECT COALESCE(MAX(CAST(identificador AS INTEGER)), 0) "
                "FROM bocetos WHERE identificador <> '' "
                "AND identificador NOT GLOB '*[^0-9]*'"
            )
        ).scalar_one()
        return str(ultimo + 1)

    def generar_identificador_recurso(self) -> str:
        # Un UPDATE sin filas adquiere el bloqueo de escritura de SQLite.
        # Se conserva hasta el commit/rollback del registro, sin modificar datos.
        self.session.execute(
            text("UPDATE recursos SET identificador = identificador WHERE 0")
        )
        ultimo = self.session.execute(
            text(
                "SELECT COALESCE(MAX(CAST(identificador AS INTEGER)), 0) "
                "FROM recursos WHERE identificador <> '' "
                "AND identificador NOT GLOB '*[^0-9]*'"
            )
        ).scalar_one()
        return str(ultimo + 1)
