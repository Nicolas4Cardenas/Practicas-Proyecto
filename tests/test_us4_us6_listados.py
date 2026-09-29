"""US4 (pendientes del profesional) y US6 (mis reportes del campesino)."""
import pytest

from app import diagnosticos, reportes
from app.errores import ErrorPermiso, ErrorValidacion


def _crear(conn, uid, fecha, desc="Manchas"):
    return reportes.crear_reporte(conn, uid, desc, "Finca El Roble", ["a.jpg"], ahora=fecha)


def test_pendientes_solo_incluye_reportados_ordenados_por_fecha(conn, campesino, agronomo):
    nuevo = _crear(conn, campesino, "2026-09-03T10:00:00")
    viejo = _crear(conn, campesino, "2026-09-01T10:00:00")
    ya_diagnosticado = _crear(conn, campesino, "2026-09-02T10:00:00")
    diagnosticos.registrar_diagnostico(conn, ya_diagnosticado, agronomo, "Sigatoka", "Fungicida")
    assert [r["id"] for r in reportes.listar_pendientes(conn, agronomo)] == [viejo, nuevo]
    assert [r["id"] for r in reportes.listar_pendientes(conn, agronomo, "desc")] == [nuevo, viejo]


def test_pendientes_rechaza_orden_invalido(conn, agronomo):
    with pytest.raises(ErrorValidacion):
        reportes.listar_pendientes(conn, agronomo, "cualquiera")


def test_campesino_no_puede_ver_pendientes(conn, campesino):
    with pytest.raises(ErrorPermiso):
        reportes.listar_pendientes(conn, campesino)


def test_mis_reportes_muestra_solo_los_propios_mas_recientes_primero(conn, campesino, campesino2):
    primero = _crear(conn, campesino, "2026-09-01T10:00:00")
    segundo = _crear(conn, campesino, "2026-09-02T10:00:00")
    _crear(conn, campesino2, "2026-09-03T10:00:00")
    assert [r["id"] for r in reportes.listar_mis_reportes(conn, campesino)] == [segundo, primero]


def test_mis_reportes_refleja_estado_y_fecha_de_actualizacion(conn, campesino, agronomo, reporte):
    antes = reportes.listar_mis_reportes(conn, campesino)[0]
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    despues = reportes.listar_mis_reportes(conn, campesino)[0]
    assert antes["estado"] == "Reportado" and despues["estado"] == "Diagnosticado"
    assert despues["actualizado_en"] > antes["actualizado_en"]
