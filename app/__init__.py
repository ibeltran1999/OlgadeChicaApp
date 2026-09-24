from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app.application.generador_identificadores import (
    GeneradorIdentificadores,
)
from app.application.registrar_filmina import RegistrarFilmina
from app.persistence.modelos import Base
from app.persistence.repositorio_filminas import (
    RepositorioFilminasSQLAlchemy,
)
from app.presentation.controladores.controlador_filminas import (
    crear_controlador_filminas,
)


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    ruta_base_datos = Path(app.instance_path)/"olga.db"
    engine = create_engine(f"sqlite:///{ruta_base_datos}")
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    repositorio = RepositorioFilminasSQLAlchemy(session)
    generador = GeneradorIdentificadores()
    gestor = RegistrarFilmina(repositorio, generador)

    app.register_blueprint(crear_controlador_filminas(gestor))

    @app.get("/")
    def index() -> str:
        return "Plataforma Olga de Chica"

    return app
