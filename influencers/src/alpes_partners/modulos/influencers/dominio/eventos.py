from datetime import datetime
from typing import List, Dict, Any, Optional
from ....seedwork.dominio.eventos import EventoDominio, EventoIntegracion
from .objetos_valor import TipoInfluencer, EstadoInfluencer, Plataforma


class InfluencerRegistrado(EventoIntegracion):
    """Evento emitido cuando se registra un nuevo influencer."""
    
    def __init__(self, 
                 influencer_id: str,
                 nombre: str,
                 email: str,
                 categorias: List[str],
                 plataformas: List[str],
                 fecha_registro: datetime):
        super().__init__()
        self.influencer_id = influencer_id
        self.nombre = nombre
        self.email = email
        self.categorias = categorias
        self.plataformas = plataformas
        self.fecha_registro = fecha_registro