"""Manejo de la conexion a SQL Server via pyodbc.

Se abre una conexion por request (guardada en flask.g) y se cierra
automaticamente al terminar el request.
"""
import pyodbc
from flask import current_app, g


def obtener_conexion():
    """Devuelve la conexion pyodbc del request actual, creandola si no existe."""
    if "db_conn" not in g:
        cfg = current_app.config
        cadena = (
            f"DRIVER={cfg['DB_DRIVER']};"
            f"SERVER={cfg['DB_SERVER']};"
            f"DATABASE={cfg['DB_NAME']};"
            f"UID={cfg['DB_USER']};"
            f"PWD={cfg['DB_PASSWORD']};"
            "TrustServerCertificate=yes;"
        )
        g.db_conn = pyodbc.connect(cadena)
    return g.db_conn


def cerrar_conexion(_exception=None):
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(cerrar_conexion)
