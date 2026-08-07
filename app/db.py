"""Manejo de la conexion a SQL Server via pyodbc.

Se abre una conexion por request (guardada en flask.g) y se cierra
automaticamente al terminar el request.

Compatible con Azure SQL serverless: aplica encriptacion obligatoria,
timeout extendido y un retry ante fallos de despertar de la BD.
"""
import time
import pyodbc
from flask import current_app, g


def _armar_cadena():
    """Arma el connection string desde la configuracion de la app."""
    cfg = current_app.config
    return (
        f"DRIVER={cfg['DB_DRIVER']};"
        f"SERVER={cfg['DB_SERVER']};"
        f"DATABASE={cfg['DB_NAME']};"
        f"UID={cfg['DB_USER']};"
        f"PWD={cfg['DB_PASSWORD']};"
        "Encrypt=yes;"                 # Azure SQL exige conexion encriptada
        "TrustServerCertificate=yes;"
        "Connection Timeout=60;"       # Azure serverless puede tardar en despertar
    )


def obtener_conexion():
    """Devuelve la conexion pyodbc del request actual, creandola si no existe.

    Si la primera conexion falla por timeout o por que la BD esta
    despertandose (error 40613 en Azure), reintenta una vez tras 10 segundos.
    """
    if "db_conn" not in g:
        cadena = _armar_cadena()
        try:
            g.db_conn = pyodbc.connect(cadena)
        except pyodbc.OperationalError as err:
            mensaje = str(err).lower()
            # Solo reintentar en los casos tipicos de Azure serverless dormida
            if "timeout" in mensaje or "not currently available" in mensaje:
                current_app.logger.warning(
                    "Primera conexion a Azure SQL fallo por timeout, "
                    "reintentando en 10s (la BD serverless se esta despertando)."
                )
                time.sleep(10)
                g.db_conn = pyodbc.connect(cadena)
            else:
                raise
    return g.db_conn


def cerrar_conexion(_exception=None):
    """Cierra la conexion al terminar el request."""
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def init_app(app):
    """Registra el cierre automatico de la conexion al final de cada request."""
    app.teardown_appcontext(cerrar_conexion)