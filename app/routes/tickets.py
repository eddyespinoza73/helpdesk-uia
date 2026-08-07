"""Rutas de tickets: dashboard, listado, creacion y detalle/cambio de estado."""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from app.db import obtener_conexion
from app.models.ticket import (
    actualizar_estado,
    crear_ticket,
    listar_tickets,
    obtener_catalogos,
    obtener_estados,
    obtener_historial,
    obtener_tecnicos,
    obtener_ticket_detalle,
)
from app.models.usuario import obtener_id_tecnico
from app.utils.decoradores import login_requerido

tickets_bp = Blueprint("tickets", __name__)

ROLES_CON_VISTA_COMPLETA = ("Administrador", "Tecnico")


def _id_usuario_para_filtro():
    """Los roles Administrador/Tecnico ven todos los tickets; el rol Usuario solo los propios."""
    if session.get("rol") in ROLES_CON_VISTA_COMPLETA:
        return None
    return session["id_usuario"]


@tickets_bp.route("/dashboard")
@login_requerido
def dashboard():
    conn = obtener_conexion()
    cursor = conn.cursor()
    tickets = listar_tickets(cursor, _id_usuario_para_filtro())

    resumen = {
        "total": len(tickets),
        "abiertos": sum(1 for t in tickets if t.estado in ("Abierto", "Reabierto")),
        "en_proceso": sum(1 for t in tickets if t.estado == "En Proceso"),
        "resueltos": sum(1 for t in tickets if t.estado in ("Resuelto", "Cerrado")),
    }
    return render_template("dashboard.html", resumen=resumen, recientes=tickets[:5])


@tickets_bp.route("/tickets")
@login_requerido
def lista():
    conn = obtener_conexion()
    cursor = conn.cursor()
    tickets = listar_tickets(cursor, _id_usuario_para_filtro())
    return render_template("tickets_lista.html", tickets=tickets)


@tickets_bp.route("/tickets/nuevo", methods=["GET", "POST"])
@login_requerido
def nuevo():
    conn = obtener_conexion()
    cursor = conn.cursor()
    categorias, prioridades = obtener_catalogos(cursor)

    datos = {"titulo": "", "descripcion": "", "id_categoria": "", "id_prioridad": ""}

    if request.method == "POST":
        datos["titulo"] = request.form.get("titulo", "").strip()
        datos["descripcion"] = request.form.get("descripcion", "").strip()
        datos["id_categoria"] = request.form.get("id_categoria", "")
        datos["id_prioridad"] = request.form.get("id_prioridad", "")

        if not datos["titulo"] or not datos["descripcion"] or not datos["id_categoria"] or not datos["id_prioridad"]:
            flash("Completá todos los campos.", "error")
        elif len(datos["titulo"]) < 5:
            flash("El título debe tener al menos 5 caracteres.", "error")
        else:
            crear_ticket(
                cursor, datos["titulo"], datos["descripcion"], session["id_usuario"],
                int(datos["id_categoria"]), int(datos["id_prioridad"]),
            )
            conn.commit()
            flash("Ticket creado correctamente.", "ok")
            return redirect(url_for("tickets.lista"))

    return render_template("ticket_nuevo.html", categorias=categorias, prioridades=prioridades, datos=datos)


@tickets_bp.route("/tickets/<int:id_ticket>", methods=["GET", "POST"])
@login_requerido
def detalle(id_ticket):
    conn = obtener_conexion()
    cursor = conn.cursor()
    ticket = obtener_ticket_detalle(cursor, id_ticket)
    if ticket is None:
        abort(404)

    puede_gestionar = session.get("rol") in ROLES_CON_VISTA_COMPLETA
    es_propio = ticket.id_usuario == session["id_usuario"]

    if not puede_gestionar and not es_propio:
        flash("No tenés permiso para ver ese ticket.", "error")
        return redirect(url_for("tickets.lista"))

    if request.method == "POST":
        if not puede_gestionar:
            flash("No tenés permiso para modificar este ticket.", "error")
            return redirect(url_for("tickets.detalle", id_ticket=id_ticket))

        id_estado_nuevo = request.form.get("id_estado", "")
        id_tecnico_asignar = request.form.get("id_tecnico") or None
        comentario = request.form.get("comentario", "").strip() or None

        if not id_estado_nuevo:
            flash("Elegí un estado.", "error")
        else:
            id_tecnico_autor = obtener_id_tecnico(cursor, session["id_usuario"])
            try:
                actualizar_estado(
                    cursor,
                    id_ticket,
                    ticket.id_estado,
                    int(id_estado_nuevo),
                    int(id_tecnico_asignar) if id_tecnico_asignar else None,
                    id_tecnico_autor,
                    comentario,
                )
            except Exception:
                conn.rollback()
                raise
            conn.commit()
            flash("Ticket actualizado correctamente.", "ok")
            return redirect(url_for("tickets.detalle", id_ticket=id_ticket))

    historial = obtener_historial(cursor, id_ticket)
    estados = obtener_estados(cursor)
    tecnicos = obtener_tecnicos(cursor) if ticket.id_tecnico is None else []

    return render_template(
        "ticket_detalle.html",
        ticket=ticket,
        historial=historial,
        estados=estados,
        tecnicos=tecnicos,
        puede_gestionar=puede_gestionar,
    )
