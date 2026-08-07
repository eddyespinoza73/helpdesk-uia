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
