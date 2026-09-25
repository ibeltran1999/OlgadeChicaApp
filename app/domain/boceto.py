class Boceto:
    def __init__(self, identificador, descripcion, fecha=None):
        self.identificador = identificador
        self.descripcion = descripcion
        self.fecha = fecha
        self.filminas = []
        self.archivo = None
        self.tags = []

    def agregar_archivo(self, archivo):
        self.archivo = archivo
        pass

    def agregar_tag(self, tag):
        if tag in self.tags:
            return

        if len(self.tags) >= 3:
            raise ValueError("Un boceto no puede tener mas de tres tags")

        self.tags.append(tag)
