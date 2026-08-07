"""Consultas de los 2 reportes: por estado y de cumplimiento de SLA."""


def reporte_por_estado(cursor):
    """Cantidad de tickets activos agrupados por estado y por prioridad."""
    cursor.execute(
        """
        SELECT e.nombre AS estado, COUNT(t.id_ticket) AS total
        FROM Estado e
        LEFT JOIN Ticket t ON t.id_estado = e.id_estado AND t.activo = 1
        GROUP BY e.nombre, e.id_estado
        ORDER BY e.id_estado
        """
    )
    por_estado = cursor.fetchall()

    cursor.execute(
        """
        SELECT p.nombre AS prioridad, COUNT(t.id_ticket) AS total
        FROM Prioridad p
        LEFT JOIN Ticket t ON t.id_prioridad = p.id_prioridad AND t.activo = 1
        GROUP BY p.nombre, p.orden
        ORDER BY p.orden
        """
    )
    por_prioridad = cursor.fetchall()
    return por_estado, por_prioridad


_MINUTOS_TRANSCURRIDOS = """DATEDIFF(MINUTE, t.fecha_apertura, COALESCE(t.fecha_cierre, SYSDATETIME()))"""


def reporte_sla(cursor):
    """Cumplimiento de SLA por ticket: horas transcurridas vs horas_compromiso.

    Las horas transcurridas se calculan en minutos y se convierten a horas
    (DATEDIFF(MINUTE,...) / 60.0) en vez de DATEDIFF(HOUR,...), que trunca
    contando cruces de hora en reloj y no el tiempo real transcurrido
    (ej: 23:59 a 00:01 marcaria 1 hora con DATEDIFF(HOUR) cuando en
    realidad pasaron 2 minutos).

    Para tickets abiertos se compara contra la hora actual (SYSDATETIME);
    para tickets cerrados se compara contra fecha_cierre.
    """
    cursor.execute(
        f"""
        SELECT t.id_ticket, t.titulo, p.nombre AS prioridad, c.nombre AS categoria,
               e.nombre AS estado, sla.horas_compromiso,
               CAST({_MINUTOS_TRANSCURRIDOS} AS DECIMAL(10, 2)) / 60.0 AS horas_transcurridas,
               CASE WHEN CAST({_MINUTOS_TRANSCURRIDOS} AS DECIMAL(10, 2)) / 60.0 <= sla.horas_compromiso
                    THEN 1 ELSE 0 END AS cumple
        FROM Ticket t
        JOIN Prioridad p ON p.id_prioridad = t.id_prioridad
        JOIN Categoria c ON c.id_categoria = t.id_categoria
        JOIN Estado e ON e.id_estado = t.id_estado
        JOIN SLA sla ON sla.id_categoria = t.id_categoria
                     AND sla.id_prioridad = t.id_prioridad
                     AND sla.activo = 1
        WHERE t.activo = 1
        ORDER BY t.fecha_apertura DESC
        """
    )
    filas = cursor.fetchall()

    total = len(filas)
    cumplidos = sum(1 for f in filas if f.cumple == 1)
    resumen = {
        "total": total,
        "cumplidos": cumplidos,
        "incumplidos": total - cumplidos,
        "porcentaje": round(100 * cumplidos / total, 1) if total else 0,
    }
    return filas, resumen


def reporte_sla_por_tecnico(cursor):
    """Cumplimiento de SLA agregado por tecnico (solo tickets ya asignados)."""
    cursor.execute(
        f"""
        SELECT tec_u.nombre AS tecnico,
               CASE WHEN CAST({_MINUTOS_TRANSCURRIDOS} AS DECIMAL(10, 2)) / 60.0 <= sla.horas_compromiso
                    THEN 1 ELSE 0 END AS cumple
        FROM Ticket t
        JOIN Tecnico tec ON tec.id_tecnico = t.id_tecnico
        JOIN Usuario tec_u ON tec_u.id_usuario = tec.id_usuario
        JOIN SLA sla ON sla.id_categoria = t.id_categoria
                     AND sla.id_prioridad = t.id_prioridad
                     AND sla.activo = 1
        WHERE t.activo = 1 AND t.id_tecnico IS NOT NULL
        """
    )
    filas = cursor.fetchall()

    por_tecnico = {}
    for f in filas:
        stats = por_tecnico.setdefault(f.tecnico, {"total": 0, "cumplidos": 0})
        stats["total"] += 1
        stats["cumplidos"] += f.cumple

    resultado = []
    for tecnico, stats in sorted(por_tecnico.items()):
        resultado.append(
            {
                "tecnico": tecnico,
                "total": stats["total"],
                "cumplidos": stats["cumplidos"],
                "porcentaje": round(100 * stats["cumplidos"] / stats["total"], 1) if stats["total"] else 0,
            }
        )
    return resultado
