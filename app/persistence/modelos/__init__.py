from app.persistence.modelos.modelo_archivo import ArchivoModel
from app.persistence.modelos.modelo_filmina import Base, FilminaModel
from app.persistence.modelos.modelo_tag import TagModel

__all__ = [
    "Base",
    "ArchivoModel",
    "FilminaModel",
    "TagModel",
    "BocetoModel",
    "RecursoModel",
]

from app.persistence.modelos.modelo_boceto import BocetoModel

from app.persistence.modelos.modelo_recurso import RecursoModel
