"""Recorrido de demostración en consola: registro -> reporte -> diagnóstico ->
notificación -> cierre -> estadísticas.

Uso:
    python demo.py
"""
from app import (db, diagnosticos, estadisticas, notificaciones, reportes,
                 usuarios)


def main() -> None:
    conn = db.conectar()  # base de datos en memoria: no deja archivos
    db.inicializar(conn)

    print("1. Registro de usuarios (US1)")
    campesino = usuarios.registrar_usuario(conn, "Carlos Pérez", "carlos@finca.co", "clave1234")
    agronomo = usuarios.registrar_usuario(conn, "Laura Gómez", "laura@agro.co", "clave1234",
                                          rol="profesional")
    print(f"   Campesino #{campesino} y agrónomo #{agronomo} registrados.")

    print("2. El campesino reporta una afectación (US2, US3)")
    rid = reportes.crear_reporte(conn, campesino, "Hojas amarillas con manchas negras",
                                 "Vereda La Esperanza", ["hoja1.jpg", "hoja2.jpg"],
                                 tipo_plaga="Sigatoka", zona="Villavicencio")
    print(f"   Reporte #{rid} creado en estado '{reportes.obtener_reporte(conn, rid)['estado']}'.")

    print("3. El agrónomo ve los reportes pendientes (US4)")
    for r in reportes.listar_pendientes(conn, agronomo):
        print(f"   Pendiente #{r['id']}: {r['descripcion']} ({r['ubicacion']})")

    print("4. El agrónomo registra el diagnóstico (US5)")
    diagnosticos.registrar_diagnostico(conn, rid, agronomo, "Sigatoka negra",
                                       "Aplicar fungicida y podar hojas afectadas")

    print("5. El campesino consulta su reporte (US6) y su notificación (US7)")
    for r in reportes.listar_mis_reportes(conn, campesino):
        print(f"   Mi reporte #{r['id']}: {r['estado']}")
    for n in notificaciones.listar_notificaciones(conn, campesino):
        print(f"   Notificación: {n['mensaje']}")

    print("6. El agrónomo cierra el caso (US8)")
    diagnosticos.marcar_resuelto(conn, rid, agronomo)

    print("7. Panel de estadísticas (US9)")
    for estado, total in estadisticas.reportes_por_estado(conn, agronomo).items():
        print(f"   {estado}: {total}")


if __name__ == "__main__":
    main()
