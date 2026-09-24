from app.domain.tag import Tag


class RegistrarTag:

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self, identificador: str, nombre: str) -> Tag:
        identificador = identificador.strip()
        nombre = nombre.strip()

        if not identificador:
            raise ValueError("El identificador es obligatorio")
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if self.repositorio.obtener_por_identificador(identificador) is not None:
            raise ValueError("El identificador del tag ya existe")

        tag = Tag(identificador=identificador, nombre=nombre)
        self.repositorio.guardar(tag)
        return tag
