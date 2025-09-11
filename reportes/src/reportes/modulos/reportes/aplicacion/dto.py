from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field

from reportes.seedwork.aplicacion.dto import DTO


class CrearReporteDTO(DTO):
    """DTO para crear un reporte."""
    
    fecha_creacion: str
    fecha_actualizacion: str
    id: str
    nombre: str
    descripcion: str
    tipo_reporte: str
    datos_origen: Dict[str, Any]
    origen_evento: str
    estado: str = "activo"  # Campo para manejo de compensación
    version_esquema: str = "1.0"
    datos_adicionales: Optional[Dict[str, Any]] = None
    incluir_metricas: bool = True
    formato_salida: str = "json"
    notificar_completado: bool = False


class ReporteDTO(DTO):
    """DTO para representar un reporte."""
    
    id: str
    nombre: str
    descripcion: str
    tipo_reporte: str
    estado: str
    datos_origen: Dict[str, Any]
    origen_evento: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
