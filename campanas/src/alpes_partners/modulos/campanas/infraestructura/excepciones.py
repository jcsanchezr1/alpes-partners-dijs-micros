"""Excepciones de la infraestructura de campanas

En este archivo usted encontrará las diferentes excepciones de la capa de infraestructura de campanas

"""

from alpes_partners.seedwork.dominio.excepciones import ExcepcionDominio


class ExcepcionInfraestructuraCampanas(ExcepcionDominio):
    """Excepción base para la infraestructura de campanas"""
    pass


class ExcepcionFabricaCampanas(ExcepcionInfraestructuraCampanas):
    """Excepción lanzada en las fábricas de campanas"""
    pass


class ExcepcionRepositorioCampanas(ExcepcionInfraestructuraCampanas):
    """Excepción lanzada en los repositorios de campanas"""
    pass


class ExcepcionMapeadorCampanas(ExcepcionInfraestructuraCampanas):
    """Excepción lanzada en los mapeadores de campanas"""
    pass
