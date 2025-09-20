import logging
from typing import List, Optional

from ..dominio.repositorios import RepositorioInfluencers
from ..dominio.entidades import Influencer
from ..dominio.objetos_valor import TipoInfluencer, EstadoInfluencer, Plataforma
from ..dominio.excepciones import InfluencerNoEncontrado

from alpes_partners.seedwork.infraestructura.uow import UnidadTrabajo
from .dto import InfluencerDTO, RegistrarInfluencerDTO

from typing import Union

logger = logging.getLogger(__name__)


class ServicioInfluencer:
    """Servicio de aplicación para operaciones de influencers."""
    
    def __init__(self, repositorio: RepositorioInfluencers, uow: UnidadTrabajo):
        self._repositorio = repositorio
        self._uow = uow
    
    @property
    def repositorio(self):
        return self._repositorio
    
    @property
    def uow(self):
        return self._uow
    
    def listar_influencers(
        self,
        estado: Optional[EstadoInfluencer] = None,
        tipo: Optional[TipoInfluencer] = None,
        categoria: Optional[str] = None,
        plataforma: Optional[Plataforma] = None,
        min_seguidores: Optional[int] = None,
        max_seguidores: Optional[int] = None,
        engagement_minimo: Optional[float] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[InfluencerDTO]:
        """Lista influencers con filtros opcionales."""
        logger.info("SERVICIO: Obteniendo lista de influencers con filtros")
        
        influencers = self.repositorio.obtener_con_filtros(
            estado=estado,
            tipo=tipo,
            categoria=categoria,
            plataforma=plataforma,
            min_seguidores=min_seguidores,
            max_seguidores=max_seguidores,
            engagement_minimo=engagement_minimo,
            limite=limite,
            offset=offset
        )
        
        logger.info(f"SERVICIO: {len(influencers)} influencers encontrados")
        return [self._convertir_a_dto(influencer) for influencer in influencers]
    
    def _convertir_a_dto(self, influencer: Influencer) -> InfluencerDTO:
        """Convierte una entidad Influencer a DTO."""
        
        # Obtener plataformas
        plataformas = [plat.value for plat in influencer.audiencia_por_plataforma.keys()]
        
        # Calcular tipo principal
        tipo_principal = None
        if influencer.obtener_tipo_principal():
            tipo_principal = influencer.obtener_tipo_principal().value
        
        # Convertir demografía si existe
        demografia_dto = None
        if influencer.demografia:
            from .dto import DemografiaDTO
            demografia_dto = DemografiaDTO(
                distribucion_genero=influencer.demografia.distribucion_genero,
                distribucion_edad=influencer.demografia.distribucion_edad,
                paises_principales=influencer.demografia.paises_principales
            )
        
        return InfluencerDTO(
            id=influencer.id,
            nombre=influencer.nombre,
            email=influencer.email.valor,
            estado=influencer.estado,
            categorias=influencer.perfil.categorias.categorias,
            descripcion=influencer.perfil.descripcion,
            biografia=influencer.perfil.biografia,
            sitio_web=influencer.perfil.sitio_web,
            telefono=influencer.telefono.numero if influencer.telefono else "",
            fecha_creacion=influencer.fecha_creacion.isoformat() if influencer.fecha_creacion else "",
            fecha_activacion=influencer.fecha_activacion.isoformat() if influencer.fecha_activacion else None,
            plataformas=plataformas,
            total_seguidores=influencer.obtener_total_seguidores(),
            engagement_promedio=influencer.metricas.engagement_promedio,
            tipo_principal=tipo_principal,
            campanas_completadas=influencer.metricas.campanas_completadas,
            cpm_promedio=influencer.metricas.cpm_promedio,
            ingresos_generados=influencer.metricas.ingresos_generados,
            demografia=demografia_dto
        )