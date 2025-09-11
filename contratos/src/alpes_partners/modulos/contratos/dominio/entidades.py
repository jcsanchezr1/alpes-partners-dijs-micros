from datetime import datetime
from typing import Optional, Dict, List
from ....seedwork.dominio.entidades import AgregacionRaiz
from ....seedwork.dominio.objetos_valor import Email, Telefono
from ....seedwork.dominio.excepciones import ExcepcionReglaDeNegocio, ExcepcionEstadoInvalido
from .objetos_valor import (
    TipoContrato, EstadoContrato, TerminosContrato, 
    MetricasContrato, CategoriaContrato, DatosAudiencia,
    Demografia, Plataforma, PeriodoContrato, CompensacionContrato,
    InfluencerContrato, CampanaContrato
)
from .eventos import ContratoCreado


class Contrato(AgregacionRaiz):
    """Agregado raíz para Contrato entre Influencer y Campaña."""
    
    def __init__(self, 
                 influencer: InfluencerContrato,
                 campana: CampanaContrato,
                 terminos: TerminosContrato,
                 compensacion: CompensacionContrato,
                 periodo: PeriodoContrato,
                 tipo_contrato: TipoContrato = TipoContrato.PUNTUAL,
                 id: Optional[str] = None):
        super().__init__(id)
        self.influencer = influencer
        self.campana = campana
        self.terminos = terminos
        self.compensacion = compensacion
        self.periodo = periodo
        self.tipo_contrato = tipo_contrato
        self.estado = EstadoContrato.BORRADOR
        self.metricas = MetricasContrato()
        self.audiencia_por_plataforma: Dict[Plataforma, DatosAudiencia] = {}
        self.demografia: Optional[Demografia] = None
        self.fecha_firma: Optional[datetime] = None
        self.fecha_finalizacion: Optional[datetime] = None
        
        # Validaciones
        if not self.influencer or not self.campana:
            raise ExcepcionReglaDeNegocio("El influencer y la campaña son requeridos para el contrato")
    
    @classmethod
    def crear(cls, 
              influencer_id: str,
              influencer_nombre: str,
              influencer_email: str,
              campana_id: str,
              campana_nombre: str,
              categorias: list,
              descripcion: str,
              monto_base: float,
              moneda: str,
              fecha_inicio: datetime,
              fecha_fin: datetime = None,
              entregables: str = "",
              tipo_contrato: TipoContrato = TipoContrato.PUNTUAL) -> 'Contrato':
        """Factory method para crear un contrato."""
        
        from ....seedwork.dominio.objetos_valor import Dinero
        
        # Crear objetos valor
        influencer = InfluencerContrato(
            influencer_id=influencer_id,
            nombre=influencer_nombre,
            email=influencer_email,
            plataformas_principales=[]
        )
        
        campana = CampanaContrato(
            campana_id=campana_id,
            nombre=campana_nombre
        )
        
        categoria_obj = CategoriaContrato(categorias)
        terminos = TerminosContrato(
            categorias=categoria_obj,
            descripcion=descripcion,
            entregables=entregables
        )
        
        dinero = Dinero(monto_base, moneda)
        compensacion = CompensacionContrato(monto_base=dinero)
        
        periodo = PeriodoContrato(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return cls(
            influencer=influencer,
            campana=campana,
            terminos=terminos,
            compensacion=compensacion,
            periodo=periodo,
            tipo_contrato=tipo_contrato
        )
    
    def crear_contrato(self, contrato: 'Contrato') -> None:
        """Método para procesar la creación del contrato."""
        # Validar que el contrato esté en estado correcto
        if self.estado != EstadoContrato.BORRADOR:
            raise ExcepcionEstadoInvalido("El contrato debe estar en estado BORRADOR para ser procesado")
        
        # Cambiar estado a pendiente
        self.estado = EstadoContrato.PENDIENTE
        
        # Emitir evento de creación
        self.agregar_evento(ContratoCreado(
            contrato_id=self.id,
            influencer_id=self.influencer.influencer_id,
            campana_id=self.campana.campana_id,
            monto_total=self.compensacion.monto_base.cantidad,
            moneda=self.compensacion.monto_base.moneda,
            fecha_inicio=self.periodo.fecha_inicio,
            fecha_fin=self.periodo.fecha_fin,
            tipo_contrato=self.tipo_contrato.value,
            fecha_creacion=self.fecha_creacion
        ))
    
    def obtener_tipo_principal(self) -> Optional[TipoContrato]:
        """Obtiene el tipo de contrato basado en la plataforma con más seguidores."""
        if not self.audiencia_por_plataforma:
            return self.tipo_contrato
        
        plataforma_principal = max(
            self.audiencia_por_plataforma.values(),
            key=lambda x: x.seguidores
        )
        
        return plataforma_principal.calcular_tipo_influencer()
    
    def obtener_engagement_promedio(self) -> float:
        """Calcula el engagement promedio across todas las plataformas del influencer."""
        if not self.audiencia_por_plataforma:
            return 0.0
        
        total_engagement = sum(datos.engagement_rate for datos in self.audiencia_por_plataforma.values())
        return total_engagement / len(self.audiencia_por_plataforma)
    
    def esta_vigente(self) -> bool:
        """Verifica si el contrato está vigente."""
        return self.estado == EstadoContrato.ACTIVO and self.periodo.esta_vigente()
    
    def obtener_total_seguidores(self) -> int:
        """Obtiene el total de seguidores across todas las plataformas."""
        return sum(datos.seguidores for datos in self.audiencia_por_plataforma.values())
    
    def activar_contrato(self) -> None:
        """Activa el contrato."""
        if self.estado != EstadoContrato.PENDIENTE:
            raise ExcepcionEstadoInvalido("Solo se pueden activar contratos en estado PENDIENTE")
        
        self.estado = EstadoContrato.ACTIVO
        self.fecha_firma = datetime.now()
    
    def finalizar_contrato(self) -> None:
        """Finaliza el contrato."""
        if self.estado != EstadoContrato.ACTIVO:
            raise ExcepcionEstadoInvalido("Solo se pueden finalizar contratos en estado ACTIVO")
        
        self.estado = EstadoContrato.COMPLETADO
        self.fecha_finalizacion = datetime.now()
    
    def cancelar_contrato(self, razon: str = "") -> None:
        """Cancela el contrato."""
        if self.estado in [EstadoContrato.COMPLETADO, EstadoContrato.CANCELADO]:
            raise ExcepcionEstadoInvalido("No se puede cancelar un contrato completado o ya cancelado")
        
        self.estado = EstadoContrato.CANCELADO
        self.fecha_finalizacion = datetime.now()
