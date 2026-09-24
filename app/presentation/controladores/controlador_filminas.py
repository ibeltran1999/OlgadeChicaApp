from datetime import date
from pathlib import Path
from typing import Any

from flask import Blueprint, jsonify, request, render_template

from app.application.registrar_filmina import RegistrarFilmina
from app.domain.enums import TipoArchivo

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
    def crear_filmina() -> Any:
        try:
            datos = request.form or request.get_json(silent=True)

            if datos is None:
                return jsonify({"error": "Datos inválidos"}), 400

            archivo_subido = request.files.get("archivo")
            archivo = None

            if archivo_subido is not None and archivo_subido.filename:
                extension = Path(
                    archivo_subido.filename
                ).suffix[1:].upper()

                archivo = {
                    "contenido": archivo_subido.read(),
                    "nombre_original": archivo_subido.filename,
                    "tipo": TipoArchivo(extension),
                }

            filmina = gestor.ejecutar(
                descripcion=datos["descripcion"],
                fecha=date.fromisoformat(datos["fecha"]),
                procedencia=datos["procedencia"],
                archivo=archivo,
            )

        except (KeyError, TypeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

        resultado = {
            "identificador": filmina.identificador,
            "descripcion": filmina.descripcion,
            "fecha": filmina.fecha.isoformat(),
            "procedencia": filmina.procedencia.value,
        }

        if request.form:
            return render_template(
                "filminas/confirmacion.html",
                resultado=resultado,
            )

        return jsonify(resultado), 201

    return controlador