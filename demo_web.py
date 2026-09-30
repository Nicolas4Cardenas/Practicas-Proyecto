"""Demo web del producto (US1-US9) sobre la lógica de app/, sin dependencias extra.

Uso:
    python demo_web.py        # abre http://localhost:8000

Usa una base de datos en memoria con datos de ejemplo. Es solo una demostración:
la sesión viaja en la URL (?u=id) y no hay carga real de fotos.
"""
import html
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote, urlparse

from app import (db, diagnosticos, estadisticas, notificaciones, reportes,
                 usuarios)
from app.errores import ErrorDominio

CONN = db.conectar()
CSS = ("body{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;"
       "color:#1f2a1f}h1{color:#2e6b2e}.card{border:1px solid #cfdccf;border-radius:8px;"
       "padding:.8rem 1rem;margin:.6rem 0;background:#f7fbf7}.msg{background:#fff3cd;padding:.6rem;"
       "border-radius:6px}.tag{background:#2e6b2e;color:#fff;border-radius:10px;padding:0 .6rem;"
       "font-size:.85rem}input,textarea,select{width:100%;padding:.4rem;margin:.2rem 0}"
       "button{background:#2e6b2e;color:#fff;border:0;border-radius:6px;padding:.4rem .9rem;"
       "cursor:pointer}a{color:#2e6b2e}")


def sembrar() -> None:
    """Crea usuarios y reportes de ejemplo para que la demo no arranque vacía."""
    db.inicializar(CONN)
    carlos = usuarios.registrar_usuario(CONN, "Carlos Pérez", "carlos@finca.co", "clave1234")
    usuarios.registrar_usuario(CONN, "Laura Gómez", "laura@agro.co", "clave1234",
                               rol="profesional")
    reportes.crear_reporte(CONN, carlos, "Hojas amarillas con manchas negras",
                           "Vereda La Esperanza", ["hoja1.jpg"], "Sigatoka", "Villavicencio")
    reportes.crear_reporte(CONN, carlos, "Tallos con galerías y pudrición", "4.15, -73.63",
                           ["tallo.png"], "Picudo negro", "Acacías")


def pagina(cuerpo: str, msg: str = "") -> bytes:
    """Envuelve el cuerpo en el HTML base; escapa el mensaje para el usuario."""
    aviso = f'<p class="msg">{html.escape(msg)}</p>' if msg else ""
    return (f"<!doctype html><meta charset=utf-8><title>Control de Plagas</title>"
            f"<style>{CSS}</style><h1>🍌 Control de Plagas en Plátano</h1>{aviso}{cuerpo}").encode()


def vista_login() -> str:
    return ('<div class="card"><h3>Iniciar sesión (US1)</h3>'
            '<form method=post action=/login>Correo<input name=email value=carlos@finca.co>'
            'Contraseña<input name=password type=password value=clave1234>'
            '<button>Entrar</button></form>'
            '<p>Demo: <b>carlos@finca.co</b> (campesino) · <b>laura@agro.co</b> (profesional), '
            'clave <b>clave1234</b></p></div>')


def vista_campesino(u) -> str:
    uid = u["id"]
    filas = "".join(
        f'<div class="card">#{r["id"]} {html.escape(r["descripcion"])} — '
        f'<span class="tag">{r["estado"]}</span><br><small>{html.escape(r["ubicacion"])}</small></div>'
        for r in reportes.listar_mis_reportes(CONN, uid)) or "<p>Sin reportes.</p>"
    notas = "".join(
        f'<div class="card">{"🔔" if not n["leida"] else "✔"} {html.escape(n["mensaje"])}'
        + (f'<form method=post action=/leida style="display:inline"><input type=hidden name=u '
           f'value={uid}><input type=hidden name=n value={n["id"]}><button>Marcar leída</button>'
           f'</form>' if not n["leida"] else "") + "</div>"
        for n in notificaciones.listar_notificaciones(CONN, uid)) or "<p>Sin notificaciones.</p>"
    return (f'<h2>Hola, {html.escape(u["nombre"])} (campesino)</h2>'
            f'<div class="card"><h3>Nuevo reporte (US2, US3)</h3><form method=post action=/reportar>'
            f'<input type=hidden name=u value={uid}>Descripción<textarea name=descripcion></textarea>'
            f'Ubicación (dirección o "lat, lon")<input name=ubicacion>'
            f'Foto (nombre de archivo .jpg/.png)<input name=foto value=foto.jpg>'
            f'Tipo de plaga<input name=tipo_plaga>Zona<input name=zona><button>Enviar reporte</button>'
            f'</form></div><h3>Mis reportes (US6)</h3>{filas}<h3>Notificaciones (US7)</h3>{notas}'
            f'<p><a href=/>Salir</a></p>')


