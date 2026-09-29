"""US2 (reporte con fotos) y US3 (ubicación del cultivo)."""
import pytest

from app import reportes
from app.errores import ErrorPermiso, ErrorValidacion


def test_crear_reporte_queda_reportado_y_asociado_al_usuario(conn, campesino):
    rid = reportes.crear_reporte(conn, campesino, "Manchas negras", "Finca El Roble", ["a.jpg", "b.png"])
    fila = reportes.obtener_reporte(conn, rid)
    assert fila["estado"] == "Reportado" and fila["usuario_id"] == campesino
    assert conn.execute("SELECT COUNT(*) FROM foto WHERE reporte_id = ?", (rid,)).fetchone()[0] == 2


@pytest.mark.parametrize("descripcion", ["", "   ", None])
def test_descripcion_es_obligatoria(conn, campesino, descripcion):
    with pytest.raises(ErrorValidacion):
        reportes.crear_reporte(conn, campesino, descripcion, "Finca El Roble", ["a.jpg"])


def test_exige_al_menos_una_imagen(conn, campesino):
    with pytest.raises(ErrorValidacion):
        reportes.crear_reporte(conn, campesino, "Manchas", "Finca El Roble", [])


@pytest.mark.parametrize("archivo", ["documento.pdf", "foto.gif", "foto"])
def test_rechaza_archivos_que_no_son_imagen_valida(conn, campesino, archivo):
    with pytest.raises(ErrorValidacion):
        reportes.crear_reporte(conn, campesino, "Manchas", "Finca El Roble", [archivo])


def test_acepta_extension_en_mayusculas(conn, campesino):
    assert reportes.crear_reporte(conn, campesino, "Manchas", "Finca El Roble", ["FOTO.JPG"])


def test_profesional_no_puede_crear_reportes(conn, agronomo):
    with pytest.raises(ErrorPermiso):
        reportes.crear_reporte(conn, agronomo, "Manchas", "Finca El Roble", ["a.jpg"])


@pytest.mark.parametrize("ubicacion", ["Vereda La Esperanza", "4.15, -73.63", "  -12.5,80  "])
def test_ubicacion_valida_direccion_o_coordenadas(ubicacion):
    assert reportes.validar_ubicacion(ubicacion) == ubicacion.strip()


@pytest.mark.parametrize("ubicacion", ["", "  ", None, "ab", "95.0, -73.63", "4.15, 200"])
def test_ubicacion_invalida(ubicacion):
    with pytest.raises(ErrorValidacion):
        reportes.validar_ubicacion(ubicacion)


def test_reporte_sin_ubicacion_no_se_crea(conn, campesino):
    with pytest.raises(ErrorValidacion):
        reportes.crear_reporte(conn, campesino, "Manchas", "", ["a.jpg"])
    assert conn.execute("SELECT COUNT(*) FROM reporte").fetchone()[0] == 0
