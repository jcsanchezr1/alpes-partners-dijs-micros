"""Excepciones del dominio."""


class ExcepcionDominio(Exception):
    """Excepción base del dominio."""
    pass


class ExcepcionReglaDeNegocio(ExcepcionDominio):
    """Excepción cuando se viola una regla de negocio."""
    pass


class ExcepcionEntidadNoEncontrada(ExcepcionDominio):
    """Excepción cuando no se encuentra una entidad."""
    pass


class ExcepcionEntidadYaExiste(ExcepcionDominio):
    """Excepción cuando una entidad ya existe."""
    pass


class ExcepcionEstadoInvalido(ExcepcionDominio):
    """Excepción cuando una entidad está en un estado inválido."""
    pass


class ExcepcionPermisosDenegados(ExcepcionDominio):
    """Excepción cuando no se tienen permisos para realizar una operación."""
    pass
