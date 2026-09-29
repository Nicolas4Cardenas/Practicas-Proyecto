"""US2, US3, US4 y US6 - Creación, ubicación y consulta de reportes."""
import re
import sqlite3

from . import usuarios
from .db import ahora_iso
from .errores import ErrorNoEncontrado, ErrorValidacion

EXTENSIONES_VALIDAS = (".jpg", ".jpeg", ".png")
_COORDENADAS_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$")


def validar_ubicacion(ubicacion: str) -> str:
    """Valida la ubicación del cultivo (US3).

    Acepta una dirección/descripción (mínimo 3 caracteres) o coordenadas
    "lat, lon" dentro de rango.

    Returns:
        La ubicación sin espacios sobrantes.

    Raises:
        ErrorValidacion: Vacía, muy corta o con coordenadas fuera de rango.
    """
    texto = (ubicacion or "").strip()
    if not texto:
        raise ErrorValidacion("La ubicación es obligatoria.")
    coords = _COORDENADAS_RE.match(texto)
    if coords:
        lat, lon = float(coords.group(1)), float(coords.group(2))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ErrorValidacion("Las coordenadas están fuera de rango.")
        return texto
    if len(texto) < 3:
        raise ErrorValidacion("La ubicación es demasiado corta.")
    return texto


def crear_reporte(conn: sqlite3.Connection, usuario_id: int, descripcion: str,
                  ubicacion: str, fotos: list[str], tipo_plaga: str | None = None,
                  zona: str | None = None, ahora: str | None = None) -> int:
    """Crea un reporte de afectación con evidencia fotográfica (US2 y US3).

    Args:
        conn: Conexión a la base de datos.
        usuario_id: Campesino que reporta.
        descripcion: Descripción de la afectación (obligatoria).
        ubicacion: Dirección o coordenadas del cultivo (obligatoria).
        fotos: Nombres de archivo; mínimo uno, extensión .jpg/.jpeg/.png.
        tipo_plaga: Tipo de plaga, opcional (usado en estadísticas).
        zona: Zona del cultivo, opcional (usada en estadísticas).
        ahora: Marca de tiempo ISO opcional (útil en pruebas).

    Returns:
        Identificador del reporte, creado en estado "Reportado".

    Raises:
        ErrorPermiso: El usuario no es campesino.
        ErrorValidacion: Falta descripción, ubicación o imagen válida.
    """
    usuarios.exigir_rol(conn, usuario_id, "campesino")
    descripcion = (descripcion or "").strip()
    if not descripcion:
        raise ErrorValidacion("La descripción es obligatoria.")
    ubicacion = validar_ubicacion(ubicacion)
    if not fotos:
        raise ErrorValidacion("Debes adjuntar al menos una imagen.")
    for nombre in fotos:
        if not str(nombre).lower().endswith(EXTENSIONES_VALIDAS):
            raise ErrorValidacion("Solo se permiten imágenes .jpg, .jpeg o .png.")
    marca = ahora or ahora_iso()
    cur = conn.execute(
        "INSERT INTO reporte (usuario_id, descripcion, ubicacion, tipo_plaga, zona, "
        "estado, creado_en, actualizado_en) VALUES (?, ?, ?, ?, ?, 'Reportado', ?, ?)",
        (usuario_id, descripcion, ubicacion,
         (tipo_plaga or "").strip() or None, (zona or "").strip() or None, marca, marca))
    reporte_id = cur.lastrowid
    conn.executemany("INSERT INTO foto (reporte_id, nombre_archivo) VALUES (?, ?)",
                     [(reporte_id, n) for n in fotos])
    conn.commit()
    return reporte_id


def obtener_reporte(conn: sqlite3.Connection, reporte_id: int) -> sqlite3.Row:
    """Devuelve un reporte por id o lanza ErrorNoEncontrado."""
    fila = conn.execute("SELECT * FROM reporte WHERE id = ?", (reporte_id,)).fetchone()
    if fila is None:
        raise ErrorNoEncontrado("El reporte no existe.")
    return fila


def listar_pendientes(conn: sqlite3.Connection, profesional_id: int,
                      orden: str = "asc") -> list[sqlite3.Row]:
    """Lista los reportes en estado "Reportado" para el profesional (US4).

    Args:
        orden: "asc" (más antiguos primero, por defecto) o "desc".

    Raises:
        ErrorPermiso: El usuario no es profesional.
        ErrorValidacion: Orden distinto de "asc" o "desc".
    """
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    if orden not in ("asc", "desc"):
        raise ErrorValidacion("El orden debe ser 'asc' o 'desc'.")
    return conn.execute(
        f"SELECT * FROM reporte WHERE estado = 'Reportado' "
        f"ORDER BY creado_en {orden.upper()}, id {orden.upper()}").fetchall()


def listar_mis_reportes(conn: sqlite3.Connection, usuario_id: int) -> list[sqlite3.Row]:
    """Lista los reportes propios con su estado y última actualización (US6).

    Los más recientes aparecen primero.
    """
    usuarios.exigir_rol(conn, usuario_id, "campesino")
    return conn.execute(
        "SELECT id, descripcion, ubicacion, estado, actualizado_en FROM reporte "
        "WHERE usuario_id = ? ORDER BY creado_en DESC, id DESC", (usuario_id,)).fetchall()
