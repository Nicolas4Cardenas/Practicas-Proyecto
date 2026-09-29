"""US9 - Panel de estadísticas por estado, zona y tipo de plaga."""
import pytest

from app import diagnosticos, estadisticas, reportes
from app.errores import ErrorPermiso


@pytest.fixture
def datos(conn, campesino, agronomo):
    r1 = reportes.crear_reporte(conn, campesino, "a", "Finca 1", ["a.jpg"], "Sigatoka", "Villavicencio")
    r2 = reportes.crear_reporte(conn, campesino, "b", "Finca 2", ["a.jpg"], "Picudo negro", "Villavicencio")
    reportes.crear_reporte(conn, campesino, "c", "Finca 3", ["a.jpg"], "Sigatoka", "Acacías")
    diagnosticos.registrar_diagnostico(conn, r1, agronomo, "Sigatoka", "Fungicida")
    diagnosticos.marcar_resuelto(conn, r1, agronomo)
    diagnosticos.registrar_diagnostico(conn, r2, agronomo, "Picudo", "Trampas")


def test_sin_reportes_devuelve_los_cuatro_estados_en_cero(conn, agronomo):
    assert estadisticas.reportes_por_estado(conn, agronomo) == {
        "Reportado": 0, "En revisión": 0, "Diagnosticado": 0, "Resuelto": 0}


def test_cuenta_reportes_por_estado(conn, agronomo, datos):
    assert estadisticas.reportes_por_estado(conn, agronomo) == {
        "Reportado": 1, "En revisión": 0, "Diagnosticado": 1, "Resuelto": 1}


def test_filtra_por_zona_sin_distinguir_mayusculas(conn, agronomo, datos):
    r = estadisticas.reportes_por_estado(conn, agronomo, zona="villavicencio")
    assert sum(r.values()) == 2 and r["Reportado"] == 0


def test_filtra_por_tipo_de_plaga(conn, agronomo, datos):
    assert sum(estadisticas.reportes_por_estado(conn, agronomo, tipo_plaga="Sigatoka").values()) == 2


def test_combina_filtros_de_zona_y_plaga(conn, agronomo, datos):
    r = estadisticas.reportes_por_estado(conn, agronomo, zona="Acacías", tipo_plaga="Sigatoka")
    assert r["Reportado"] == 1 and sum(r.values()) == 1


def test_filtro_sin_coincidencias_devuelve_ceros(conn, agronomo, datos):
    assert sum(estadisticas.reportes_por_estado(conn, agronomo, zona="Bogotá").values()) == 0


def test_campesino_no_accede_al_panel(conn, campesino):
    with pytest.raises(ErrorPermiso):
        estadisticas.reportes_por_estado(conn, campesino)
