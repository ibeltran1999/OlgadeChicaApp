from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.domain import Recurso, Archivo, Filmina, Boceto
from app.domain.enums import TipoArchivo, ProcedenciaFilmina
from app.persistence.modelos import (
    RecursoModel,
    ArchivoModel,
    FilminaModel,
    BocetoModel,
)


class RepositorioRecursosSQLAlchemy:
    def __init__(self, session):
        self.session = session

    def guardar(self, recurso):
        try:
            modelo = RecursoModel(
                identificador=recurso.identificador,
                nombre=recurso.nombre,
                tipo=recurso.tipo,
            )
            for atributo, clase in (("filmina", FilminaModel), ("boceto", BocetoModel)):
                asociado = getattr(recurso, atributo)
                if asociado is not None:
                    existente = self.session.scalar(
                        select(clase).where(
                            clase.identificador == asociado.identificador
                        )
                    )
                    if existente is None:
                        raise ValueError("El elemento asociado no existe")
                    setattr(modelo, atributo, existente)
            if recurso.archivo is not None:
                modelo.archivo = ArchivoModel(
                    nombre=recurso.archivo.nombre,
                    ruta=recurso.archivo.ruta,
                    tipo=recurso.archivo.tipo.value,
                )
            self.session.add(modelo)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def _consulta(self):
        return select(RecursoModel).options(
            selectinload(RecursoModel.archivo),
            selectinload(RecursoModel.filmina),
            selectinload(RecursoModel.boceto),
        )

    def listar(self):
        return [
            self._dominio(m)
            for m in self.session.scalars(
                self._consulta().order_by(RecursoModel.id)
            ).all()
        ]

    def obtener_por_identificador(self, identificador):
        modelo = self.session.scalar(
            self._consulta().where(RecursoModel.identificador == identificador)
        )
        return self._dominio(modelo) if modelo is not None else None

    @staticmethod
    def _dominio(modelo):
        filmina = modelo.filmina
        boceto = modelo.boceto
        archivo = modelo.archivo
        return Recurso(
            modelo.identificador,
            modelo.nombre,
            modelo.tipo,
            (
                Archivo(archivo.ruta, archivo.nombre, TipoArchivo(archivo.tipo))
                if archivo
                else None
            ),
            filmina=(
                Filmina(
                    filmina.identificador,
                    filmina.descripcion,
                    filmina.fecha,
                    ProcedenciaFilmina(filmina.procedencia),
                )
                if filmina
                else None
            ),
            boceto=(
                Boceto(boceto.identificador, boceto.descripcion, boceto.fecha)
                if boceto
                else None
            ),
        )
