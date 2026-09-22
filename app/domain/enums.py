from enum import Enum


class ProcedenciaFilmina(Enum):
    ARCHIVO_PEDRO_FELIPE_HOYOS_KORVEL = "Archivo Pedro Felipe Hoyos Korvel"
    BLAA = "BLAA"


class TipoRecurso(Enum):
    OBRA_FISICA = "Obra fisica"
    FILMINA_BIBLIOTECA = "Filmina biblioteca"


class TipoArchivo(Enum):
    PDF = "PDF"
    JPG = "JPG"
    PNG = "PNG"
    CR2 = "CR2"
