from pathlib import Path

from app.domain import Archivo


class AlmacenamientoArchivosLocal:
    def __init__(self, carpeta_raiz):
        self.carpeta_raiz = Path(carpeta_raiz)

    def guardar(
        self,
        contenido,
        categoria,
        identificador,
        nombre_original,
        tipo,
    ):
        carpeta = self.carpeta_raiz / categoria / identificador
        carpeta.mkdir(parents=True, exist_ok=True)

        ruta_relativa = Path(categoria) / identificador / nombre_original
        ruta_fisica = self.carpeta_raiz / ruta_relativa
        ruta_fisica.write_bytes(contenido)

        return Archivo(
            ruta=str(ruta_relativa),
            nombre=nombre_original,
            tipo=tipo,
        )
