"""Excepciones del dominio de campanas

En este archivo usted encontrará las diferentes excepciones del dominio de campanas

"""

from alpes_partners.seedwork.dominio.excepciones import ExcepcionDominio


class ExcepcionDominioCampanas(ExcepcionDominio):
    """Excepción base para el dominio de campanas"""
    pass


class TipoObjetoNoExisteEnDominioCampanasExcepcion(ExcepcionDominioCampanas):
    """Excepción lanzada cuando se intenta crear un objeto que no existe en el dominio"""
    pass


class CampanaYaExisteExcepcion(ExcepcionDominioCampanas):
    """Excepción lanzada cuando se intenta crear una campana que ya existe"""
    pass


class CampanaNoEncontradaExcepcion(ExcepcionDominioCampanas):
    """Excepción lanzada cuando no se encuentra una campana"""
    pass


class EstadoCampanaInvalidoExcepcion(ExcepcionDominioCampanas):
    """Excepción lanzada cuando se intenta realizar una operación con un estado inválido"""
    pass


class ParametrosCampanaInvalidosExcepcion(ExcepcionDominioCampanas):
    """Excepción lanzada cuando los parámetros de la campana son inválidos"""
    pass


class CampanaNoExisteExcepcion(ExcepcionDominioCampanas):
    """Excepción lanzada cuando se intenta eliminar una campaña que no existe"""
    pass
