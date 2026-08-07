"""Fija las contraseñas de los usuarios de prueba (hash bcrypt real en la BD).

Uso: python seed_passwords.py
"""
import os

import bcrypt
import pyodbc
from dotenv import load_dotenv

load_dotenv()

# Todos los usuarios de prueba comparten la misma contraseña demo,
# asi se puede iniciar sesion con cualquier rol para la exposicion.
USUARIOS_DEMO = {
    "ana.ramirez@empresa.cr": "Demo123!",
    "luis.vargas@empresa.cr": "Demo123!",
    "marta.solis@empresa.cr": "Demo123!",
    "carlos.mora@empresa.cr": "Demo123!",
    "sofia.jimenez@empresa.cr": "Demo123!",
    "diego.castro@empresa.cr": "Demo123!",
}


def main():
    cadena = (
        f"DRIVER={os.environ['DB_DRIVER']};"
        f"SERVER={os.environ['DB_SERVER']};"
        f"DATABASE={os.environ['DB_NAME']};"
        f"UID={os.environ['DB_USER']};"
        f"PWD={os.environ['DB_PASSWORD']};"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(cadena)
    cursor = conn.cursor()

    for correo, password in USUARIOS_DEMO.items():
        hash_bcrypt = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            """
            UPDATE Usuario
               SET contrasena_hash = ?, intentos_fallidos = 0, bloqueado = 0
             WHERE correo = ?
            """,
            hash_bcrypt,
            correo,
        )
        print(f"Actualizado: {correo}")

    conn.commit()
    conn.close()
    print("Listo.")


if __name__ == "__main__":
    main()
