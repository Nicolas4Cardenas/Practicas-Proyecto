"""US9 - Estadísticas básicas de los reportes."""
import sqlite3

from . import usuarios
from .estados import ESTADOS


def reportes_por_estado(conn: sqlite3.Connection, profesional_id: int,
                        zona: str | None = None,
                        tipo_plaga: str | None = None) -> dict[str, int]:
    """Cuenta los reportes por estado, con filtros opcionales (US9).

    Siempre incluye los cuatro estados (con 0 si no hay reportes).
    Los filtros no distinguen mayúsculas de minúsculas.

    Raises:
        ErrorPermiso: El usuario no es profesional.
    """
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    sql = "SELECT estado, COUNT(*) AS total FROM reporte WHERE 1=1"
    params: list[str] = []
    if zona:
        sql += " AND zona = ? COLLATE NOCASE"
        params.append(zona.strip())
    if tipo_plaga:
        sql += " AND tipo_plaga = ? COLLATE NOCASE"
        params.append(tipo_plaga.strip())
    sql += " GROUP BY estado"
    conteo = {e: 0 for e in ESTADOS}
    for fila in conn.execute(sql, params):
        conteo[fila["estado"]] = fila["total"]
    return conteo
