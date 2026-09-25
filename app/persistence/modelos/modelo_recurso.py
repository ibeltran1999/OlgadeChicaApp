from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.persistence.modelos.modelo_filmina import Base, FilminaModel
from app.persistence.modelos.modelo_boceto import BocetoModel
from app.persistence.modelos.modelo_archivo import ArchivoModel


class RecursoModel(Base):
    __tablename__ = "recursos"
    __table_args__ = (
        CheckConstraint(
            "filmina_id IS NOT NULL OR boceto_id IS NOT NULL",
            name="ck_recurso_asociado",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    identificador: Mapped[str] = mapped_column(String(100), unique=True)
    nombre: Mapped[str] = mapped_column(String(500))
    tipo: Mapped[str] = mapped_column(String(100))
    archivo_id: Mapped[int | None] = mapped_column(
        ForeignKey("archivos.id"), unique=True
    )
    filmina_id: Mapped[int | None] = mapped_column(ForeignKey("filminas.id"))
    boceto_id: Mapped[int | None] = mapped_column(ForeignKey("bocetos.id"))
    archivo: Mapped[ArchivoModel | None] = relationship(
        cascade="all, delete-orphan", single_parent=True
    )
    filmina: Mapped[FilminaModel | None] = relationship()
    boceto: Mapped[BocetoModel | None] = relationship()
