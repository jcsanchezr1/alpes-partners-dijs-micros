from datetime import datetime
from typing import Any, Dict
from ....seedwork.dominio.entidades import AgregacionRaiz
from ....seedwork.dominio.objetos_valor import ObjetoValor
import uuid


class SagaLog(AgregacionRaiz):
    """Entidad para registrar el log de la saga."""
    
    def __init__(self, 
                 id_correlacion: str,
                 evento_tipo: str,
                 evento_datos: Dict[str, Any],
                 comando_tipo: str = None,
                 comando_datos: Dict[str, Any] = None,
                 paso_index: int = None,
                 estado: str = "pendiente",
                 fecha_procesamiento: datetime = None):
        super().__init__()
        self.id_correlacion = id_correlacion
        self.evento_tipo = evento_tipo
        self.evento_datos = evento_datos or {}
        self.comando_tipo = comando_tipo
        self.comando_datos = comando_datos or {}
        self.paso_index = paso_index
        self.estado = estado  # pendiente, procesado, error, compensado
        self.fecha_procesamiento = fecha_procesamiento or datetime.utcnow()
