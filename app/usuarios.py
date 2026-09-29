"""US1 - Registro e inicio de sesión de usuarios."""
import hashlib
import hmac
import os
import re
import sqlite3

from .db import ahora_iso
from .errores import (ErrorAutenticacion, ErrorNoEncontrado, ErrorPermiso,
                      ErrorValidacion)

ROLES = ("campesino", "profesional")
LONGITUD_MIN_PASSWORD = 8
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _hashear(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return f"{salt.hex()}${digest.hex()}"


def _verificar(password: str, almacenado: str) -> bool:
    salt_hex, digest_hex = almacenado.split("$")
    esperado = _hashear(password, bytes.fromhex(salt_hex)).split("$")[1]
    return hmac.compare_digest(esperado, digest_hex)


def registrar_usuario(conn: sqlite3.Connection, nombre: str, email: str,
                      password: str, rol: str = "campesino") -> int:
    """Registra un usuario nuevo (US1).

    Args:
        conn: Conexión a la base de datos.
        nombre: Nombre completo (obligatorio).
        email: Correo único con formato válido.
        password: Contraseña de al menos 8 caracteres.
        rol: "campesino" (por defecto) o "profesional".

    Returns:
        Identificador del usuario creado.

    Raises:
        ErrorValidacion: Campos vacíos, correo inválido, contraseña corta,
            rol inválido o correo ya registrado.
    """
    nombre = (nombre or "").strip()
    email = (email or "").strip().lower()
    if not nombre:
        raise ErrorValidacion("El nombre es obligatorio.")
    if not _EMAIL_RE.match(email):
        raise ErrorValidacion("El correo no tiene un formato válido.")
    if len(password or "") < LONGITUD_MIN_PASSWORD:
        raise ErrorValidacion(
            f"La contraseña debe tener al menos {LONGITUD_MIN_PASSWORD} caracteres.")
    if rol not in ROLES:
        raise ErrorValidacion("Rol inválido.")
    if conn.execute("SELECT 1 FROM usuario WHERE email = ?", (email,)).fetchone():
        raise ErrorValidacion("El correo ya está registrado.")
    cur = conn.execute(
        "INSERT INTO usuario (nombre, email, password_hash, rol, creado_en) "
        "VALUES (?, ?, ?, ?, ?)",
        (nombre, email, _hashear(password), rol, ahora_iso()))
    conn.commit()
    return cur.lastrowid


def iniciar_sesion(conn: sqlite3.Connection, email: str, password: str) -> sqlite3.Row:
    """Valida credenciales y devuelve el usuario (US1).

    Raises:
        ErrorAutenticacion: Correo o contraseña incorrectos.
    """
    fila = conn.execute("SELECT * FROM usuario WHERE email = ?",
                        ((email or "").strip().lower(),)).fetchone()
    if fila is None or not _verificar(password or "", fila["password_hash"]):
        raise ErrorAutenticacion("Correo o contraseña incorrectos.")
    return fila


def obtener_usuario(conn: sqlite3.Connection, usuario_id: int) -> sqlite3.Row:
    """Devuelve un usuario por id o lanza ErrorNoEncontrado."""
    fila = conn.execute("SELECT * FROM usuario WHERE id = ?", (usuario_id,)).fetchone()
    if fila is None:
        raise ErrorNoEncontrado("El usuario no existe.")
    return fila


def exigir_rol(conn: sqlite3.Connection, usuario_id: int, rol: str) -> sqlite3.Row:
    """Verifica que el usuario exista y tenga el rol indicado.

    Raises:
        ErrorNoEncontrado: El usuario no existe.
        ErrorPermiso: El usuario tiene otro rol.
    """
    usuario = obtener_usuario(conn, usuario_id)
    if usuario["rol"] != rol:
        raise ErrorPermiso(f"Esta acción es solo para el rol {rol}.")
    return usuario
