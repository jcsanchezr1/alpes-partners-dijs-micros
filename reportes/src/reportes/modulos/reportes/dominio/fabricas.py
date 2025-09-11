"""Fábricas para la creación de objetos del dominio de reportes.

En este archivo usted encontrará las diferentes fábricas para crear
objetos complejos del dominio de reportes.
"""

from dataclasses import dataclass
from typing import Any, Dict
from datetime import datetime

from reportes.seedwork.dominio.repositorios import Mapeador
from reportes.seedwork.dominio.entidades import Entidad
from reportes.modulos.reportes.aplicacion.dto import CrearReporteDTO

from .entidades import Reporte
from .objetos_valor import TipoReporte, MetadatosReporte, ConfiguracionReporte
from .excepciones import TipoObjetoNoExisteEnDominioReportesExcepcion


@dataclass
class _FabricaReporte:
    """Fábrica interna para crear reportes."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if isinstance(obj, Entidad):
            # Convertir entidad a DTO
            return mapeador.entidad_a_dto(obj) if mapeador else obj
        else:
            # Crear entidad desde DTO o evento
            if isinstance(obj, CrearReporteDTO):
                return self._crear_desde_dto(obj)
            elif isinstance(obj, dict):
                return self._crear_desde_evento(obj)
            elif mapeador:
                return mapeador.dto_a_entidad(obj)
            else:
                return obj
    
    def _crear_desde_dto(self, dto: CrearReporteDTO) -> Reporte:
        """Crea un reporte desde un DTO."""
        
        # Determinar tipo de reporte
        try:
            tipo_reporte = TipoReporte(dto.tipo_reporte)
        except ValueError:
            tipo_reporte = TipoReporte.GENERAL
        
        # Crear metadatos
        metadatos = MetadatosReporte(
            origen_evento=dto.origen_evento,
            version_esquema=dto.version_esquema,
            datos_adicionales=dto.datos_adicionales or {}
        )
        
        # Crear configuración
        configuracion = ConfiguracionReporte(
            incluir_metricas=dto.incluir_metricas,
            formato_salida=dto.formato_salida,
            notificar_completado=dto.notificar_completado
        )
        
        return Reporte(
            nombre=dto.nombre,
            descripcion=dto.descripcion,
            tipo_reporte=tipo_reporte,
            datos_origen=dto.datos_origen,
            metadatos=metadatos,
            configuracion=configuracion
        )
    
    def _crear_desde_evento(self, evento_data: Dict[str, Any]) -> Reporte:
        """Crea un reporte desde datos de evento."""
        
        # Determinar el tipo de evento y extraer datos básicos
        if 'id_contrato' in evento_data or 'contrato_id' in evento_data:
            contrato_id = evento_data.get('id_contrato') or evento_data.get('contrato_id', 'N/A')
            nombre = f"Reporte de Contrato: {contrato_id}"
            descripcion = f"Reporte generado para el contrato {contrato_id}"
            tipo_reporte = TipoReporte.CONTRATO
            origen_evento = "ContratoCreado"
        elif 'campana_id' in evento_data:
            campana_id = evento_data.get('campana_id')
            nombre_campana = evento_data.get('nombre', 'Sin nombre')
            nombre = f"Reporte Campaña: {nombre_campana}"
            descripcion = f"Reporte generado para la campaña: {nombre_campana}"
            tipo_reporte = TipoReporte.CAMPANA
            origen_evento = "CampanaCreada"
        else:
            nombre = "Reporte Genérico"
            descripcion = "Reporte generado desde evento no identificado"
            tipo_reporte = TipoReporte.GENERAL
            origen_evento = "EventoGenerico"
        
        # Crear metadatos y configuración
        metadatos = MetadatosReporte(
            origen_evento=origen_evento,
            version_esquema="1.0",
            datos_adicionales={
                "timestamp_evento": datetime.utcnow().isoformat(),
                **evento_data
            }
        )
        
        configuracion = ConfiguracionReporte(
            incluir_metricas=True,
            formato_salida="json",
            notificar_completado=True
        )
        
        return Reporte(
            nombre=nombre,
            descripcion=descripcion,
            tipo_reporte=tipo_reporte,
            datos_origen=evento_data,
            metadatos=metadatos,
            configuracion=configuracion
        )


@dataclass
class FabricaReportes:
    """Fábrica principal para objetos del dominio de reportes."""
    
    def crear_objeto(self, obj: Any, mapeador: Mapeador = None) -> Any:
        if (isinstance(obj, (CrearReporteDTO, dict)) or 
            (mapeador and mapeador.obtener_tipo() == Reporte.__class__)):
            fabrica_reporte = _FabricaReporte()
            return fabrica_reporte.crear_objeto(obj, mapeador)
        else:
            raise TipoObjetoNoExisteEnDominioReportesExcepcion(f"No se puede crear objeto para el tipo: {type(obj)}")