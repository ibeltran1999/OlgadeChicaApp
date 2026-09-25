from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain import Archivo, Boceto, Filmina, Tag
from app.domain.enums import TipoArchivo, ProcedenciaFilmina
from app.persistence.modelos import ArchivoModel, BocetoModel, FilminaModel, TagModel


class RepositorioBocetosSQLAlchemy:
    def __init__(self, session):
        self.session = session

    def guardar(self, boceto):
        try:
            modelo = BocetoModel(
                identificador=boceto.identificador,
                descripcion=boceto.descripcion,
                fecha=boceto.fecha,
            )
            for tag in boceto.tags:
                existente = self.session.scalar(
                    select(TagModel).where(TagModel.identificador == tag.identificador)
                )
                if existente is None:
                    raise ValueError("El tag no existe")
                modelo.tags.append(existente)
            for filmina in boceto.filminas:
                existente = self.session.scalar(
                    select(FilminaModel).where(
                        FilminaModel.identificador == filmina.identificador
                    )
                )
                if existente is None:
                    raise ValueError("La filmina no existe")
                modelo.filminas.append(existente)
            if boceto.archivo is not None:
                modelo.archivo = ArchivoModel(
                    nombre=boceto.archivo.nombre,
                    ruta=boceto.archivo.ruta,
                    tipo=boceto.archivo.tipo.value,
                )
            self.session.add(modelo)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def _consulta(self):
        return select(BocetoModel).options(
            selectinload(BocetoModel.tags),
            selectinload(BocetoModel.filminas),
            selectinload(BocetoModel.archivo),
        )

    def listar(self):
        return [
            self._dominio(m)
            for m in self.session.scalars(
                self._consulta().order_by(BocetoModel.id)
            ).all()
        ]

    def obtener_por_identificador(self, identificador):
        modelo = self.session.scalar(
            self._consulta().where(BocetoModel.identificador == identificador)
        )
        return self._dominio(modelo) if modelo is not None else None

    @staticmethod
    def _dominio(modelo):
        boceto = Boceto(modelo.identificador, modelo.descripcion, modelo.fecha)
        for tag in modelo.tags:
            boceto.agregar_tag(Tag(tag.identificador, tag.nombre))
        for filmina in modelo.filminas:
            Filmina(
                filmina.identificador,
                filmina.descripcion,
                filmina.fecha,
                ProcedenciaFilmina(filmina.procedencia),
            ).agregar_boceto(boceto)
        if modelo.archivo:
            boceto.agregar_archivo(
                Archivo(
                    modelo.archivo.ruta,
                    modelo.archivo.nombre,
                    TipoArchivo(modelo.archivo.tipo),
                )
            )
        return boceto
