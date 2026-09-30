# Sistema Web Control de Plagas en Plátano

Aplicación para que campesinos del Llano Oriental reporten afectaciones en sus cultivos de plátano con fotos y ubicación, y para que un profesional agrónomo las diagnostique y haga seguimiento hasta resolverlas.

Proyecto académico — Politécnico Grancolombiano, Tecnología en Desarrollo de Software, desarrollado con Scrum.
|||
|---|---|
| **Docente** | Edilberto Torres Ortiz |
| **Scrum Master** | Nicolás Abril Cárdenas |
| **Product Owner** | Juan Miguel Parra Garzón |
| **Equipo de desarrollo** | Santiago Cortez Mojica |

## Estado del proyecto

Sprints 0 a 3 completados. Historias entregadas (todas en estado "Completada" en el Product Backlog):

| Sprint | Historias | Contenido |
|---|---|---|
| 1 | US1, US2, US3 | Registro del campesino, reporte con fotos, ubicación del cultivo |
| 2 | US4, US5, US6 | Reportes pendientes, diagnóstico del profesional, estado del reporte |
| 3 | US7, US8, US9 | Notificaciones, cierre de caso, panel de estadísticas |

Candidata para el Sprint 4: exportar el panel de estadísticas a PDF o Excel.

> **Nota:** el repositorio contiene la lógica de negocio y la base de datos, con sus pruebas unitarias, un recorrido en consola y una demo web de demostración. La interfaz web de producción (API y pantallas definitivas) se construye sobre esta misma lógica.

## Requisitos

- Python 3.10 o superior (probado con 3.14)
- `pip`
- No se necesita instalar una base de datos: se usa SQLite, que ya viene con Python.

## Instalación

```bash
git clone https://github.com/Nicolas4Cardenas/Practicas-Proyecto.git
cd Practicas-Proyecto

# Opcional pero recomendado: entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

python -m pip install -r requirements.txt
```

## Cómo correr el proyecto

Todos los comandos se ejecutan desde la carpeta raíz (la que contiene `app`, `tests` y `schema.sql`).

Para ver la **demo web** (pantallas de campesino y profesional, sobre la misma lógica):

```bash
python demo_web.py          # abrir http://localhost:8000
```

Usuarios de ejemplo: `carlos@finca.co` (campesino) y `laura@agro.co` (profesional), contraseña `clave1234`. Usa base de datos en memoria; al reiniciar vuelve a los datos de ejemplo.

Para ver el flujo completo en la consola (registro → reporte → diagnóstico → notificación → cierre → estadísticas):

```bash
python demo.py
```

El script usa una base de datos en memoria, así que se puede ejecutar cuantas veces se quiera sin dejar archivos.

Para usar la lógica desde otro código:

```python
from app import db, usuarios, reportes

conn = db.conectar("plagas.db")   # o ":memory:" para no guardar nada
db.inicializar(conn)

campesino = usuarios.registrar_usuario(conn, "Carlos", "carlos@finca.co", "clave1234")
reportes.crear_reporte(conn, campesino, "Hojas con manchas", "Vereda La Esperanza", ["hoja.jpg"])
```

## Cómo correr las pruebas

```bash
python -m pytest            # todas las pruebas
python -m pytest -v         # con el nombre de cada prueba
python -m pytest tests/test_us7_estados_notificaciones.py   # solo una historia
```

Resultado esperado: `69 passed`. Las pruebas usan una base de datos en memoria, por lo que no afectan ningún dato real.

> Ejecutar siempre `python -m pytest` desde la carpeta raíz del proyecto. Si se corre desde otra carpeta, Python no encuentra el paquete `app`.

## Arquitectura

El sistema está organizado en capas simples, cada archivo con una sola responsabilidad:

```
Practicas-Proyecto/
├── README.md
├── schema.sql               # Tablas: usuario, reporte, foto, diagnostico, notificacion
├── app/                     # Lógica de negocio
│   ├── db.py                # Conexión a SQLite y creación de tablas
│   ├── errores.py           # Excepciones de dominio
│   ├── usuarios.py          # US1  Registro e inicio de sesión
│   ├── reportes.py          # US2, US3, US4, US6  Reportes, ubicación y listados
│   ├── estados.py           # US7  Estados del reporte y notificación automática
│   ├── diagnosticos.py      # US5, US8  Diagnóstico y cierre del caso
│   ├── notificaciones.py    # US7  Consulta y lectura de notificaciones
│   └── estadisticas.py      # US9  Conteo por estado, zona y tipo de plaga
├── tests/                   # Pruebas unitarias con pytest, una por área
├── docs/                    # Documentación del equipo
│   ├── DoD_Control_Plagas_Platano.pdf   # Definition of Done
│   ├── ESTANDAR_DOCUMENTACION.md        # Estándar de comentarios y docstrings (v1.1)
│   └── ACTA_EPS.md                      # Acta de Entrega Parcial de Software
├── demo.py                  # Recorrido de demostración en consola
├── demo_web.py              # Demo web (http.server) sobre la lógica de app/
├── requirements.txt / pytest.ini
└── .gitignore
```

**Roles.** Hay dos: *campesino* (reporta y consulta sus reportes y notificaciones) y *profesional* (ve pendientes, diagnostica, cierra casos y consulta estadísticas). Cada función valida el rol antes de actuar.

**Ciclo de vida del reporte.** Es la regla central del sistema:

```
Reportado ──► En revisión ──► Diagnosticado ──► Resuelto
    └──────────────────────────►┘
```

Un reporte también puede pasar directo de "Reportado" a "Diagnosticado". No se permiten otros saltos, y cada cambio válido genera una notificación para el campesino dueño del reporte (`estados.py`).

**Base de datos.** SQLite mediante el módulo estándar `sqlite3`, con consultas parametrizadas. Las contraseñas se guardan con PBKDF2 y sal, nunca en texto plano.

## Estándar de código

Las convenciones de comentarios, docstrings y nombres están en [`docs/ESTANDAR_DOCUMENTACION.md`](docs/ESTANDAR_DOCUMENTACION.md). Aplican a todo código nuevo y hacen parte del Definition of Done.

## Trabajo en equipo

- Se trabaja por sprints con Scrum (planeación, daily, review y retrospectiva).
- Una historia se considera terminada cuando cumple el [Definition of Done](docs/DoD_Control_Plagas_Platano.pdf) del equipo.
- Los mensajes de commit indican la historia: `US7: notificar al campesino al cambiar el estado`.
