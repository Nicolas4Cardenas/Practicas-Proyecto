"""US7 - Consulta y lectura de notificaciones del campesino."""
import sqlite3

from .errores import ErrorNoEncontrado, ErrorPermiso


def listar_notificaciones(conn: sqlite3.Connection, usuario_id: int,
                          solo_no_leidas: bool = False) -> list[sqlite3.Row]:
    """Devuelve las notificaciones del usuario, las más recientes primero."""
    filtro = " AND leida = 0" if solo_no_leidas else ""
    return conn.execute(
        f"SELECT * FROM notificacion WHERE usuario_id = ?{filtro} "
        "ORDER BY creado_en DESC, id DESC", (usuario_id,)).fetchall()


def marcar_leida(conn: sqlite3.Connection, notificacion_id: int, usuario_id: int) -> None:
    """Marca una notificación como leída; solo su dueño puede hacerlo.

    Raises:
        ErrorNoEncontrado: La notificación no existe.
        ErrorPermiso: La notificación pertenece a otro usuario.
    """
    fila = conn.execute("SELECT usuario_id FROM notificacion WHERE id = ?",
                        (notificacion_id,)).fetchone()
    if fila is None:
        raise ErrorNoEncontrado("La notificación no existe.")
    if fila["usuario_id"] != usuario_id:
        raise ErrorPermiso("No puedes modificar notificaciones de otro usuario.")
    conn.execute("UPDATE notificacion SET leida = 1 WHERE id = ?", (notificacion_id,))
    conn.commit()
