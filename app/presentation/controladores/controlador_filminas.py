from datetime import date
from typing import Any

from flask import Blueprint, jsonify, request

from app.application.registrar_filmina import RegistrarFilmina


def crear_controlador_filminas(gestor) -> Blueprint:
    controlador = Blueprint("filminas", __name__)

    @controlador.post("/filminas")
    def crear_filmina() -> tuple[Any, int]:
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict):
            return jsonify({"error": "El cuerpo debe ser JSON"}), 400

        try:
            filmina = gestor.ejecutar(
                descripcion=datos["descripcion"],
                fecha=date.fromisoformat(datos["fecha"]),
                procedencia=datos["procedencia"],
            )
        except (KeyError, TypeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400

        return jsonify(
            {
                "identificador": filmina.identificador,
                "descripcion": filmina.descripcion,
                "fecha": filmina.fecha.isoformat(),
                "procedencia": filmina.procedencia.value,
            }
        ), 201

    return controlador