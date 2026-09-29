"""Conexión y utilidades de base de datos (SQLite)."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

RUTA_SCHEMA = Path(__file__).resolve().parent.parent / "schema.sql"


def conectar(ruta: str = ":memory:") -> sqlite3.Connection:
    """Abre una conexión SQLite con filas tipo diccionario y llaves foráneas activas.

    Args:
        ruta: Archivo de la base de datos o ":memory:" para pruebas.

    Returns:
        Conexión lista para usar.
    """
    conn = sqlite3.connect(ruta)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar(conn: sqlite3.Connection) -> None:
    """Crea las tablas definidas en schema.sql si no existen."""
    conn.executescript(RUTA_SCHEMA.read_text(encoding="utf-8"))
    conn.commit()


def ahora_iso() -> str:
    """Devuelve la fecha y hora UTC actual en formato ISO 8601."""
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")
