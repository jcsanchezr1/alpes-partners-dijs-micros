"""Excepciones específicas del dominio de reportes."""

from reportes.seedwork.dominio.excepciones import ExcepcionDominio


class ExcepcionReporte(ExcepcionDominio):
    """Excepción base para el dominio de reportes."""
    pass


class ExcepcionReporteNoEncontrado(ExcepcionReporte):
    """Excepción cuando no se encuentra un reporte."""
    pass


class ExcepcionReporteYaExiste(ExcepcionReporte):
    """Excepción cuando un reporte ya existe."""
    pass


class ExcepcionEstadoReporteInvalido(ExcepcionReporte):
    """Excepción cuando un reporte está en un estado inválido."""
    pass


class ExcepcionProcesamientoReporte(ExcepcionReporte):
    """Excepción durante el procesamiento de un reporte."""
    pass


class TipoObjetoNoExisteEnDominioReportesExcepcion(ExcepcionReporte):
    """Excepción cuando no se puede crear un objeto para el tipo especificado."""
    pass
