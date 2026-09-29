"""Excepciones de dominio del sistema."""


class ErrorDominio(Exception):
    """Clase base de los errores de negocio."""


class ErrorValidacion(ErrorDominio):
    """Datos de entrada inválidos o incompletos."""


class ErrorAutenticacion(ErrorDominio):
    """Credenciales incorrectas."""


class ErrorPermiso(ErrorDominio):
    """El usuario no tiene el rol requerido para la acción."""


class ErrorNoEncontrado(ErrorDominio):
    """El recurso solicitado no existe."""


class ErrorTransicion(ErrorDominio):
    """Cambio de estado no permitido para un reporte."""
