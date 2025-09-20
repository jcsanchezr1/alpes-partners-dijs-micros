from ....seedwork.dominio.excepciones import ExcepcionDominio


class InfluencerNoEncontrado(ExcepcionDominio):
    """Excepción lanzada cuando no se encuentra un influencer."""
    pass

class PlataformaNoSoportada(ExcepcionDominio):
    """Excepción lanzada cuando se intenta usar una plataforma no soportada."""
    pass


class DatosAudienciaInvalidos(ExcepcionDominio):
    """Excepción lanzada cuando los datos de audiencia son inválidos."""
    pass


class EngagementInvalido(ExcepcionDominio):
    """Excepción lanzada cuando el engagement rate es inválido."""
    pass


class CategoriaInvalida(ExcepcionDominio):
    """Excepción lanzada cuando se proporciona una categoría inválida."""
    pass


class TipoObjetoNoExisteEnDominioInfluencersExcepcion(ExcepcionDominio):
    """Excepción lanzada cuando se intenta crear un objeto que no existe en el dominio de influencers."""
    pass
