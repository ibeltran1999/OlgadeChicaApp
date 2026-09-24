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

        if archivo is not None:
            archivo_guardado = self.almacenamiento.guardar(
                contenido=archivo["contenido"],
                categoria="filminas",
                identificador=identificador,
                nombre_original= archivo["nombre_original"],
                tipo=archivo["tipo"],
            )
            filmina.agregar_archivo(archivo_guardado)
            
        self.repositorio.guardar(filmina)

        return filmina
