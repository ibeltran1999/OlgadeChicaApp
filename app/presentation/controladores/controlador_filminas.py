from datetime import date
from typing import Any

from flask import Blueprint, jsonify, request, render_template

from app.application.registrar_filmina import RegistrarFilmina


def crear_controlador_filminas(gestor) -> Blueprint:
    controlador = Blueprint(
        "filminas",
        __name__,
        template_folder="../templates",
    )

    @controlador.get("/filminas/nueva")
    def mostrar_formulario() -> str:
        return render_template("filminas/formulario.html")

    @controlador.post("/filminas")
    def crear_filmina() -> tuple[Any, int]:
        datos: Any

        if request.form:
            datos = request.form
        else:
            datos = request.get_json(silent=True)

        if not isinstance(datos, dict):
            return jsonify({"error": "Datos inválidos"}), 400

        try:
            filmina = gestor.ejecutar(
                descripcion=datos["descripcion"],
                fecha=date.fromisoformat(datos["fecha"]),
                procedencia=datos["procedencia"],
            )
        except (KeyError, TypeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

        return (
            jsonify(
                {
                    "identificador": filmina.identificador,
                    "descripcion": filmina.descripcion,
                    "fecha": filmina.fecha.isoformat(),
                    "procedencia": filmina.procedencia.value,
                }
            ),
            201,
        )

    return controlador
