from sqlalchemy import select

from app.domain.tag import Tag
from app.persistence.modelos import TagModel


class RepositorioTagsSQLAlchemy:

    def __init__(self, session):
        self.session = session

    def guardar(self, tag: Tag) -> None:
        modelo = self.session.scalar(
            select(TagModel).where(TagModel.identificador == tag.identificador)
        )

        if modelo is None:
            modelo = TagModel(
                identificador=tag.identificador,
                nombre=tag.nombre,
            )
            self.session.add(modelo)
        else:
            modelo.nombre = tag.nombre

        self.session.commit()

    def obtener_por_identificador(self, identificador: str) -> Tag | None:
        modelo = self.session.scalar(
            select(TagModel).where(TagModel.identificador == identificador)
        )

        if modelo is None:
            return None

        return Tag(
            identificador=modelo.identificador,
            nombre=modelo.nombre,
        )

    def listar(self) -> list[Tag]:
        modelos = self.session.scalars(
            select(TagModel).order_by(TagModel.identificador)
        ).all()

        return [
            Tag(identificador=modelo.identificador, nombre=modelo.nombre)
            for modelo in modelos
        ]
