from datetime import date
from pathlib import Path
from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from app.domain.enums import TipoArchivo


def crear_controlador_bocetos(
    gestor, repositorio, repositorio_tags, repositorio_filminas, storage
):
    controlador = Blueprint("bocetos", __name__, template_folder="../templates")

    def formulario(error=None, estado=200):
        return (
            render_template(
                "bocetos/formulario.html",
                error=error,
                datos=request.form,
                seleccionados=request.form.getlist("tag_identificador"),
                tags=repositorio_tags.listar(),
                filminas=repositorio_filminas.listar(),
            ),
            estado,
        )

    @controlador.get("/bocetos/nuevo")
    def nuevo():
        return formulario()

    @controlador.get("/bocetos")
    def listar():
        return render_template("bocetos/listado.html", bocetos=repositorio.listar())

    @controlador.get("/bocetos/<identificador>")
    def detalle(identificador):
        boceto = repositorio.obtener_por_identificador(identificador)
        if boceto is None:
            abort(404)
        return render_template("bocetos/detalle.html", boceto=boceto)

    @controlador.get("/bocetos/<identificador>/archivo")
    def archivo(identificador):
        boceto = repositorio.obtener_por_identificador(identificador)
        if boceto is None or boceto.archivo is None:
            abort(404)
        raiz = Path(storage).resolve()
        ruta = (raiz / boceto.archivo.ruta).resolve()
        if not ruta.is_relative_to(raiz) or not ruta.is_file():
            abort(404)
        tipos = {
            TipoArchivo.PNG: "image/png",
            TipoArchivo.JPG: "image/jpeg",
            TipoArchivo.PDF: "application/pdf",
        }
        respuesta = send_file(
            ruta,
            mimetype=tipos.get(boceto.archivo.tipo, "application/octet-stream"),
            download_name=boceto.archivo.nombre,
            as_attachment=request.args.get("descargar") == "1"
            or boceto.archivo.tipo not in tipos,
        )
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        return respuesta

    @controlador.post("/bocetos")
    def registrar():
        try:
            datos = (
                request.form
                if request.mimetype != "application/json"
                else request.get_json(silent=True)
            )
            if not isinstance(datos, dict) and not request.form:
                raise ValueError("Datos inválidos")
            ids = (
                request.form.getlist("tag_identificador")
                if request.form
                else datos.get("tags", [])
            )
            if not isinstance(ids, list) or any(not isinstance(i, str) for i in ids):
                raise ValueError("Tags inválidos")
            ids = [i for i in ids if i]
            if len(ids) > 3 or len(ids) != len(set(ids)):
                raise ValueError("Selecciona hasta tres tags distintos")
            tags = []
            for identificador in ids:
                tag = repositorio_tags.obtener_por_identificador(identificador)
                if tag is None:
                    raise ValueError("El tag seleccionado no existe")
                tags.append(tag)
            filmina = None
            if datos.get("filmina_identificador"):
                filmina = repositorio_filminas.obtener_por_identificador(
                    datos["filmina_identificador"]
                )
                if filmina is None:
                    raise ValueError("La filmina seleccionada no existe")
            adjunto = request.files.get("archivo")
            archivo_datos = None
            if adjunto and adjunto.filename:
                nombre = secure_filename(adjunto.filename)
                archivo_datos = dict(
                    contenido=adjunto.read(),
                    nombre_original=nombre,
                    tipo=TipoArchivo(Path(nombre).suffix[1:].upper()),
                )
            boceto = gestor.ejecutar(
                descripcion=datos.get("descripcion"),
                fecha=(
                    date.fromisoformat(datos["fecha"]) if datos.get("fecha") else None
                ),
                archivo=archivo_datos,
                tags=tags,
                filmina=filmina,
            )
        except (ValueError, TypeError, KeyError) as error:
            return (
                formulario(str(error), 400)
                if request.form
                else (jsonify(error=str(error)), 400)
            )
        except IntegrityError:
            mensaje = (
                "No se pudo guardar el boceto por un conflicto con los datos existentes"
            )
            return (
                formulario(mensaje, 409)
                if request.form
                else (jsonify(error=mensaje), 409)
            )
        if request.form:
            return redirect(
                url_for("bocetos.detalle", identificador=boceto.identificador)
            )
        return (
            jsonify(
                identificador=boceto.identificador,
                descripcion=boceto.descripcion,
                fecha=boceto.fecha.isoformat() if boceto.fecha else None,
            ),
            201,
        )

    return controlador
