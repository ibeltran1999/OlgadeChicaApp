from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.modelos.modelo_filmina import Base


class ArchivoModel(Base):
    __tablename__ = "archivos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    ruta: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)