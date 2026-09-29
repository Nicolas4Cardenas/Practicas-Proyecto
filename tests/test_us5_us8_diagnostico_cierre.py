"""US5 (diagnóstico) y US8 (cierre del caso)."""
import pytest

from app import diagnosticos, reportes
from app.errores import ErrorPermiso, ErrorTransicion, ErrorValidacion


def test_diagnostico_guarda_datos_y_cambia_estado(conn, agronomo, reporte):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka negra", "Aplicar fungicida")
    fila = conn.execute("SELECT * FROM diagnostico WHERE reporte_id = ?", (reporte,)).fetchone()
    assert fila["texto"] == "Sigatoka negra" and fila["profesional_id"] == agronomo
    assert reportes.obtener_reporte(conn, reporte)["estado"] == "Diagnosticado"


@pytest.mark.parametrize("texto,recomendacion", [("", "Fungicida"), ("Sigatoka", ""), ("  ", "  ")])
def test_diagnostico_exige_texto_y_recomendacion(conn, agronomo, reporte, texto, recomendacion):
    with pytest.raises(ErrorValidacion):
        diagnosticos.registrar_diagnostico(conn, reporte, agronomo, texto, recomendacion)
    assert reportes.obtener_reporte(conn, reporte)["estado"] == "Reportado"


def test_campesino_no_puede_diagnosticar(conn, campesino, reporte):
    with pytest.raises(ErrorPermiso):
        diagnosticos.registrar_diagnostico(conn, reporte, campesino, "Sigatoka", "Fungicida")


def test_no_se_puede_diagnosticar_dos_veces(conn, agronomo, reporte):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    with pytest.raises(ErrorTransicion):
        diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Otra cosa", "Otra")


def test_diagnostico_desde_en_revision(conn, agronomo, reporte):
    diagnosticos.iniciar_revision(conn, reporte, agronomo)
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    assert reportes.obtener_reporte(conn, reporte)["estado"] == "Diagnosticado"


def test_marcar_resuelto_desde_diagnosticado(conn, agronomo, reporte):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    diagnosticos.marcar_resuelto(conn, reporte, agronomo)
    assert reportes.obtener_reporte(conn, reporte)["estado"] == "Resuelto"


def test_no_se_puede_resolver_un_reporte_sin_diagnosticar(conn, agronomo, reporte):
    with pytest.raises(ErrorTransicion):
        diagnosticos.marcar_resuelto(conn, reporte, agronomo)


def test_campesino_no_puede_marcar_resuelto(conn, campesino, agronomo, reporte):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    with pytest.raises(ErrorPermiso):
        diagnosticos.marcar_resuelto(conn, reporte, campesino)
