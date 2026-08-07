"""Decoradores de autorizacion para las rutas protegidas."""
from functools import wraps

from flask import flash, redirect, session, url_for


def login_requerido(vista):
    """Exige que haya una sesion activa; si no, redirige al login."""

    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "id_usuario" not in session:
            flash("Iniciá sesión para continuar.", "error")
            return redirect(url_for("auth.login"))
        return vista(*args, **kwargs)

    return envoltura
