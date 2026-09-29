"""US7 - Máquina de estados del reporte y notificaciones por cambio de estado."""
import sqlite3

from .db import ahora_iso
from .errores import ErrorTransicion, ErrorValidacion
from .reportes import obtener_reporte

ESTADOS = ("Reportado", "En revisión", "Diagnosticado", "Resuelto")

TRANSICIONES = {
    "Reportado": {"En revisión", "Diagnosticado"},
    "En revisión": {"Diagnosticado"},
    "Diagnosticado": {"Resuelto"},
    "Resuelto": set(),
}


def cambiar_estado(conn: sqlite3.Connection, reporte_id: int, nuevo_estado: str,
                   ahora: str | None = None) -> None:
    """Cambia el estado de un reporte y notifica al campesino (US7).

    No hace commit: quien la llama confirma la transacción.

    Raises:
        ErrorValidacion: El estado destino no existe.
        ErrorTransicion: La transición no está permitida.
    """
    if nuevo_estado not in ESTADOS:
        raise ErrorValidacion(f"Estado inválido: {nuevo_estado}.")
    reporte = obtener_reporte(conn, reporte_id)
    actual = reporte["estado"]
    if nuevo_estado not in TRANSICIONES[actual]:
        raise ErrorTransicion(f"No se puede pasar de '{actual}' a '{nuevo_estado}'.")
    marca = ahora or ahora_iso()
    conn.execute("UPDATE reporte SET estado = ?, actualizado_en = ? WHERE id = ?",
                 (nuevo_estado, marca, reporte_id))
    conn.execute(
        "INSERT INTO notificacion (usuario_id, reporte_id, mensaje, creado_en) "
        "VALUES (?, ?, ?, ?)",
        (reporte["usuario_id"], reporte_id,
         f"Tu reporte #{reporte_id} cambió a estado '{nuevo_estado}'.", marca))
