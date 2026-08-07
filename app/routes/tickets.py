"""Rutas de tickets: dashboard, listado y creacion."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.db import obtener_conexion
from app.models.ticket import crear_ticket, listar_tickets, obtener_catalogos
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
