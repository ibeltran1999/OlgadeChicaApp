from sqlalchemy import select

from app.domain.enums import ProcedenciaFilmina

from app.domain.filmina import Filmina
from app.persistence.modelos import FilminaModel


class RepositorioFilminasSQLAlchemy:

    def __init__(self, session):
        self.session = session

    def guardar(self, filmina: Filmina) -> None:
        modelo = FilminaModel(
            identificador=filmina.identificador,
            descripcion=filmina.descripcion,
            fecha=filmina.fecha,
            procedencia=filmina.procedencia.value,
        )

        self.session.add(modelo)
        self.session.commit()

    def obtener_por_identificador(self, identificador: str) -> Filmina | None:
        modelo = self.session.scalar(
            select(FilminaModel).where(
                FilminaModel.identificador == identificador
            )
        )

        if modelo is None:
            return None

        return Filmina(
            identificador=modelo.identificador,
            descripcion=modelo.descripcion,
            fecha=modelo.fecha,
            procedencia=ProcedenciaFilmina(modelo.procedencia),
        )