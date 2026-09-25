"""Rutas compartidas por la aplicación y las migraciones."""

import os
from pathlib import Path
import sys

from sqlalchemy.engine import URL


def carpeta_recursos() -> Path:
    """Los recursos de PyInstaller pueden vivir en una carpeta temporal."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def carpeta_datos(data_dir: Path | None = None) -> Path:
    """Prioridad: argumento explícito, OLGA_DATA_DIR y ruta predeterminada."""
    if data_dir is None:
        configured = os.environ.get("OLGA_DATA_DIR")
        if configured:
            data_dir = Path(configured)
        elif sys.platform == "win32" or getattr(sys, "frozen", False):
            data_dir = (
                Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "OlgaDeChica"
            )
        else:
            data_dir = Path(__file__).resolve().parents[1] / "instance"
    return data_dir.expanduser().resolve()


def ruta_base_datos(data_dir: Path | None = None) -> Path:
    return carpeta_datos(data_dir) / "olga.db"


def url_base_datos(data_dir: Path | None = None) -> str:
    return URL.create(
        "sqlite", database=str(ruta_base_datos(data_dir))
    ).render_as_string(hide_password=False)
