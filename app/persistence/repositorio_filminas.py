from sqlalchemy import select

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

        for tag in filmina.tags:
            tag_model = self.session.scalar(
                select(TagModel).where(TagModel.identificador == tag.identificador)
            )

            if tag_model is None:
                tag_model = TagModel(
                    identificador=tag.identificador,
                    nombre=tag.nombre,
                )

            modelo.tags.append(tag_model)

        self.session.add(modelo)
        self.session.commit()

    def obtener_por_identificador(self, identificador: str) -> Filmina | None:
        modelo = self.session.scalar(
            select(FilminaModel).where(FilminaModel.identificador == identificador)
        )

        if modelo is None:
            return None

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
