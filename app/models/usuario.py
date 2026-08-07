"""Consultas relacionadas al login y los datos de usuario."""


def obtener_usuario_por_correo(cursor, correo):
    """Trae el usuario junto con el nombre de su rol y departamento."""
    cursor.execute(
        """
        SELECT u.id_usuario, u.nombre, u.correo, u.contrasena_hash,
               u.activo, u.bloqueado, u.id_rol, r.nombre AS nombre_rol,
               u.id_departamento, d.nombre AS nombre_departamento
        FROM Usuario u
        JOIN Rol r ON r.id_rol = u.id_rol
        JOIN Departamento d ON d.id_departamento = u.id_departamento
        WHERE u.correo = ?
        """,
        correo,
    )
    return cursor.fetchone()


def procesar_login(cursor, correo, password_valido):
    """Llama a sp_procesar_login y devuelve (resultado, id_usuario).

    pyodbc no soporta bien parametros OUTPUT de T-SQL directamente, por eso
    el SP se ejecuta dentro de un bloque que declara variables locales y
    despues las selecciona como si fuera un resultado normal.
    """
    cursor.execute(
        """
        DECLARE @resultado NVARCHAR(20), @id_usuario INT;
        EXEC sp_procesar_login
            @correo = ?,
            @password_valido = ?,
            @resultado = @resultado OUTPUT,
            @id_usuario = @id_usuario OUTPUT;
        SELECT @resultado AS resultado, @id_usuario AS id_usuario;
        """,
        correo,
        password_valido,
    )
    fila = cursor.fetchone()
    return fila.resultado, fila.id_usuario


def obtener_id_tecnico(cursor, id_usuario):
    """Devuelve el id_tecnico asociado a un usuario, o None si no es tecnico
    (ej. un Administrador que no tiene fila en la tabla Tecnico)."""
    cursor.execute("SELECT id_tecnico FROM Tecnico WHERE id_usuario = ? AND activo = 1", id_usuario)
    fila = cursor.fetchone()
    return fila.id_tecnico if fila else None


def obtener_usuario_por_id(cursor, id_usuario):
    cursor.execute(
        """
        SELECT u.id_usuario, u.nombre, u.correo, u.id_rol, r.nombre AS nombre_rol,
               u.id_departamento, d.nombre AS nombre_departamento
        FROM Usuario u
        JOIN Rol r ON r.id_rol = u.id_rol
        JOIN Departamento d ON d.id_departamento = u.id_departamento
        WHERE u.id_usuario = ?
        """,
        id_usuario,
    )
    return cursor.fetchone()
