"""US7 - Cambios de estado y notificaciones al campesino."""
import pytest

from app import diagnosticos, estados, notificaciones
from app.errores import ErrorNoEncontrado, ErrorPermiso, ErrorTransicion, ErrorValidacion


@pytest.mark.parametrize("origen,destino,valida", [
    ("Reportado", "En revisión", True),
    ("Reportado", "Diagnosticado", True),
    ("Reportado", "Resuelto", False),
    ("En revisión", "Diagnosticado", True),
    ("En revisión", "Reportado", False),
    ("Diagnosticado", "Resuelto", True),
    ("Diagnosticado", "Reportado", False),
    ("Resuelto", "Diagnosticado", False),
])
def test_tabla_de_transiciones(origen, destino, valida):
    assert (destino in estados.TRANSICIONES[origen]) is valida


def test_cambiar_estado_rechaza_estado_inexistente(conn, reporte):
    with pytest.raises(ErrorValidacion):
        estados.cambiar_estado(conn, reporte, "Archivado")


def test_cambiar_estado_rechaza_transicion_no_permitida(conn, reporte):
    with pytest.raises(ErrorTransicion):
        estados.cambiar_estado(conn, reporte, "Resuelto")


def test_recorre_los_cuatro_estados_y_notifica_cada_cambio(conn, campesino, agronomo, reporte):
    diagnosticos.iniciar_revision(conn, reporte, agronomo)
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    diagnosticos.marcar_resuelto(conn, reporte, agronomo)
    mensajes = [n["mensaje"] for n in notificaciones.listar_notificaciones(conn, campesino)]
    assert len(mensajes) == 3
    for estado in ("En revisión", "Diagnosticado", "Resuelto"):
        assert any(estado in m for m in mensajes)


def test_notificacion_va_al_campesino_dueno_y_no_a_otros(conn, campesino, campesino2, agronomo, reporte):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    assert len(notificaciones.listar_notificaciones(conn, campesino)) == 1
    assert notificaciones.listar_notificaciones(conn, campesino2) == []


def test_transicion_invalida_no_genera_notificacion(conn, campesino, reporte):
    with pytest.raises(ErrorTransicion):
        estados.cambiar_estado(conn, reporte, "Resuelto")
    assert notificaciones.listar_notificaciones(conn, campesino) == []


def test_marcar_leida_y_filtrar_no_leidas(conn, campesino, agronomo, reporte):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    notif = notificaciones.listar_notificaciones(conn, campesino)[0]
    notificaciones.marcar_leida(conn, notif["id"], campesino)
    assert notificaciones.listar_notificaciones(conn, campesino, solo_no_leidas=True) == []


def test_no_se_puede_marcar_leida_la_notificacion_de_otro(conn, campesino, campesino2, agronomo, reporte):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Fungicida")
    notif = notificaciones.listar_notificaciones(conn, campesino)[0]
    with pytest.raises(ErrorPermiso):
        notificaciones.marcar_leida(conn, notif["id"], campesino2)


def test_marcar_leida_notificacion_inexistente(conn, campesino):
    with pytest.raises(ErrorNoEncontrado):
        notificaciones.marcar_leida(conn, 999, campesino)
