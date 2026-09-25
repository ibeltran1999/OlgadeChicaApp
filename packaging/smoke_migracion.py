"""Verifica el migrador empaquetado, sin importar módulos de la aplicación."""

from contextlib import closing
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile


def main() -> None:
    ejecutable = Path(sys.argv[1]).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="olga-smoke-") as temporal:
        trabajo = Path(temporal)
        datos = trabajo / "datos con espacios 100%"
        entorno = dict(os.environ, OLGA_DATA_DIR=str(datos))
        for intento in range(2):
            resultado = subprocess.run(
                [str(ejecutable)],
                cwd=trabajo,
                env=entorno,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=60,
            )
            print(resultado.stdout, flush=True)
            print(resultado.stderr, file=sys.stderr, flush=True)
            if resultado.returncode:
                raise RuntimeError(
                    f"Migración {intento + 1} falló: código {resultado.returncode}"
                )
            base = datos / "olga.db"
            if not base.is_file():
                raise RuntimeError("No se creó olga.db en OLGA_DATA_DIR")
            with closing(
                sqlite3.connect(base.as_uri() + "?mode=ro", uri=True)
            ) as conexion:
                tablas = {
                    fila[0]
                    for fila in conexion.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
                esperadas = {
                    "alembic_version",
                    "archivos",
                    "filminas",
                    "filmina_tags",
                    "tags",
                    "bocetos",
                    "recursos",
                    "boceto_tags",
                    "boceto_filminas",
                }
                if not esperadas <= tablas:
                    raise RuntimeError(f"Faltan tablas: {esperadas - tablas}")
                versiones = conexion.execute(
                    "SELECT version_num FROM alembic_version"
                ).fetchall()
                if not versiones:
                    raise RuntimeError("Alembic no registró la versión del esquema")
        print("Smoke test de migración completado")


if __name__ == "__main__":
    main()
