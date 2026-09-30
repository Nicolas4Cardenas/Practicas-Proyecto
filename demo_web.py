"""Demo web del producto (US1-US9) sobre la lógica de app/, sin dependencias extra.

Uso:
    python demo_web.py        # abre http://localhost:8000

Usa una base de datos en memoria con datos de ejemplo. Es solo una demostración:
la sesión viaja en la URL (?u=id). Las fotos que sube el campesino (JPG o PNG) se guardan
en una carpeta temporal que se borra al cerrar la demo.

Rutas: /login (US1), /reportar (US2, US3), /leida (US7), /revisar y /diagnosticar (US5),
/resolver (US8), /panel (US4, US6, US9) y /fotos/<archivo> para mostrar las imágenes.
"""
import atexit
import html
import re
import shutil
import sys
import tempfile
import uuid
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from app import (db, diagnosticos, estadisticas, notificaciones, reportes,
                 usuarios)
from app.errores import ErrorDominio, ErrorValidacion

CONN = db.conectar()
CARPETA_FOTOS = Path(tempfile.mkdtemp(prefix="plagas_fotos_"))
atexit.register(shutil.rmtree, CARPETA_FOTOS, ignore_errors=True)
MAX_BYTES = 10 * 1024 * 1024  # tope de la petición completa (todas las fotos juntas)
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


def detectar_extension(datos: bytes) -> str:
    """Devuelve la extensión real del archivo según sus primeros bytes.

    Se mira el contenido y no el nombre: un .exe renombrado a .jpg no debe pasar.

    Raises:
        ErrorValidacion: El archivo no es una imagen JPG o PNG.
    """
    if datos.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    raise ErrorValidacion("Solo se permiten imágenes .jpg, .jpeg o .png.")


