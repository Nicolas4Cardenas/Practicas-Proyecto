"""US5 y US8 - Diagnóstico y cierre de casos por el profesional."""
import sqlite3

from . import usuarios
from .db import ahora_iso
from .errores import ErrorTransicion, ErrorValidacion
from .estados import cambiar_estado
from .reportes import obtener_reporte


def iniciar_revision(conn: sqlite3.Connection, reporte_id: int, profesional_id: int) -> None:
    """Pasa un reporte de "Reportado" a "En revisión"."""
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    cambiar_estado(conn, reporte_id, "En revisión")
    conn.commit()


def registrar_diagnostico(conn: sqlite3.Connection, reporte_id: int, profesional_id: int,
                          texto: str, recomendacion: str) -> int:
    """Registra el diagnóstico y deja el reporte en "Diagnosticado" (US5).

    Raises:
        ErrorPermiso: El usuario no es profesional.
        ErrorValidacion: Falta el texto del diagnóstico o la recomendación.
        ErrorTransicion: El reporte ya estaba diagnosticado o resuelto.
    """
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    texto = (texto or "").strip()
    recomendacion = (recomendacion or "").strip()
    if not texto:
        raise ErrorValidacion("El diagnóstico es obligatorio.")
    if not recomendacion:
        raise ErrorValidacion("La recomendación es obligatoria.")
    obtener_reporte(conn, reporte_id)
    cambiar_estado(conn, reporte_id, "Diagnosticado")
    cur = conn.execute(
        "INSERT INTO diagnostico (reporte_id, profesional_id, texto, recomendacion, creado_en) "
        "VALUES (?, ?, ?, ?, ?)",
        (reporte_id, profesional_id, texto, recomendacion, ahora_iso()))
    conn.commit()
    return cur.lastrowid


def marcar_resuelto(conn: sqlite3.Connection, reporte_id: int, profesional_id: int) -> None:
    """Cierra un caso diagnosticado como "Resuelto" (US8).

    Raises:
        ErrorPermiso: El usuario no es profesional.
        ErrorTransicion: El reporte no está en estado "Diagnosticado".
    """
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    if obtener_reporte(conn, reporte_id)["estado"] != "Diagnosticado":
        raise ErrorTransicion("Solo se puede resolver un reporte diagnosticado.")
    cambiar_estado(conn, reporte_id, "Resuelto")
    conn.commit()
