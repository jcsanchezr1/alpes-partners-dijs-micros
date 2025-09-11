from datetime import datetime
from typing import Dict, Any, Optional

from reportes.seedwork.dominio.eventos import EventoDominio, EventoIntegracion
from .objetos_valor import TipoReporte, EstadoReporte


class ReporteCreado(EventoIntegracion):
    """Evento emitido cuando se crea un nuevo reporte."""
    
    def __init__(self,
                 reporte_id: str,
                 nombre: str,
                 descripcion: str,
                 tipo_reporte: TipoReporte,
                 datos_origen: Dict[str, Any],
                 origen_evento: str):
        super().__init__()
        self.reporte_id = reporte_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_reporte = tipo_reporte
        self.datos_origen = datos_origen
        self.origen_evento = origen_evento
    
    def _datos_evento(self) -> Dict[str, Any]:
        return {
            'reporte_id': self.reporte_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo_reporte': self.tipo_reporte.value,
            'datos_origen': self.datos_origen,
            'origen_evento': self.origen_evento
        }


