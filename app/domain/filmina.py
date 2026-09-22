class Filmina:
    def __init__(self, id, descripcion, fecha, procedencia):
        self.id = id
        self.descripcion = descripcion
        self.fecha = fecha
        self.procedencia = procedencia
        self.bocetos = []
        self.archivo = None

    def agregar_boceto(self, boceto):
        if boceto not in self.bocetos:
            self.bocetos.append(boceto)

        if self not in boceto.filminas:
            boceto.filminas.append(self)

    def agregar_archivo(self, archivo):
        self.archivo = archivo
