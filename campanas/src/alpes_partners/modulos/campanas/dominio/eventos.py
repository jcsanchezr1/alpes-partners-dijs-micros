from datetime import datetime
from typing import List, Dict, Any
from alpes_partners.seedwork.dominio.eventos import EventoDominio, EventoIntegracion
from .objetos_valor import TipoComision, EstadoCampana


class CampanaCreada(EventoIntegracion):
    """Evento emitido cuando se crea una nueva campana."""
    
    def __init__(self, 
                 campana_id: str,
                 nombre: str,
                 descripcion: str,
                 tipo_comision: TipoComision,
                 valor_comision: float,
                 moneda: str,
                 categorias_objetivo: List[str],
                 fecha_inicio: datetime,
                 fecha_fin: datetime = None):
        super().__init__()
        self.campana_id = campana_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo_comision = tipo_comision
        self.valor_comision = valor_comision
        self.moneda = moneda
        self.categorias_objetivo = categorias_objetivo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
    
    def _datos_evento(self) -> Dict[str, Any]:
        return {
            'campana_id': self.campana_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo_comision': self.tipo_comision.value,
            'valor_comision': self.valor_comision,
            'moneda': self.moneda,
            'categorias_objetivo': self.categorias_objetivo,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None
        }

