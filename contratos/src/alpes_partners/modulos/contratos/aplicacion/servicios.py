import logging
from typing import List, Optional

from ..dominio.repositorios import RepositorioContratos
from ..dominio.entidades import Contrato
from ..dominio.objetos_valor import TipoContrato, EstadoContrato

from alpes_partners.seedwork.infraestructura.uow import UnidadTrabajo
from .dto import ContratoDTO, CrearContratoDTO

logger = logging.getLogger(__name__)


class ServicioContrato:
    """Servicio de aplicación para operaciones de contratos."""
    
    def __init__(self, repositorio: RepositorioContratos, uow: UnidadTrabajo):
        self._repositorio = repositorio
        self._uow = uow
    
    @property
    def repositorio(self):
        return self._repositorio
    
    @property
    def uow(self):
        return self._uow
    
    def listar_contratos(
        self,
        estado: Optional[EstadoContrato] = None,
        tipo: Optional[TipoContrato] = None,
        categoria: Optional[str] = None,
        influencer_id: Optional[str] = None,
        campana_id: Optional[str] = None,
        monto_minimo: Optional[float] = None,
        monto_maximo: Optional[float] = None,
        limite: int = 100,
        offset: int = 0
    ) -> List[ContratoDTO]:
        """Lista contratos con filtros opcionales."""
        logger.info("SERVICIO: Obteniendo lista de contratos con filtros")
        
        contratos = self.repositorio.obtener_con_filtros(
            estado=estado,
            tipo=tipo,
            categoria=categoria,
            influencer_id=influencer_id,
            campana_id=campana_id,
            monto_minimo=monto_minimo,
            monto_maximo=monto_maximo,
            limite=limite,
            offset=offset
        )
        
        logger.info(f"SERVICIO: {len(contratos)} contratos encontrados")
        return [self._convertir_a_dto(contrato) for contrato in contratos]
    
    def _convertir_a_dto(self, contrato: Contrato) -> ContratoDTO:
        """Convierte una entidad Contrato a DTO."""
        
        return ContratoDTO(
            id=contrato.id,
            influencer_id=contrato.influencer.influencer_id,
            influencer_nombre=contrato.influencer.nombre,
            influencer_email=contrato.influencer.email,
            campana_id=contrato.campana.campana_id,
            campana_nombre=contrato.campana.nombre,
            estado=contrato.estado,
            tipo_contrato=contrato.tipo_contrato,
            categorias=contrato.terminos.categorias.categorias,
            descripcion=contrato.terminos.descripcion,
            entregables=contrato.terminos.entregables,
            monto_base=contrato.compensacion.monto_base.cantidad,
            moneda=contrato.compensacion.monto_base.moneda,
            fecha_inicio=contrato.periodo.fecha_inicio.isoformat() if contrato.periodo.fecha_inicio else "",
            fecha_fin=contrato.periodo.fecha_fin.isoformat() if contrato.periodo.fecha_fin else None,
            fecha_creacion=contrato.fecha_creacion.isoformat() if contrato.fecha_creacion else "",
            fecha_firma=contrato.fecha_firma.isoformat() if contrato.fecha_firma else None,
            fecha_finalizacion=contrato.fecha_finalizacion.isoformat() if contrato.fecha_finalizacion else None,
            entregables_completados=contrato.metricas.entregables_completados,
            engagement_alcanzado=contrato.metricas.engagement_alcanzado,
            costo_total=contrato.metricas.costo_total,
            roi_obtenido=contrato.metricas.roi_obtenido
        )