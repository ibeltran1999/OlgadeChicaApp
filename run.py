import logging
from logging.handlers import RotatingFileHandler
import threading
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
import webbrowser

from waitress.server import create_server

from app import create_app
from app.configuracion import carpeta_datos

URL = "http://127.0.0.1:5000/"


def abrir_navegador(url=URL, intentos=50):
    # La comprobación local no debe pasar por un proxy del sistema.
    cliente = build_opener(ProxyHandler({}))
    for _ in range(intentos):
        try:
            with cliente.open(url, timeout=1):
                pass
        except (URLError, OSError):
            time.sleep(0.2)
        else:
            try:
                if not webbrowser.open(url):
                    logging.error("No se pudo abrir el navegador: %s", url)
            except Exception:
                logging.exception("Error al abrir el navegador")
            return
    logging.error("La aplicación no respondió a tiempo en %s", url)


def main():
    datos = carpeta_datos()
    datos.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            RotatingFileHandler(
                datos / "aplicacion.log",
                maxBytes=2_000_000,
                backupCount=2,
                encoding="utf-8",
            )
        ],
    )
    servidor = None
    try:
        # Reservar el puerto antes de lanzar el navegador evita abrir otro servicio
        # si el puerto ya está ocupado.
        servidor = create_server(create_app(), host="127.0.0.1", port=5000)
        threading.Thread(target=abrir_navegador, daemon=True).start()
        logging.info("Aplicación iniciada en %s", URL)
        servidor.run()
    except Exception:
        logging.exception("No se pudo ejecutar la aplicación")
        return 1
    finally:
        if servidor is not None:
            servidor.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
