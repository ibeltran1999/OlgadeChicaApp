from app.domain import Recurso
from app.domain.enums import TipoRecurso


class RegistrarRecurso:
    def __init__(self, repositorio, generador, almacenamiento):
        self.repositorio = repositorio
        self.generador = generador
        self.almacenamiento = almacenamiento

    def ejecutar(self, nombre, tipo, archivo=None, filmina=None, boceto=None):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del recurso es obligatorio")
        tipo = TipoRecurso(tipo)
        if filmina is None and boceto is None:
            raise ValueError("El recurso debe estar asociado a una filmina o un boceto")
        recurso = Recurso(
            self.generador.generar_identificador_recurso(),
            nombre,
            tipo.value,
            filmina=filmina,
            boceto=boceto,
        )
        if archivo is not None:
            recurso.archivo = self.almacenamiento.guardar(
                categoria="recursos", identificador=recurso.identificador, **archivo
            )
        self.repositorio.guardar(recurso)
        return recurso
