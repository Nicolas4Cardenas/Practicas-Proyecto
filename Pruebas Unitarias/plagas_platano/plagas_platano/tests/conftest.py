"""Fixtures compartidas: base de datos en memoria y usuarios de ejemplo."""
import pytest

from app import db, reportes, usuarios


@pytest.fixture
def conn():
    conexion = db.conectar(":memory:")
    db.inicializar(conexion)
    yield conexion
    conexion.close()


@pytest.fixture
def campesino(conn):
    return usuarios.registrar_usuario(conn, "Carlos Pérez", "carlos@finca.co", "clave1234")


@pytest.fixture
def campesino2(conn):
    return usuarios.registrar_usuario(conn, "Ana Rojas", "ana@finca.co", "clave1234")


@pytest.fixture
def agronomo(conn):
    return usuarios.registrar_usuario(conn, "Laura Gómez", "laura@agro.co", "clave1234",
                                      rol="profesional")


@pytest.fixture
def reporte(conn, campesino):
    return reportes.crear_reporte(conn, campesino, "Hojas amarillas y manchas",
                                  "Vereda La Esperanza", ["hoja1.jpg"],
                                  tipo_plaga="Sigatoka", zona="Villavicencio")
