from abc import ABC
from datetime import datetime
from typing import Any, Dict
import uuid


class EventoDominio(ABC):
    """Clase base para todos los eventos de dominio."""
    
    def __init__(self) -> None:
        self.id = str(uuid.uuid4())
        self.fecha_creacion = datetime.utcnow()
        self.agregado_id: str = ""
        self.version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización."""
        return {
            'id': self.id,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'agregado_id': self.agregado_id,
            'version': self.version,
            'tipo_evento': self.__class__.__name__,
            **self._datos_evento()
        }
    
    def _datos_evento(self) -> Dict[str, Any]:
        """Datos específicos del evento. Debe ser implementado por subclases."""
        return {}


class EventoIntegracion(EventoDominio):
    """Eventos que cruzan límites de contexto."""
    pass
