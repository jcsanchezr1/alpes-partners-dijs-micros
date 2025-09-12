from abc import ABC
from datetime import datetime
from typing import List, Optional
import uuid

from .eventos import EventoDominio


class Entidad(ABC):
    """Clase base para todas las entidades del dominio."""
    
    def __init__(self, id: Optional[str] = None) -> None:
        self.id = id or str(uuid.uuid4())
        self.fecha_creacion = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
        self._eventos: List[EventoDominio] = []
    
    @property
    def eventos(self) -> List[EventoDominio]:
        """Obtiene los eventos de dominio generados por la entidad."""
        return self._eventos.copy()
    
    def agregar_evento(self, evento: EventoDominio) -> None:
        """Agrega un evento de dominio a la entidad."""
        evento.agregado_id = self.id
        self._eventos.append(evento)
    
    def limpiar_eventos(self) -> None:
        """Limpia los eventos después de ser procesados."""
        self._eventos.clear()
    
    def marcar_actualizado(self) -> None:
        """Marca la entidad como actualizada."""
        self.fecha_actualizacion = datetime.utcnow()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entidad):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)


class AgregacionRaiz(Entidad):
    """Clase base para agregados raíz."""
    
    def __init__(self, id: Optional[str] = None) -> None:
        super().__init__(id)
        self.version = 1
    
    def incrementar_version(self) -> None:
        """Incrementa la versión del agregado."""
        self.version += 1
        self.marcar_actualizado()
    
    def validar_regla(self, regla):
        """Método temporal para compatibilidad con el tutorial."""
        # TODO: Implementar validación de reglas completa
        pass
