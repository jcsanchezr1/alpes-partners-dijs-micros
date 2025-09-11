from ....seedwork.dominio.excepciones import ExcepcionDominio


class ContratoYaExiste(ExcepcionDominio):
    """Excepción lanzada cuando ya existe un contrato activo entre influencer y campaña."""
    pass


class ContratoNoEncontrado(ExcepcionDominio):
    """Excepción lanzada cuando no se encuentra un contrato."""
    pass


class TipoObjetoNoExisteEnDominioContratosExcepcion(ExcepcionDominio):
    """Excepción lanzada cuando se intenta crear un objeto que no existe en el dominio de contratos."""
    pass