def vista_profesional(u) -> str:
    uid = u["id"]

    def boton(ruta: str, rid: int, texto: str) -> str:
        return (f'<form method=post action={ruta} style="display:inline"><input type=hidden name=u '
                f'value={uid}><input type=hidden name=r value={rid}><button>{texto}</button></form>')

    pend = "".join(
        f'<div class="card">#{r["id"]} {html.escape(r["descripcion"])} '
        f'<small>({html.escape(r["ubicacion"])})</small> {boton("/revisar", r["id"], "Iniciar revisión")}'
        f'<form method=post action=/diagnosticar><input type=hidden name=u value={uid}>'
        f'<input type=hidden name=r value={r["id"]}>Diagnóstico<input name=texto>'
        f'Recomendación<input name=recomendacion><button>Diagnosticar</button></form></div>'
        for r in reportes.listar_pendientes(CONN, uid)) or "<p>No hay reportes pendientes.</p>"
    # Los casos diagnosticados o en revisión no salen en "pendientes" (US4): se listan aparte.
    otros = CONN.execute("SELECT id, descripcion, estado FROM reporte WHERE estado "
                         "IN ('En revisión','Diagnosticado') ORDER BY id").fetchall()
    seguimiento = "".join(
        f'<div class="card">#{r["id"]} {html.escape(r["descripcion"])} — '
        f'<span class="tag">{r["estado"]}</span>'
        + (boton("/resolver", r["id"], "Marcar resuelto") if r["estado"] == "Diagnosticado" else
           '<form method=post action=/diagnosticar><input type=hidden name=u value=' + str(uid) +
           '><input type=hidden name=r value=' + str(r["id"]) + '>Diagnóstico<input name=texto>'
           'Recomendación<input name=recomendacion><button>Diagnosticar</button></form>')
        + "</div>" for r in otros) or "<p>Sin casos en seguimiento.</p>"
    stats = "".join(f'<span class="tag">{e}: {t}</span> '
                    for e, t in estadisticas.reportes_por_estado(CONN, uid).items())
    return (f'<h2>Hola, {html.escape(u["nombre"])} (profesional)</h2><h3>Pendientes (US4, US5)</h3>'
            f'{pend}<h3>En seguimiento (US8)</h3>{seguimiento}<h3>Estadísticas (US9)</h3>'
            f'<div class="card">{stats}</div><p><a href=/>Salir</a></p>')


class Manejador(BaseHTTPRequestHandler):
    """Enruta las pantallas de la demo hacia la lógica de negocio."""

    def _responder(self, cuerpo: bytes, codigo: int = 200) -> None:
        self.send_response(codigo)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _volver(self, uid: int, msg: str = "") -> None:
        self.send_response(303)
        self.send_header("Location", f"/panel?u={uid}&msg={quote(msg)}")
        self.end_headers()

    def do_GET(self) -> None:
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path == "/panel" and "u" in q:
            u = usuarios.obtener_usuario(CONN, int(q["u"][0]))
            vista = vista_campesino if u["rol"] == "campesino" else vista_profesional
            return self._responder(pagina(vista(u), q.get("msg", [""])[0]))
        self._responder(pagina(vista_login(), parse_qs(url.query).get("msg", [""])[0]))

    def do_POST(self) -> None:
        largo = int(self.headers.get("Content-Length", 0))
        f = {k: v[0] for k, v in parse_qs(self.rfile.read(largo).decode()).items()}
        ruta = self.path
        try:
            if ruta == "/login":
                u = usuarios.iniciar_sesion(CONN, f.get("email", ""), f.get("password", ""))
                return self._volver(u["id"], f"Bienvenido/a, {u['nombre']}.")
            uid, rid = int(f["u"]), int(f.get("r", 0))
            if ruta == "/reportar":
                n = reportes.crear_reporte(CONN, uid, f.get("descripcion", ""), f.get("ubicacion", ""),
                                           [f.get("foto", "")], f.get("tipo_plaga"), f.get("zona"))
                msg = f"Reporte #{n} enviado."
            elif ruta == "/leida":
                notificaciones.marcar_leida(CONN, int(f["n"]), uid)
                msg = "Notificación marcada como leída."
            elif ruta == "/revisar":
                diagnosticos.iniciar_revision(CONN, rid, uid)
                msg = f"Reporte #{rid} en revisión."
            elif ruta == "/diagnosticar":
                diagnosticos.registrar_diagnostico(CONN, rid, uid, f.get("texto", ""),
                                                   f.get("recomendacion", ""))
                msg = f"Diagnóstico registrado en el reporte #{rid}."
            elif ruta == "/resolver":
                diagnosticos.marcar_resuelto(CONN, rid, uid)
                msg = f"Reporte #{rid} resuelto."
            else:
                msg = "Acción desconocida."
            self._volver(uid, msg)
        except ErrorDominio as e:
            # Los errores de negocio están redactados para mostrarse tal cual (estándar §7).
            if "u" in f:
                return self._volver(int(f["u"]), f"⚠ {e}")
            self.send_response(303)
            self.send_header("Location", f"/?msg={quote('⚠ ' + str(e))}")
            self.end_headers()

    def log_message(self, *args) -> None:
        """Silencia el registro por petición para no ensuciar la consola."""


if __name__ == "__main__":
    sembrar()
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Demo en http://localhost:{puerto}  (Ctrl+C para salir)")
    HTTPServer(("", puerto), Manejador).serve_forever()
