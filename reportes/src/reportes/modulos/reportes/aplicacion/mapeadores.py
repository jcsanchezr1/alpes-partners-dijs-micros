from datetime import datetime
from typing import Dict, Any

from reportes.seedwork.dominio.repositorios import Mapeador
from reportes.seedwork.dominio.entidades import AgregacionRaiz

from .dto import CrearReporteDTO, ReporteDTO
from ..dominio.entidades import Reporte
from ..dominio.objetos_valor import TipoReporte, MetadatosReporte, ConfiguracionReporte


class MapeadorReporte(Mapeador):
    """Mapeador para convertir entre DTOs y entidades de Reporte."""
    
    def obtener_tipo(self) -> type:
        return Reporte
    
    def entidad_a_dto(self, entidad: Reporte) -> ReporteDTO:
        """Convierte una entidad Reporte a DTO."""
        return ReporteDTO(
            id=entidad.id,
            nombre=entidad.nombre,
            descripcion=entidad.descripcion,
            tipo_reporte=entidad.tipo_reporte.value,
            estado=entidad.estado.value,
            datos_origen=entidad.datos_origen,
            origen_evento=entidad.metadatos.origen_evento,
            fecha_creacion=entidad.fecha_creacion,
            fecha_actualizacion=entidad.fecha_actualizacion,
        )
    
    def dto_a_entidad(self, dto: CrearReporteDTO) -> Reporte:
        """Convierte un DTO a entidad Reporte."""
        
        # Crear objetos valor
        tipo_reporte = TipoReporte(dto.tipo_reporte)
        
        metadatos = MetadatosReporte(
            origen_evento=dto.origen_evento,
            version_esquema=dto.version_esquema,
            datos_adicionales=dto.datos_adicionales or {}
        )
        
        configuracion = ConfiguracionReporte(
            incluir_metricas=dto.incluir_metricas,
            formato_salida=dto.formato_salida,
            notificar_completado=dto.notificar_completado
        )
        
        # Crear la entidad
        reporte = Reporte(
            nombre=dto.nombre,
            descripcion=dto.descripcion,
            tipo_reporte=tipo_reporte,
            datos_origen=dto.datos_origen,
            metadatos=metadatos,
            configuracion=configuracion,
            id=dto.id
        )
        
        # Establecer fechas si están presentes en el DTO
        if hasattr(dto, 'fecha_creacion') and dto.fecha_creacion:
            try:
                reporte.fecha_creacion = datetime.fromisoformat(dto.fecha_creacion.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass  # Usar fecha por defecto
        
        if hasattr(dto, 'fecha_actualizacion') and dto.fecha_actualizacion:
            try:
                reporte.fecha_actualizacion = datetime.fromisoformat(dto.fecha_actualizacion.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass  # Usar fecha por defecto
        
        return reporte
