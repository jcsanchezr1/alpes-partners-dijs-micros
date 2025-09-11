from datetime import datetime
from typing import List, Dict, Any
from ....seedwork.dominio.eventos import EventoDominio, EventoIntegracion
from .objetos_valor import TipoContrato, EstadoContrato, Plataforma


class ContratoCreado(EventoIntegracion):
    """Evento emitido cuando se crea un nuevo contrato."""
    
    def __init__(self, 
                 contrato_id: str,
                 influencer_id: str,
                 campana_id: str,
                 monto_total: float,
                 moneda: str,
                 fecha_inicio: datetime,
                 fecha_fin: datetime,
                 tipo_contrato: str,
                 fecha_creacion: datetime):
        super().__init__()
        self.contrato_id = contrato_id
        self.influencer_id = influencer_id
        self.campana_id = campana_id
        self.monto_total = monto_total
        self.moneda = moneda
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.tipo_contrato = tipo_contrato
        self.fecha_creacion = fecha_creacion