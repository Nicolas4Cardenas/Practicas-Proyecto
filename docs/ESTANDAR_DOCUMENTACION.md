# Estándar de comentarios y documentación del código

**Proyecto:** Sistema Web Control de Plagas en Plátano  
**Aplica a:** todo el código Python y SQL del repositorio. Es parte del Definition of Done.

## 1. Idioma y nombres

- Comentarios, docstrings y mensajes de error para el usuario: **en español**.
- Nombres de funciones y variables: `snake_case` en español, descriptivos (`registrar_diagnostico`, no `reg_diag`).
- Constantes en `MAYUSCULAS` (`ESTADOS`, `EXTENSIONES_VALIDAS`). Nombres privados con guion bajo inicial (`_hashear`).
- Tablas y columnas SQL en minúscula y singular (`reporte`, `usuario_id`).

## 2. Docstring de módulo

Cada archivo `.py` inicia con una línea que dice qué hace e indica la historia de usuario que implementa.

```python
"""US7 - Máquina de estados del reporte y notificaciones por cambio de estado."""
```

## 3. Docstring de función

Toda función pública lleva docstring con estilo Google. Resumen en una línea; luego, solo las secciones que apliquen:

| Sección | Cuándo se incluye |
|---|---|
| `Args:` | Si hay parámetros que no se explican solos |
| `Returns:` | Si devuelve algo distinto de `None` |
| `Raises:` | Siempre que lance excepciones de dominio |

```python
def marcar_resuelto(conn: sqlite3.Connection, reporte_id: int, profesional_id: int) -> None:
    """Cierra un caso diagnosticado como "Resuelto" (US8).

    Raises:
        ErrorPermiso: El usuario no es profesional.
        ErrorTransicion: El reporte no está en estado "Diagnosticado".
    """
```

Las funciones privadas cortas (`_verificar`) no necesitan docstring si el nombre es claro.

## 4. Anotaciones de tipo

Todos los parámetros y retornos de funciones públicas llevan anotaciones (`usuario_id: int`, `-> list[sqlite3.Row]`).

## 5. Comentarios en línea

- Explican el **porqué**, no el qué. Mal: `# suma 1 al contador`. Bien: `# El PRAGMA es necesario: SQLite no activa las llaves foráneas por defecto.`
- Van en su propia línea, encima del código que explican.
- Si una regla de negocio viene de una historia o de una decisión del equipo, se cita: `# US4: los más antiguos primero, son los más urgentes.`
- No se deja código comentado ni `TODO` sin responsable y fecha.

## 6. SQL

- Siempre consultas **parametrizadas** (`?`), nunca datos del usuario concatenados en el texto SQL.
- Las restricciones (`CHECK`, `UNIQUE`, `REFERENCES`) se definen en `schema.sql` y llevan un comentario `--` si no son evidentes.

## 7. Errores

- La lógica lanza excepciones de `app/errores.py` (`ErrorValidacion`, `ErrorPermiso`, `ErrorTransicion`, `ErrorNoEncontrado`, `ErrorAutenticacion`).
- El mensaje debe poder mostrarse tal cual al usuario y decir qué corregir.

## 8. Pruebas

- Un archivo por área: `tests/test_us<N>_<tema>.py`.
- Nombre de la prueba = comportamiento esperado: `test_no_se_puede_resolver_un_reporte_sin_diagnosticar`.
- Cada historia con lógica de negocio tiene al menos una prueba del caso válido y una de cada regla de rechazo.

## 9. Commits

Formato: `US<N>: qué se hizo`, en presente e imperativo, por ejemplo `US9: filtrar estadísticas por zona`.

## 10. Lista de revisión rápida

- [ ] Docstring de módulo con la historia
- [ ] Docstring en funciones públicas, con `Raises:` si aplica
- [ ] Anotaciones de tipo
- [ ] Comentarios que explican el porqué
- [ ] SQL parametrizado
- [ ] Pruebas nuevas o actualizadas y `python -m pytest` en verde
