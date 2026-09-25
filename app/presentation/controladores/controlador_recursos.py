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
from app.domain.enums import TipoArchivo, TipoRecurso


def crear_controlador_recursos(gestor, repositorio, filminas, bocetos, storage):
    controlador = Blueprint("recursos", __name__, template_folder="../templates")

    def formulario(error=None, estado=200):
        return (
            render_template(
                "recursos/formulario.html",
                error=error,
                datos=request.form,
                tipos=list(TipoRecurso),
                filminas=filminas.listar(),
                bocetos=bocetos.listar(),
            ),
            estado,
        )

    @controlador.get("/recursos/nuevo")
    def nuevo():
        return formulario()

    @controlador.get("/recursos")
    def listar():
        return render_template("recursos/listado.html", recursos=repositorio.listar())

    @controlador.get("/recursos/<identificador>")
    def detalle(identificador):
        recurso = repositorio.obtener_por_identificador(identificador)
        if recurso is None:
            abort(404)
        return render_template("recursos/detalle.html", recurso=recurso)

    @controlador.get("/recursos/<identificador>/archivo")
    def archivo(identificador):
        recurso = repositorio.obtener_por_identificador(identificador)
        if recurso is None or recurso.archivo is None:
            abort(404)
        raiz = Path(storage).resolve()
        ruta = (raiz / recurso.archivo.ruta).resolve()
        if not ruta.is_relative_to(raiz) or not ruta.is_file():
            abort(404)
        tipos = {
            TipoArchivo.PNG: "image/png",
            TipoArchivo.JPG: "image/jpeg",
            TipoArchivo.PDF: "application/pdf",
        }
        respuesta = send_file(
            ruta,
            mimetype=tipos.get(recurso.archivo.tipo, "application/octet-stream"),
            download_name=recurso.archivo.nombre,
            as_attachment=request.args.get("descargar") == "1"
            or recurso.archivo.tipo not in tipos,
        )
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        return respuesta

    @controlador.post("/recursos")
    def registrar():
        try:
            datos = (
                request.form
                if request.mimetype != "application/json"
                else request.get_json(silent=True)
            )
            if not isinstance(datos, dict) and not request.form:
                raise ValueError("Datos inválidos")
            asociaciones = {}
            for nombre, repo in (("filmina", filminas), ("boceto", bocetos)):
                identificador = datos.get(nombre + "_identificador")
                if identificador:
                    if not isinstance(identificador, str):
                        raise ValueError("Identificador de asociación inválido")
                    elemento = repo.obtener_por_identificador(identificador)
                    if elemento is None:
                        raise ValueError("El elemento seleccionado no existe")
                    asociaciones[nombre] = elemento
            adjunto = request.files.get("archivo")
            archivo_datos = None
            if adjunto and adjunto.filename:
                nombre = secure_filename(adjunto.filename)
                archivo_datos = dict(
                    contenido=adjunto.read(),
                    nombre_original=nombre,
                    tipo=TipoArchivo(Path(nombre).suffix[1:].upper()),
                )
            recurso = gestor.ejecutar(
                nombre=datos.get("nombre"),
                tipo=datos.get("tipo"),
                archivo=archivo_datos,
                **asociaciones
            )
        except (ValueError, TypeError, KeyError) as error:
            return (
                formulario(str(error), 400)
                if request.form
                else (jsonify(error=str(error)), 400)
            )
        except IntegrityError:
            mensaje = "No se pudo guardar el recurso por un conflicto con los datos existentes"
            return (
                formulario(mensaje, 409)
                if request.form
                else (jsonify(error=mensaje), 409)
            )
        if request.form:
            return redirect(
                url_for("recursos.detalle", identificador=recurso.identificador)
            )
        return (
            jsonify(
                identificador=recurso.identificador,
                nombre=recurso.nombre,
                tipo=recurso.tipo,
            ),
            201,
        )

    return controlador
