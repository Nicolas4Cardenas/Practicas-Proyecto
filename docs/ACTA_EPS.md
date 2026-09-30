# Acta de Entrega Parcial de Software (EPS)

**Proyecto:** Sistema Web Control de Plagas en Plátano  
**Materia:** Prácticas Aplicadas — Politécnico Grancolombiano, Tecnología en Desarrollo de Software  
**Fecha de la entrega:** 30 de septiembre de 2026  
**Versión del acta:** 1.0

## 1. Datos generales

| | |
|---|---|
| **Docente** | Edilberto Torres Ortiz |
| **Scrum Master** | Nicolás Abril Cárdenas |
| **Product Owner** | Juan Miguel Parra Garzón |
| **Equipo de desarrollo** | Santiago Cortez Mojica |
| **Repositorio** | https://github.com/SayoNara34/Practicas-Proyecto |
| **Metodología** | Scrum (Sprints 0 a 3 completados) |

## 2. Objetivo del producto

Permitir que campesinos del Llano Oriental reporten afectaciones en sus cultivos de plátano con fotos y ubicación, y que un profesional agrónomo las diagnostique y haga seguimiento hasta resolverlas.

## 3. Alcance de esta entrega

Se entregan las historias de usuario US1 a US9, con lógica de negocio, base de datos, pruebas y dos formas de demostración.

| Sprint | Historias | Funcionalidad entregada |
|---|---|---|
| 1 | US1, US2, US3 | Registro e inicio de sesión del campesino; reporte con fotos; ubicación del cultivo (dirección o coordenadas) |
| 2 | US4, US5, US6 | Reportes pendientes para el profesional; diagnóstico con recomendación; estado del reporte para el campesino |
| 3 | US7, US8, US9 | Notificaciones por cambio de estado; cierre del caso; estadísticas por estado, zona y tipo de plaga |

**Ciclo de vida del reporte:** Reportado → En revisión → Diagnosticado → Resuelto (también Reportado → Diagnosticado). No se permiten otros saltos.

### Entregables

| Entregable | Ubicación |
|---|---|
| Lógica de negocio (9 historias) | `app/` |
| Esquema de base de datos (SQLite) | `schema.sql` |
| Pruebas unitarias | `tests/` |
| Recorrido de demostración en consola | `demo.py` |
| **Demo web del producto** | `demo_web.py` |
| Definition of Done | `docs/DoD_Control_Plagas_Platano.pdf` |
| Estándar de documentación (v1.1) | `docs/ESTANDAR_DOCUMENTACION.md` |
| Manual de instalación y ejecución | `README.md` |

## 4. Evidencias verificables

Cada cifra puede reproducirse desde la carpeta raíz del proyecto.

| Evidencia | Comando | Resultado esperado |
|---|---|---|
| Pruebas unitarias | `python -m pytest` | `69 passed` |
| Flujo de extremo a extremo | `python demo.py` | Registro → reporte → diagnóstico → notificación → cierre → estadísticas, sin errores |
| Demo web | `python demo_web.py` y abrir `http://localhost:8000` | Pantallas de campesino y profesional operando sobre la misma lógica |

**Guion sugerido para la demostración web** (usuarios de ejemplo, contraseña `clave1234`):

1. Entrar como `carlos@finca.co` (campesino) y crear un reporte; probar enviarlo vacío para ver los mensajes de validación (US2, US3).
2. Entrar como `laura@agro.co` (profesional), ver los pendientes, iniciar revisión y registrar un diagnóstico (US4, US5).
3. Volver como Carlos: el estado del reporte cambió y hay notificaciones por marcar como leídas (US6, US7).
4. Como Laura, marcar el caso como resuelto y revisar el panel de estadísticas (US8, US9).
5. Intentar resolver un reporte que no está diagnosticado: el sistema lo rechaza con un mensaje claro.

## 5. Cumplimiento del Definition of Done

Los criterios 3 a 6 se comprueban con los comandos de la sección 4. Los criterios 1, 2, 7, 8, 9 y 10 dependen de registros del equipo (Product Backlog, revisión de código, Sprint Review) que no están en el repositorio, por lo que deben confirmarse antes de firmar.

| # | Criterio | Estado | Cómo se verifica |
|---|---|---|---|
| 1 | Criterios de aceptación | Por confirmar | Product Backlog |
| 2 | Código integrado y revisado | Por confirmar | Historial de revisiones del repositorio |
| 3 | Estándar de código | Cumple | `docs/ESTANDAR_DOCUMENTACION.md`, lista de revisión (sección 12) |
| 4 | Pruebas unitarias | Cumple | `python -m pytest` → 69 passed |
| 5 | Prueba de flujo | Cumple | `python demo.py` y demo web |
| 6 | Validaciones y errores | Cumple | Excepciones de dominio con mensajes para el usuario, cubiertas por pruebas |
| 7 | Sin defectos críticos | Por confirmar | Lista de defectos abiertos del equipo |
| 8 | Backlog actualizado | Por confirmar | Product Backlog (US1–US9 en "Completada") |
| 9 | Sprint Review | Por confirmar | Acta del Sprint Review y aceptación del Product Owner |
| 10 | Documentación | Cumple | README y estándar actualizados en esta entrega |

## 6. Limitaciones conocidas

- La interfaz web es una **demostración**: la sesión viaja en la URL, no hay carga real de fotos (se registra solo el nombre del archivo) y los datos viven en memoria.
- No hay API ni pantallas definitivas; se construirán sobre la lógica de `app/` sin duplicar reglas de negocio.
- No hay manual de usuario final independiente del README.

## 7. Próximos pasos

- Sprint 4 (candidata): exportar el panel de estadísticas a PDF o Excel.
- Definir el stack de la interfaz web de producción y la carga real de fotos.
- Actualizar este documento y el DoD si cambia el alcance.

## 8. Aceptación

| Rol | Nombre | Firma | Fecha |
|---|---|---|---|
| Docente | Edilberto Torres Ortiz | | |
| Product Owner | Juan Miguel Parra Garzón | | |
| Scrum Master | Nicolás Abril Cárdenas | | |
| Equipo de desarrollo | Santiago Cortez Mojica | | |

**Observaciones del docente:**

&nbsp;

&nbsp;
