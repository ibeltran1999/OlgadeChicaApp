import os
from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    datos_windows = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "OlgaDeChica"
    os.environ.setdefault("OLGA_DATA_DIR", str(datos_windows))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
