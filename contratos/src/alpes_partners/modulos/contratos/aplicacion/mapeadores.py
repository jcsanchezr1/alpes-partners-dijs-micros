""" Mapeadores para la conversión de objetos en la capa de aplicación del dominio de contratos

En este archivo usted encontrará los diferentes mapeadores para convertir
objetos entre DTOs y entidades del dominio de contratos

"""

# Importaciones usando el path correcto para el contexto de ejecución
import sys
import os

# Agregar el directorio src al path si no está
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', '..', '..')
src_path = os.path.normpath(src_path)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from alpes_partners.seedwork.dominio.repositorios import Mapeador
from alpes_partners.modulos.contratos.dominio.entidades import Contrato
from alpes_partners.modulos.contratos.aplicacion.dto import CrearContratoDTO, ContratoDTO

from datetime import datetime


class MapeadorContrato(Mapeador):
    """Mapeador para convertir entre DTOs y Contratos."""
    
    def obtener_tipo(self) -> type:
        return Contrato.__class__
    
    def entidad_a_dto(self, entidad: Contrato) -> ContratoDTO:
        """Convierte una entidad Contrato a DTO."""
        
        return ContratoDTO(
            id=entidad.id,
            influencer_id=entidad.influencer.influencer_id,
            influencer_nombre=entidad.influencer.nombre,
            influencer_email=entidad.influencer.email,
            campana_id=entidad.campana.campana_id,
            campana_nombre=entidad.campana.nombre,
            estado=entidad.estado,
            tipo_contrato=entidad.tipo_contrato,
            categorias=entidad.terminos.categorias.categorias,
            descripcion=entidad.terminos.descripcion,
            entregables=entidad.terminos.entregables,
            monto_base=entidad.compensacion.monto_base.cantidad,
            moneda=entidad.compensacion.monto_base.moneda,
            fecha_inicio=entidad.periodo.fecha_inicio.isoformat(),
            fecha_fin=entidad.periodo.fecha_fin.isoformat() if entidad.periodo.fecha_fin else None,
            fecha_creacion=entidad.fecha_creacion.isoformat(),
            fecha_firma=entidad.fecha_firma.isoformat() if entidad.fecha_firma else None,
            fecha_finalizacion=entidad.fecha_finalizacion.isoformat() if entidad.fecha_finalizacion else None,
            entregables_completados=entidad.metricas.entregables_completados,
            engagement_alcanzado=entidad.metricas.engagement_alcanzado,
            costo_total=entidad.metricas.costo_total,
            roi_obtenido=entidad.metricas.roi_obtenido
        )
    
    def dto_a_entidad(self, dto: CrearContratoDTO) -> Contrato:
        """Convierte un DTO a entidad Contrato."""
        
        from ..dominio.objetos_valor import TipoContrato
        
        # Determinar tipo de contrato
        try:
            tipo_contrato = TipoContrato(dto.tipo_contrato)
        except ValueError:
            tipo_contrato = TipoContrato.PUNTUAL
        
        # Crear contrato usando el método de fábrica de la entidad
        contrato = Contrato.crear(
            influencer_id=dto.influencer_id,
            influencer_nombre=dto.influencer_nombre,
            influencer_email=dto.influencer_email,
            campana_id=dto.campana_id,
            campana_nombre=dto.campana_nombre,
            categorias=dto.categorias,
            descripcion=dto.descripcion,
            monto_base=dto.monto_base,
            moneda=dto.moneda,
            fecha_inicio=datetime.fromisoformat(dto.fecha_inicio),
            fecha_fin=datetime.fromisoformat(dto.fecha_fin) if dto.fecha_fin else None,
            entregables=dto.entregables or "",
            tipo_contrato=tipo_contrato
        )
        
        # Establecer el ID si viene en el DTO (para comandos)
        if hasattr(dto, 'id') and dto.id:
            contrato._id = dto.id
        
        return contrato
