from typing import Any

from flask import Blueprint, jsonify, render_template, request

from app.application.registrar_tag import RegistrarTag


def crear_controlador_tags(gestor: RegistrarTag, repositorio=None) -> Blueprint:
    controlador = Blueprint(
        "tags",
        __name__,
        template_folder="../templates",
    )

    @controlador.get("/tags")
    def listar():
        return render_template(
            "tags/listado.html", tags=repositorio.listar() if repositorio else []
        )

    @controlador.get("/tags/nueva")
    def mostrar_formulario() -> str:
        return render_template("tags/formulario.html")

    @controlador.post("/tags")
    def crear_tag() -> Any:
        try:
            datos = request.form or request.get_json(silent=True)

            if datos is None:
                return jsonify({"error": "Datos inválidos"}), 400

            tag = gestor.ejecutar(
                identificador=datos["identificador"],
                nombre=datos["nombre"],
            )
        except (KeyError, TypeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

        resultado = {
            "identificador": tag.identificador,
            "nombre": tag.nombre,
        }

        if request.form:
            return render_template("tags/confirmacion.html", resultado=resultado)

        return jsonify(resultado), 201

    return controlador
