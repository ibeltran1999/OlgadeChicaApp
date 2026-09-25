class Boceto:
    def __init__(self, identificador, descripcion, fecha = None):
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
        pass

