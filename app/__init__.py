from flask import Flask, g, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from werkzeug.local import LocalProxy
from app.configuracion import carpeta_datos, url_base_datos

from app.application.generador_identificadores import (
    GeneradorIdentificadores,
)
from app.application.registrar_filmina import RegistrarFilmina
from app.application.registrar_tag import RegistrarTag
from app.persistence.repositorio_filminas import (
    RepositorioFilminasSQLAlchemy,
)
from app.persistence.repositorio_tags import RepositorioTagsSQLAlchemy
from app.persistence.almacenamiento_archivos_local import (
    AlmacenamientoArchivosLocal,
)
from app.presentation.controladores.controlador_filminas import (
    crear_controlador_filminas,
)
from app.presentation.controladores.controlador_tags import crear_controlador_tags


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    datos = carpeta_datos()
    datos.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url_base_datos(datos), poolclass=NullPool)

    session_factory = sessionmaker(bind=engine)

    def obtener_session():
        if "database_session" not in g:
            g.database_session = session_factory()
        return g.database_session

    session = LocalProxy(obtener_session)

    @app.teardown_appcontext
    def cerrar_session(error=None):
        session_actual = g.pop("database_session", None)
        if session_actual is not None:
            session_actual.close()

    carpeta_storage = datos / "storage"
    carpeta_storage.mkdir(parents=True, exist_ok=True)

    repositorio = RepositorioFilminasSQLAlchemy(session)
    repositorio_tags = RepositorioTagsSQLAlchemy(session)
    generador = GeneradorIdentificadores()
    almacenamiento = AlmacenamientoArchivosLocal(carpeta_storage)
    gestor = RegistrarFilmina(repositorio, generador, almacenamiento)
    gestor_tags = RegistrarTag(repositorio_tags)

    app.register_blueprint(
        crear_controlador_filminas(
            gestor, repositorio_tags, repositorio, carpeta_storage
        )
    )
    app.register_blueprint(crear_controlador_tags(gestor_tags))

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    return app
