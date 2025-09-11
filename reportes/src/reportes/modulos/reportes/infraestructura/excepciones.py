"""Excepciones de la capa de infraestructura de reportes."""


class ExcepcionInfraestructuraReportes(Exception):
    """Excepción base de infraestructura para reportes."""
    pass


class ExcepcionFabricaReportes(ExcepcionInfraestructuraReportes):
    """Excepción en las fábricas de reportes."""
    pass


class ExcepcionRepositorioReportes(ExcepcionInfraestructuraReportes):
    """Excepción en el repositorio de reportes."""
    pass


class ExcepcionConsumidorReportes(ExcepcionInfraestructuraReportes):
    """Excepción en el consumidor de eventos de reportes."""
    pass
