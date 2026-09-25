from datetime import date
from pathlib import Path
from typing import Any

from flask import Blueprint, abort, jsonify, request, render_template, send_file

from sqlalchemy.exc import IntegrityError
from app.domain.enums import TipoArchivo


def crear_controlador_filminas(
    gestor, repositorio_tags=None, repositorio_filminas=None, carpeta_storage=None
) -> Blueprint:
    controlador = Blueprint(
        "filminas",
        __name__,
        template_folder="../templates",
    )

    @controlador.get("/filminas")
    def listar_filminas() -> str:
        return render_template(
            "filminas/listado.html", filminas=repositorio_filminas.listar()
        )

    @controlador.get("/filminas/<identificador>")
    def consultar_filmina(identificador: str) -> str:
        filmina = repositorio_filminas.obtener_por_identificador(identificador)
        if filmina is None:
            abort(404)
        return render_template("filminas/detalle.html", filmina=filmina)

    @controlador.get("/filminas/<identificador>/archivo")
    def consultar_archivo(identificador: str):
        filmina = repositorio_filminas.obtener_por_identificador(identificador)
        if filmina is None or filmina.archivo is None or carpeta_storage is None:
            abort(404)
        raiz = Path(carpeta_storage).resolve()
        ruta = (raiz / filmina.archivo.ruta).resolve()
        if not ruta.is_relative_to(raiz) or not ruta.is_file():
            abort(404)
        tipos = {
            TipoArchivo.JPG: "image/jpeg",
            TipoArchivo.PNG: "image/png",
            TipoArchivo.PDF: "application/pdf",
        }
        respuesta = send_file(
            ruta,
            mimetype=tipos.get(filmina.archivo.tipo, "application/octet-stream"),
            download_name=filmina.archivo.nombre,
            as_attachment=(
                request.args.get("descargar") == "1"
                or filmina.archivo.tipo not in tipos
            ),
            conditional=True,
        )
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        return respuesta

    @controlador.get("/filminas/nueva")
    def mostrar_formulario() -> str:
        tags = repositorio_tags.listar() if repositorio_tags is not None else []
        return render_template("filminas/formulario.html", tags=tags)

    def mostrar_error(mensaje, estado):
        if request.form:
            tags = repositorio_tags.listar() if repositorio_tags is not None else []
            return (
                render_template(
                    "filminas/formulario.html",
                    tags=tags,
                    error=mensaje,
                    datos=request.form,
                    seleccionados=request.form.getlist("tag_identificador"),
                ),
                estado,
            )
        return jsonify({"error": mensaje}), estado

    @controlador.post("/filminas")
    def crear_filmina() -> Any:
        try:
            datos = request.form or request.get_json(silent=True)

            if datos is None:
                return jsonify({"error": "Datos inválidos"}), 400

            identificadores_recibidos = (
                request.form.getlist("tag_identificador")
                if request.form
                else datos.get("tags", [])
            )
            identificadores = [
                identificador
                for identificador in identificadores_recibidos
                if identificador
            ]
            if len(set(identificadores)) != len(identificadores):
                raise ValueError("No puedes seleccionar el mismo tag más de una vez.")

            if repositorio_tags is not None:
                tags = []
                for identificador in identificadores:
                    tag = repositorio_tags.obtener_por_identificador(identificador)
                    if tag is None:
                        raise ValueError(f"El tag {identificador} no existe")
                    tags.append(tag)
            else:
                tags = identificadores

            archivo_subido = request.files.get("archivo")
            archivo = None

            if archivo_subido is not None and archivo_subido.filename:
                extension = Path(archivo_subido.filename).suffix[1:].upper()

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
                tags=tags,
            )

        except (KeyError, TypeError, ValueError) as error:
            return mostrar_error(str(error), 400)
        except IntegrityError:
            return mostrar_error(
                "No se pudo guardar la filmina por un conflicto con los datos existentes.",
                409,
            )

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