def miniaturas(reporte_id: int) -> str:
    """Muestra las fotos de un reporte; si el archivo no existe, solo su nombre."""
    piezas = []
    for fila in CONN.execute("SELECT nombre_archivo FROM foto WHERE reporte_id = ?", (reporte_id,)):
        nombre = fila["nombre_archivo"]
        if (CARPETA_FOTOS / nombre).is_file():
            piezas.append(f'<a href="/fotos/{nombre}" target=_blank><img src="/fotos/{nombre}" '
                          f'style="height:90px;border-radius:6px;margin:.3rem .3rem 0 0"></a>')
        else:
            # Los reportes de ejemplo solo tienen el nombre, sin archivo real.
            piezas.append(f"<small>📷 {html.escape(nombre)} (ejemplo)</small> ")
    return "".join(piezas)


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
        f'<span class="tag">{r["estado"]}</span><br><small>{html.escape(r["ubicacion"])}</small>'
        f'<br>{miniaturas(r["id"])}</div>'
        for r in reportes.listar_mis_reportes(CONN, uid)) or "<p>Sin reportes.</p>"
    notas = "".join(
        f'<div class="card">{"🔔" if not n["leida"] else "✔"} {html.escape(n["mensaje"])}'
        + (f'<form method=post action=/leida style="display:inline"><input type=hidden name=u '
           f'value={uid}><input type=hidden name=n value={n["id"]}><button>Marcar leída</button>'
           f'</form>' if not n["leida"] else "") + "</div>"
        for n in notificaciones.listar_notificaciones(CONN, uid)) or "<p>Sin notificaciones.</p>"
    return (f'<h2>Hola, {html.escape(u["nombre"])} (campesino)</h2>'
            f'<div class="card"><h3>Nuevo reporte (US2, US3)</h3><form method=post '
            f'action="/reportar?u={uid}" enctype="multipart/form-data">'
            f'<input type=hidden name=u value={uid}>Descripción<textarea name=descripcion></textarea>'
            f'Ubicación (dirección o "lat, lon")<input name=ubicacion>'
            f'Fotos de la afectación (JPG o PNG, máx. 10 MB en total)'
            f'<input type=file name=fotos accept="image/png,image/jpeg" multiple>'
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
        f'<small>({html.escape(r["ubicacion"])})</small><br>{miniaturas(r["id"])}<br>'
        f'{boton("/revisar", r["id"], "Iniciar revisión")}'
        f'<form method=post action=/diagnosticar><input type=hidden name=u value={uid}>'
        f'<input type=hidden name=r value={r["id"]}>Diagnóstico<input name=texto>'
        f'Recomendación<input name=recomendacion><button>Diagnosticar</button></form></div>'
        for r in reportes.listar_pendientes(CONN, uid)) or "<p>No hay reportes pendientes.</p>"
    # Los casos diagnosticados o en revisión no salen en "pendientes" (US4): se listan aparte.
    otros = CONN.execute("SELECT id, descripcion, estado FROM reporte WHERE estado "
                         "IN ('En revisión','Diagnosticado') ORDER BY id").fetchall()
    seguimiento = "".join(
        f'<div class="card">#{r["id"]} {html.escape(r["descripcion"])} — '
        f'<span class="tag">{r["estado"]}</span><br>{miniaturas(r["id"])}<br>'
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

    def _enviar_foto(self, archivo: Path) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "image/png" if archivo.suffix == ".png" else "image/jpeg")
        self.end_headers()
        self.wfile.write(archivo.read_bytes())

    def _leer_formulario(self) -> tuple[dict[str, str], list[bytes]]:
        """Lee el cuerpo del POST (normal o con archivos) y devuelve (campos, fotos).

        Raises:
            ErrorValidacion: La petición supera el tamaño máximo.
        """
        largo = int(self.headers.get("Content-Length", 0))
        if largo > MAX_BYTES:
            # Se descarta el cuerpo para no dejar la conexión a medias.
            while largo > 0:
                leido = self.rfile.read(min(65536, largo))
                if not leido:
                    break
                largo -= len(leido)
            raise ErrorValidacion("Las fotos pesan demasiado: el máximo es 10 MB en total.")
        cuerpo = self.rfile.read(largo)
        tipo = self.headers.get("Content-Type", "")
        if not tipo.startswith("multipart/form-data"):
            return {k: v[0] for k, v in parse_qs(cuerpo.decode()).items()}, []
        # El módulo "cgi" se eliminó en Python 3.13, por eso se usa "email" para leer el formulario.
        mensaje = BytesParser(policy=policy.default).parsebytes(
            b"Content-Type: " + tipo.encode() + b"\r\n\r\n" + cuerpo)
        campos: dict[str, str] = {}
        fotos: list[bytes] = []
        for parte in mensaje.iter_parts():
            datos = parte.get_payload(decode=True) or b""
            if parte.get_filename() is None:
                campos[parte.get_param("name", header="content-disposition")] = datos.decode("utf-8")
            elif datos:  # un campo de archivo vacío significa que no eligió foto
                fotos.append(datos)
        return campos, fotos

    def _volver(self, uid: int, msg: str = "") -> None:
        self.send_response(303)
        self.send_header("Location", f"/panel?u={uid}&msg={quote(msg)}")
        self.end_headers()

    def do_GET(self) -> None:
        url = urlparse(self.path)
        q = parse_qs(url.query)
        # Solo nombres generados por la demo: evita que se pida un archivo fuera de la carpeta.
        foto = re.fullmatch(r"/fotos/([0-9a-f]{32}\.(?:jpg|png))", url.path)
        if foto:
            archivo = CARPETA_FOTOS / foto.group(1)
            if archivo.is_file():
                return self._enviar_foto(archivo)
            return self._responder(pagina("<p>Foto no encontrada.</p>"), 404)
        if url.path == "/panel" and "u" in q:
            u = usuarios.obtener_usuario(CONN, int(q["u"][0]))
            vista = vista_campesino if u["rol"] == "campesino" else vista_profesional
            return self._responder(pagina(vista(u), q.get("msg", [""])[0]))
        self._responder(pagina(vista_login(), parse_qs(url.query).get("msg", [""])[0]))

    def do_POST(self) -> None:
        url = urlparse(self.path)
        # El formulario con fotos también lleva ?u= en la URL, por si el cuerpo no se puede leer.
        uid_url = parse_qs(url.query).get("u", [None])[0]
        f: dict[str, str] = {}
        try:
            f, fotos = self._leer_formulario()
            ruta = url.path
            if ruta == "/login":
                u = usuarios.iniciar_sesion(CONN, f.get("email", ""), f.get("password", ""))
                return self._volver(u["id"], f"Bienvenido/a, {u['nombre']}.")
            uid, rid = int(f.get("u") or uid_url), int(f.get("r", 0))
            if ruta == "/reportar":
                # Nombre generado por la demo: nunca se usa el que trae el archivo.
                nombres = [uuid.uuid4().hex + detectar_extension(d) for d in fotos]
                n = reportes.crear_reporte(CONN, uid, f.get("descripcion", ""), f.get("ubicacion", ""),
                                           nombres, f.get("tipo_plaga"), f.get("zona"))
                # Se escribe en disco solo si el reporte fue válido: así no quedan fotos huérfanas.
                for nombre, datos in zip(nombres, fotos):
                    (CARPETA_FOTOS / nombre).write_bytes(datos)
                msg = f"Reporte #{n} enviado con {len(nombres)} foto(s)."
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
            uid = f.get("u") or uid_url
            if uid:
                return self._volver(int(uid), f"⚠ {e}")
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
