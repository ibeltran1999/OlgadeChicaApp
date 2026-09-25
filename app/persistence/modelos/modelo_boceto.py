from datetime import date
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.persistence.modelos.modelo_filmina import Base, FilminaModel
from app.persistence.modelos.modelo_archivo import ArchivoModel
from app.persistence.modelos.modelo_tag import TagModel

boceto_tags = Table(
    "boceto_tags", Base.metadata,
    Column("boceto_id", ForeignKey("bocetos.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
boceto_filminas = Table(
    "boceto_filminas", Base.metadata,
    Column("boceto_id", ForeignKey("bocetos.id"), primary_key=True),
    Column("filmina_id", ForeignKey("filminas.id"), primary_key=True),
)


class BocetoModel(Base):
    __tablename__ = "bocetos"
    id: Mapped[int] = mapped_column(primary_key=True)
    identificador: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str] = mapped_column(String(500))
    fecha: Mapped[date | None]
    archivo_id: Mapped[int | None] = mapped_column(ForeignKey("archivos.id"), unique=True)
    archivo: Mapped[ArchivoModel | None] = relationship(cascade="all, delete-orphan", single_parent=True)
    tags: Mapped[list[TagModel]] = relationship(secondary=boceto_tags)
    filminas: Mapped[list[FilminaModel]] = relationship(secondary=boceto_filminas)
