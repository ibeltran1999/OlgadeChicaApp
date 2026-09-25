class Recurso:
    def __init__(self, id, nombre, tipo, archivo=None, filmina=None, boceto=None):
        self.id = id
        self.identificador = id
        self.filmina = filmina
        self.boceto = boceto
        self.nombre = nombre
        self.tipo = tipo
        self.archivo = archivo
