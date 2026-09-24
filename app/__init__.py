from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

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

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    ruta_base_datos = Path(app.instance_path) / "olga.db"
    engine = create_engine(f"sqlite:///{ruta_base_datos}")

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    carpeta_storage = Path(app.instance_path) / "storage"
    carpeta_storage.mkdir(parents=True, exist_ok=True)

    repositorio = RepositorioFilminasSQLAlchemy(session)
    repositorio_tags = RepositorioTagsSQLAlchemy(session)
    generador = GeneradorIdentificadores()
    almacenamiento = AlmacenamientoArchivosLocal(carpeta_storage)
    gestor = RegistrarFilmina(repositorio, generador, almacenamiento)
    gestor_tags = RegistrarTag(repositorio_tags)

    app.register_blueprint(crear_controlador_filminas(gestor, repositorio_tags))
    app.register_blueprint(crear_controlador_tags(gestor_tags))

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    return app
