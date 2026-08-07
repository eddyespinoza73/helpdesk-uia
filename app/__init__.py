"""Factory de la aplicacion Flask."""
import pyodbc
from flask import Flask, render_template

from app import db as db_module
from app.config import Config
from app.routes.auth import auth_bp
from app.routes.reportes import reportes_bp
from app.routes.tickets import tickets_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db_module.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(reportes_bp)

    @app.errorhandler(404)
    def pagina_no_encontrada(_error):
        return render_template("error_404.html"), 404

    @app.errorhandler(pyodbc.Error)
    def error_base_de_datos(error):
        app.logger.error("Error de conexion/consulta a SQL Server: %s", error)
        return render_template("error_500.html"), 503

    @app.errorhandler(500)
    def error_interno(_error):
        return render_template("error_500.html"), 500

    return app
