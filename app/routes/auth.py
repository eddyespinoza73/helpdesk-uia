"""Rutas de autenticacion: login, logout y raiz del sitio."""
import bcrypt
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.db import obtener_conexion
from app.models.usuario import obtener_usuario_por_correo, procesar_login
from app.utils.decoradores import login_requerido

auth_bp = Blueprint("auth", __name__)

MENSAJES_RESULTADO = {
    "CREDENCIALES": "Correo o contraseña incorrectos.",
    "BLOQUEADO": "Tu cuenta está bloqueada por múltiples intentos fallidos. Contactá a un administrador.",
    "INACTIVO": "Tu cuenta está inactiva.",
}


@auth_bp.route("/")
def raiz():
    if "id_usuario" in session:
        return redirect(url_for("tickets.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "id_usuario" in session:
        return redirect(url_for("tickets.dashboard"))

    correo = ""
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")

        if not correo or not password:
            flash("Completá correo y contraseña.", "error")
            return render_template("login.html", correo=correo)

        conn = obtener_conexion()
        cursor = conn.cursor()
        usuario = obtener_usuario_por_correo(cursor, correo)

        password_valido = False
        if usuario is not None:
            password_valido = bcrypt.checkpw(
                password.encode("utf-8"), usuario.contrasena_hash.encode("utf-8")
            )

        resultado, id_usuario = procesar_login(cursor, correo, password_valido)
        conn.commit()

        if resultado == "OK":
            session["id_usuario"] = id_usuario
            session["nombre"] = usuario.nombre
            session["rol"] = usuario.nombre_rol
            return redirect(url_for("tickets.dashboard"))

        flash(MENSAJES_RESULTADO.get(resultado, "No se pudo iniciar sesión."), "error")

    return render_template("login.html", correo=correo)


@auth_bp.route("/logout")
@login_requerido
def logout():
    session.clear()
    flash("Sesión cerrada.", "ok")
    return redirect(url_for("auth.login"))
