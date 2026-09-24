from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FilminaModel(Base):
    __tablename__ = "filminas"

    __table_args__ = (
        UniqueConstraint(
            "identificador",
            name="uq_filminas_identificador",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    identificador: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    descripcion: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    procedencia: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    archivo_id: Mapped[int | None] = mapped_column(
        ForeignKey("archivos.id"),
        nullable=True,
        unique=True,
    )
