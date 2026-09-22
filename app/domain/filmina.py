class Filmina:
    def __init__(self, identificador, descripcion, fecha, procedencia):
        self.identificador = identificador
        self.descripcion = descripcion
        self.fecha = fecha
        self.procedencia = procedencia
        self.bocetos = []
        self.archivo = None
        self.tags = []

    def agregar_boceto(self, boceto):
        if boceto not in self.bocetos:
            self.bocetos.append(boceto)

        if self not in boceto.filminas:
            boceto.filminas.append(self)

    def agregar_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def agregar_archivo(self, archivo):
        self.archivo = archivo
