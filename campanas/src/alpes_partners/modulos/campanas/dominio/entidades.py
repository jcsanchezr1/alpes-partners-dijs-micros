from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from alpes_partners.seedwork.dominio.entidades import AgregacionRaiz
from alpes_partners.seedwork.dominio.objetos_valor import Dinero
from alpes_partners.seedwork.dominio.excepciones import ExcepcionReglaDeNegocio, ExcepcionEstadoInvalido
from .objetos_valor import (
    TipoComision, EstadoCampana, TerminosComision, PeriodoCampana,
    MaterialPromocional, CriteriosAfiliado, MetricasCampana
)
from .eventos import (
    CampanaCreada
)


class Campana(AgregacionRaiz):
    """Agregado raíz para Campana."""
    
    def __init__(self, 
                 nombre: str,
                 descripcion: str,
                 terminos_comision: TerminosComision,
                 periodo: PeriodoCampana,
                 material_promocional: MaterialPromocional,
                 criterios_afiliado: CriteriosAfiliado,
                 id: Optional[str] = None):
        super().__init__(id)
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()
        self.terminos_comision = terminos_comision
        self.periodo = periodo
        self.material_promocional = material_promocional
        self.criterios_afiliado = criterios_afiliado
        self.estado = EstadoCampana.BORRADOR
        self.metricas = MetricasCampana()
        self.afiliados_asignados: Set[str] = set()
        self.fecha_activacion: Optional[datetime] = None
        self.fecha_pausa: Optional[datetime] = None
        
        # Información del influencer origen (para eventos)
        self.influencer_origen_id: Optional[str] = None
        self.influencer_origen_nombre: Optional[str] = None
        self.influencer_origen_email: Optional[str] = None
        self.categoria_origen: Optional[str] = None
        
        # Validaciones
        if not self.nombre:
            raise ExcepcionReglaDeNegocio("El nombre de la campana es requerido")
        
        if not self.descripcion:
            raise ExcepcionReglaDeNegocio("La descripción de la campana es requerida")
        
        # El evento se emitirá después de asignar los datos del influencer
    
    @classmethod
    def crear(cls, 
              nombre: str,
              descripcion: str,
              tipo_comision: TipoComision,
              valor_comision: float,
              moneda: str,
              fecha_inicio: datetime,
              fecha_fin: Optional[datetime] = None,
              titulo_material: str = "",
              descripcion_material: str = "",
              categorias_objetivo: List[str] = None,
              tipos_afiliado_permitidos: List[str] = None) -> 'Campana':
        """Factory method para crear una campana."""
        
        # Crear objetos valor
        dinero_comision = Dinero(valor_comision, moneda)
        terminos = TerminosComision(tipo_comision, dinero_comision)
        periodo = PeriodoCampana(fecha_inicio, fecha_fin)
        
        # Material promocional básico
        material = MaterialPromocional(
            titulo=titulo_material or f"Material para {nombre}",
            descripcion=descripcion_material or descripcion
        )
        
        # Criterios de afiliado
        criterios = CriteriosAfiliado(
            tipos_permitidos=tipos_afiliado_permitidos or [],
            categorias_requeridas=categorias_objetivo or []
        )
        
        return cls(
            nombre=nombre,
            descripcion=descripcion,
            terminos_comision=terminos,
            periodo=periodo,
            material_promocional=material,
            criterios_afiliado=criterios
        )
    
    def crear_campana(self, campana: 'Campana') -> None:
        """Método para crear la campana y emitir el evento correspondiente."""
        # Emitir evento de creación
        from .eventos import CampanaCreada
        self.agregar_evento(CampanaCreada(
            campana_id=self.id,
            nombre=self.nombre,
            descripcion=self.descripcion,
            tipo_comision=self.terminos_comision.tipo,
            valor_comision=self.terminos_comision.valor.cantidad,
            moneda=self.terminos_comision.valor.moneda,
            categorias_objetivo=self.criterios_afiliado.categorias_requeridas,
            fecha_inicio=self.periodo.fecha_inicio,
            fecha_fin=self.periodo.fecha_fin,
            influencer_id=self.influencer_origen_id,
            influencer_nombre=self.influencer_origen_nombre,
            influencer_email=self.influencer_origen_email
        ))
    
    def emitir_evento_creacion(self) -> None:
        """Emite el evento de creación de campaña con los datos del influencer actualizados."""
        from .eventos import CampanaCreada
        self.agregar_evento(CampanaCreada(
            campana_id=self.id,
            nombre=self.nombre,
            descripcion=self.descripcion,
            tipo_comision=self.terminos_comision.tipo,
            valor_comision=self.terminos_comision.valor.cantidad,
            moneda=self.terminos_comision.valor.moneda,
            categorias_objetivo=self.criterios_afiliado.categorias_requeridas,
            fecha_inicio=self.periodo.fecha_inicio,
            fecha_fin=self.periodo.fecha_fin,
            influencer_id=self.influencer_origen_id,
            influencer_nombre=self.influencer_origen_nombre,
            influencer_email=self.influencer_origen_email
        ))
