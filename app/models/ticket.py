"""Consultas relacionadas a tickets: listado, catalogos y creacion."""

_SELECT_TICKETS = """
    SELECT t.id_ticket, t.titulo, t.fecha_apertura, t.fecha_cierre,
           e.nombre AS estado, p.nombre AS prioridad, c.nombre AS categoria,
           us.nombre AS solicitante, tec_u.nombre AS tecnico
    FROM Ticket t
    JOIN Estado e ON e.id_estado = t.id_estado
    JOIN Prioridad p ON p.id_prioridad = t.id_prioridad
    JOIN Categoria c ON c.id_categoria = t.id_categoria
    JOIN Usuario us ON us.id_usuario = t.id_usuario
    LEFT JOIN Tecnico tec ON tec.id_tecnico = t.id_tecnico
    LEFT JOIN Usuario tec_u ON tec_u.id_usuario = tec.id_usuario
"""


def listar_tickets(cursor, id_usuario=None):
    """Si se pasa id_usuario trae solo los tickets de ese usuario (rol Usuario).
    Si es None trae todos (rol Administrador o Tecnico). Solo tickets activos."""
    if id_usuario is not None:
        cursor.execute(
            _SELECT_TICKETS + " WHERE t.activo = 1 AND t.id_usuario = ? ORDER BY t.fecha_apertura DESC",
            id_usuario,
        )
    else:
        cursor.execute(_SELECT_TICKETS + " WHERE t.activo = 1 ORDER BY t.fecha_apertura DESC")
    return cursor.fetchall()


def obtener_catalogos(cursor):
    """Categorias y prioridades activas, para llenar el formulario de ticket nuevo."""
    cursor.execute("SELECT id_categoria, nombre FROM Categoria WHERE activo = 1 ORDER BY nombre")
    categorias = cursor.fetchall()
    cursor.execute("SELECT id_prioridad, nombre FROM Prioridad WHERE activo = 1 ORDER BY orden")
    prioridades = cursor.fetchall()
    return categorias, prioridades


def crear_ticket(cursor, titulo, descripcion, id_usuario, id_categoria, id_prioridad):
    """Inserta el ticket en estado Abierto (id_estado = 1). El caller hace conn.commit()."""
    cursor.execute(
        """
        INSERT INTO Ticket
            (titulo, descripcion, id_usuario, id_categoria, id_prioridad,
             id_estado, fecha_apertura, activo, fecha_creacion, fecha_modificacion)
        VALUES (?, ?, ?, ?, ?, 1, SYSDATETIME(), 1, SYSDATETIME(), SYSDATETIME())
        """,
        titulo,
        descripcion,
        id_usuario,
        id_categoria,
        id_prioridad,
    )


def obtener_ticket_detalle(cursor, id_ticket):
    """Trae un ticket con toda la informacion para la vista de detalle."""
    cursor.execute(
        """
        SELECT t.id_ticket, t.titulo, t.descripcion, t.fecha_apertura, t.fecha_cierre,
               t.id_usuario, t.id_tecnico, t.id_estado,
               e.nombre AS estado, e.es_final,
               p.nombre AS prioridad, c.nombre AS categoria,
               us.nombre AS solicitante, us.correo AS solicitante_correo,
               tec_u.nombre AS tecnico
        FROM Ticket t
        JOIN Estado e ON e.id_estado = t.id_estado
        JOIN Prioridad p ON p.id_prioridad = t.id_prioridad
        JOIN Categoria c ON c.id_categoria = t.id_categoria
        JOIN Usuario us ON us.id_usuario = t.id_usuario
        LEFT JOIN Tecnico tec ON tec.id_tecnico = t.id_tecnico
        LEFT JOIN Usuario tec_u ON tec_u.id_usuario = tec.id_usuario
        WHERE t.id_ticket = ? AND t.activo = 1
        """,
        id_ticket,
    )
    return cursor.fetchone()


def obtener_historial(cursor, id_ticket):
    """Cambios de estado del ticket, del mas viejo al mas nuevo (para la linea de tiempo)."""
    cursor.execute(
        """
        SELECT h.fecha_cambio, h.comentario,
               ea.nombre AS estado_anterior, en.nombre AS estado_nuevo,
               tec_u.nombre AS tecnico
        FROM HistorialTicket h
        LEFT JOIN Estado ea ON ea.id_estado = h.id_estado_anterior
        JOIN Estado en ON en.id_estado = h.id_estado_nuevo
        LEFT JOIN Tecnico tec ON tec.id_tecnico = h.id_tecnico
        LEFT JOIN Usuario tec_u ON tec_u.id_usuario = tec.id_usuario
        WHERE h.id_ticket = ? AND h.activo = 1
        ORDER BY h.fecha_cambio ASC
        """,
        id_ticket,
    )
    return cursor.fetchall()


def obtener_estados(cursor):
    cursor.execute("SELECT id_estado, nombre FROM Estado WHERE activo = 1 ORDER BY id_estado")
    return cursor.fetchall()


def obtener_tecnicos(cursor):
    cursor.execute(
        """
        SELECT tec.id_tecnico, u.nombre
        FROM Tecnico tec
        JOIN Usuario u ON u.id_usuario = tec.id_usuario
        WHERE tec.activo = 1
        ORDER BY u.nombre
        """
    )
    return cursor.fetchall()


def actualizar_estado(cursor, id_ticket, id_estado_anterior, id_estado_nuevo,
                       id_tecnico_asignar, id_tecnico_autor, comentario):
    """Cambia el estado del ticket, asigna tecnico si corresponde y deja registro
    en HistorialTicket. El caller es responsable de commit()/rollback() — las
    3 sentencias corren en la misma conexion/transaccion."""
    if id_tecnico_asignar is not None:
        cursor.execute(
            "UPDATE Ticket SET id_tecnico = ? WHERE id_ticket = ? AND id_tecnico IS NULL",
            id_tecnico_asignar,
            id_ticket,
        )

    cursor.execute(
        """
        UPDATE Ticket
           SET id_estado = ?,
               fecha_cierre = CASE
                   WHEN (SELECT es_final FROM Estado WHERE id_estado = ?) = 1
                   THEN SYSDATETIME() ELSE fecha_cierre END,
               fecha_modificacion = SYSDATETIME()
         WHERE id_ticket = ?
        """,
        id_estado_nuevo,
        id_estado_nuevo,
        id_ticket,
    )

    cursor.execute(
        """
        INSERT INTO HistorialTicket
            (id_ticket, id_estado_anterior, id_estado_nuevo, id_tecnico, comentario,
             fecha_cambio, activo, fecha_creacion, fecha_modificacion)
        VALUES (?, ?, ?, ?, ?, SYSDATETIME(), 1, SYSDATETIME(), SYSDATETIME())
        """,
        id_ticket,
        id_estado_anterior,
        id_estado_nuevo,
        id_tecnico_autor,
        comentario,
    )
