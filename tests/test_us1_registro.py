"""US1 - Registro e inicio de sesión."""
import pytest

from app import usuarios
from app.errores import ErrorAutenticacion, ErrorValidacion


def test_registro_valido_devuelve_id_y_guarda_rol_campesino(conn):
    uid = usuarios.registrar_usuario(conn, "Carlos Pérez", "carlos@finca.co", "clave1234")
    assert usuarios.obtener_usuario(conn, uid)["rol"] == "campesino"


def test_contrasena_no_se_guarda_en_texto_plano(conn):
    uid = usuarios.registrar_usuario(conn, "Carlos", "c@finca.co", "clave1234")
    assert "clave1234" not in usuarios.obtener_usuario(conn, uid)["password_hash"]


@pytest.mark.parametrize("nombre,email,password", [
    ("", "a@b.co", "clave1234"),
    ("   ", "a@b.co", "clave1234"),
    ("Ana", "correo-sin-arroba", "clave1234"),
    ("Ana", "a@b.co", "corta"),
])
def test_registro_rechaza_datos_invalidos(conn, nombre, email, password):
    with pytest.raises(ErrorValidacion):
        usuarios.registrar_usuario(conn, nombre, email, password)


def test_registro_rechaza_correo_duplicado_sin_importar_mayusculas(conn):
    usuarios.registrar_usuario(conn, "Ana", "ana@finca.co", "clave1234")
    with pytest.raises(ErrorValidacion):
        usuarios.registrar_usuario(conn, "Otra Ana", "ANA@finca.co", "clave1234")


def test_registro_rechaza_rol_invalido(conn):
    with pytest.raises(ErrorValidacion):
        usuarios.registrar_usuario(conn, "Ana", "ana@finca.co", "clave1234", rol="admin")


def test_login_correcto_devuelve_usuario(conn, campesino):
    assert usuarios.iniciar_sesion(conn, "CARLOS@finca.co", "clave1234")["id"] == campesino


@pytest.mark.parametrize("email,password", [
    ("carlos@finca.co", "incorrecta1"),
    ("nadie@finca.co", "clave1234"),
])
def test_login_rechaza_credenciales_incorrectas(conn, campesino, email, password):
    with pytest.raises(ErrorAutenticacion):
        usuarios.iniciar_sesion(conn, email, password)
