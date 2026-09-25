from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.domain.enums import ProcedenciaFilmina, TipoArchivo
from app.domain.archivo import Archivo
from app.domain.filmina import Filmina
from app.domain.tag import Tag
from app.persistence.modelos import ArchivoModel, FilminaModel, TagModel


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

        if filmina.archivo is not None:
            modelo.archivo = ArchivoModel(
                ruta=filmina.archivo.ruta,
                nombre=filmina.archivo.nombre,
                tipo=filmina.archivo.tipo.value,
            )

        try:
            self.session.add(modelo)
            identificadores = set()

            for tag in filmina.tags:
                if tag.identificador in identificadores:
                    continue

                tag_model = self.session.scalar(
                    select(TagModel).where(TagModel.identificador == tag.identificador)
                )

                if tag_model is None:
                    raise ValueError(f"El tag {tag.identificador} no existe")

                modelo.tags.append(tag_model)
                identificadores.add(tag.identificador)

            self.session.commit()
        except (SQLAlchemyError, ValueError):
            self.session.rollback()
            raise

    def obtener_por_identificador(self, identificador: str) -> Filmina | None:
        modelo = self.session.scalar(
            select(FilminaModel).where(FilminaModel.identificador == identificador)
        )

        if modelo is None:
            return None

        return self._a_dominio(modelo)

    def listar(self) -> list[Filmina]:
        modelos = self.session.scalars(
            select(FilminaModel)
            .options(
                selectinload(FilminaModel.tags),
                selectinload(FilminaModel.archivo),
            )
            .order_by(FilminaModel.id.asc())
        ).all()
        return [self._a_dominio(modelo) for modelo in modelos]

    @staticmethod
    def _a_dominio(modelo: FilminaModel) -> Filmina:
        archivo = None

        if modelo.archivo is not None:
            archivo = Archivo(
                ruta=modelo.archivo.ruta,
                nombre=modelo.archivo.nombre,
                tipo=TipoArchivo(modelo.archivo.tipo),
            )

        filmina = Filmina(
            identificador=modelo.identificador,
            descripcion=modelo.descripcion,
            fecha=modelo.fecha,
            procedencia=ProcedenciaFilmina(modelo.procedencia),
        )

        if archivo is not None:
            filmina.agregar_archivo(archivo)

        for tag_model in modelo.tags:
            filmina.agregar_tag(
                Tag(
                    identificador=tag_model.identificador,
                    nombre=tag_model.nombre,
                )
            )

        return filmina
