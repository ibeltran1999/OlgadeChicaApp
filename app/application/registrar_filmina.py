from app.domain import Filmina
from app.domain.enums import ProcedenciaFilmina


class RegistrarFilmina:
    def __init__(self, repositorio, generador, almacenamiento):
        self.repositorio = repositorio
        self.generador = generador
        self.almacenamiento = almacenamiento

    def ejecutar(self, descripcion, fecha, procedencia, archivo=None):
        identificador = self.generador.generar_identificador_filmina()
        filmina = Filmina(
            identificador=identificador,
            descripcion=descripcion,
            fecha=fecha,
            procedencia=ProcedenciaFilmina(procedencia),
        )

        self.repositorio.guardar(filmina)

        return filmina
