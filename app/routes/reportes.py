"""Rutas de los 2 reportes: por estado y de cumplimiento de SLA."""
from flask import Blueprint, render_template

from app.db import obtener_conexion
from app.models.reporte import reporte_por_estado, reporte_sla, reporte_sla_por_tecnico
from app.utils.decoradores import login_requerido

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@reportes_bp.route("/estado-prioridad")
@login_requerido
def estado():
    conn = obtener_conexion()
    cursor = conn.cursor()
    por_estado, por_prioridad = reporte_por_estado(cursor)
    return render_template("reporte_estado.html", por_estado=por_estado, por_prioridad=por_prioridad)


@reportes_bp.route("/sla")
@login_requerido
def sla():
    conn = obtener_conexion()
    cursor = conn.cursor()
    filas, resumen = reporte_sla(cursor)
    por_tecnico = reporte_sla_por_tecnico(cursor)
    return render_template("reporte_sla.html", filas=filas, resumen=resumen, por_tecnico=por_tecnico)
