from typing import TYPE_CHECKING
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.persistence.modelos.modelo_filmina import Base, filmina_tags
if TYPE_CHECKING:
    from app.persistence.modelos.modelo_filmina import FilminaModel

class TagModel(Base):
    __tablename__ = "tags"

    __table_args__ = (
        UniqueConstraint(
            "identificador",
            name="uq_tags_identificador",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    identificador: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    filminas: Mapped[list["FilminaModel"]] = relationship(
        "FilminaModel",
        secondary=filmina_tags,
        back_populates="tags",
    )