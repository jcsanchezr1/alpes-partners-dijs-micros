from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from .comandos import Comando
from .queries import Query, QueryResultado

C = TypeVar('C', bound=Comando)
Q = TypeVar('Q', bound=Query)


class ManejadorComando(ABC, Generic[C]):
    """Interfaz para manejadores de comandos."""
    
    @abstractmethod
    def handle(self, comando: C) -> None:
        """Maneja un comando."""
        pass


class ManejadorQuery(ABC, Generic[Q]):
    """Interfaz para manejadores de queries."""
    
    @abstractmethod
    def handle(self, query: Q) -> QueryResultado:
        """Maneja una query."""
        pass
