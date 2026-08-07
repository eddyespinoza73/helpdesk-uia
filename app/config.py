"""Configuracion de la app, cargada desde variables de entorno (.env)."""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = os.environ.get("FLASK_DEBUG", "False") == "True"

    DB_SERVER = os.environ["DB_SERVER"]
    DB_NAME = os.environ["DB_NAME"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_DRIVER = os.environ["DB_DRIVER"]
