from app.domain import Boceto


class RegistrarBocetos:
    def __init__(self, repositorio, generador, almacenamiento):
        self.repositorio = repositorio
        self.generador = generador
        self.almacenamiento = almacenamiento

    def ejecutar(self, descripcion, fecha=None, archivo=None, tags=None, filmina=None):
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError("La descripción es obligatoria")
        tags = list(tags or [])
        if len(tags) > 3:
            raise ValueError("Un boceto no puede tener más de tres tags")
        if len({tag.identificador for tag in tags}) != len(tags):
            raise ValueError("No puedes seleccionar el mismo tag más de una vez")
        boceto = Boceto(
            self.generador.generar_identificador_boceto(), descripcion, fecha
        )
        for tag in tags:
            boceto.agregar_tag(tag)
        if filmina is not None:
            filmina.agregar_boceto(boceto)
        if archivo is not None:
            boceto.agregar_archivo(
                self.almacenamiento.guardar(
                    categoria="bocetos", identificador=boceto.identificador, **archivo
                )
            )
        self.repositorio.guardar(boceto)
        return boceto
